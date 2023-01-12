import asyncio
import io
import aiohttp
import pygame
import pyautogui

from asyncio import AbstractEventLoop
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFilter
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent
        
# python 2.x
# from ConfigParser import SafeConfigParser
# config = SafeConfigParser()

# python 3.x
from configparser import ConfigParser

author_font = str("Segoe UI Emoji") #font
print('Font: '+str(author_font))
background = pygame.image.load('examples\Img\Bg\img_comment.png') #background
favicon_game = pygame.image.load('examples\Img\Icons\icon_comment.png') #favicon
profile_pic_size = 50
space_between_comment = 60 #20, 40, 60, 80
comment_count = 5
class Comment:
    """
    Comment object for displaying to screen
    
    """

    def __init__(self, author: str, text: str, image: bytes):
        """
        Initialize comment object
        
        :param author: Author name
        :param text: Comment text
        :param image: Comment image (as bytes)
        
        """
        self.author: str = author
        self.text: str = text
        self.name: pygame.surface = pygame.font.SysFont(author_font, 15, bold=False).render(self.author, True, (255, 0, 80))
        self.comment: pygame.surface = pygame.font.SysFont(author_font, 15, bold=False).render(self.text, True, (0, 242, 234))
        self.icon: Optional[pygame.image] = None

        try:
            image = self.__mask_circle_transparent(Image.open(io.BytesIO(image)), 2)
            self.icon = pygame.transform.scale(pygame.image.frombuffer(image.tobytes(), image.size, image.mode), (profile_pic_size, profile_pic_size))
        except:
            pass

    @staticmethod
    def __mask_circle_transparent(original: Image, blur_radius: int, offset: int = 0) -> Image:
        """
        Crop a profile picture into a circle
        
        :param original: Original profile picture
        :param blur_radius: Blur radius
        :param offset: Offset
        :return: New image
        
        """

        offset += blur_radius * 1
        mask = Image.new("L", original.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, original.size[0] - offset, original.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = original.copy()
        result.putalpha(mask)

        return result

    def blit(self, screen: pygame.display, x: int, y: int) -> None:
        """
        Blit a comment to a surface
        
        :param screen: Screen to blit on
        :param x: X-position
        :param y: Y-Position

        """

        # If exists
        if self.icon:
            screen.blit(self.icon, (x + 0, y - 5))
        screen.blit(self.name, (x + (profile_pic_size + 5), y + 5)) #jarak profil_pic ke nama
        screen.blit(self.comment, (x + (profile_pic_size + 5), y + self.comment.get_height() + 5)) #jarak profil ke komentar
        # screen.blit(self.name, (x + 125, y)) #jarak profil_pic ke nama
        # screen.blit(self.comment, (x + self.name.get_width() + 135, y + self.comment.get_height() / 4)) #jarak profil ke komentar


class DisplayCase:
    """
    DisplayCase class for managing pygame 
    
    """

    def __init__(self, loop: AbstractEventLoop, height: int = 400, width: int = 400):
    #def __init__(self, loop: AbstractEventLoop, height: int = 480, width: int = 720):
        """
        Initialize a display case
        
        :param loop: asyncio event loop
        :param height: Screen height
        :param width: Screen width
        
        """

        self.height: int = height
        self.width: int = width

        self.loop: AbstractEventLoop = loop
        self.screen: pygame.display = pygame.display.set_mode((width, height))
        self._running: bool = True
        self.screen: pygame.display = pygame.display.set_mode((self.width, self.height))
        self.queue: List[CommentEvent] = list()
        self.active: List[Comment] = list()

    async def start(self):
        """
        Start the loop
        :return: None
        
        """

        #pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.display.set_caption("CommentRealLive - "+str(tiktok_id))
        pygame.display.set_icon(favicon_game)

        self._running = True
        await self.__screen_loop()

    def stop(self):
        """
        Stop the loop
        :return: None
        
        """

        self._running = False
        pygame.quit()

    async def __pop_queue(self):
        """
        Pop an item from the queue
        :return: None
        
        """

        comment = self.queue.pop(0)

        async with aiohttp.ClientSession() as session:
            async with session.get(comment.user.profilePicture.avatar_url) as request:
                c = Comment(author=comment.user.nickname+str(" (@"+comment.user.uniqueId+")"), text=comment.comment, image=await request.read())
                self.active.insert(0, c)
                
                file = 'examples\DonationSounds\sounds\_260614__kwahmah-02__pop.wav'
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()

    async def __screen_loop(self):
        """
        Main loop for screen
        :return: None

        """

        while self._running:
            # Clear screen
            self.screen.fill((0, 0, 0))
            self.screen.blit(background,(0, 0))

            # Get events
            events: List[pygame.event] = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.stop()
                    return

            # Enumerate through & display data
            for idx, comment in enumerate(self.active):
                y: int = int(self.height - (15 + ((idx + 1) * space_between_comment)))#jarak antar chat
                if y > 0:
                    comment.blit(self.screen, 20, y)

            # Pop from the queue
            if len(self.queue) > 0:
                self.loop.create_task(self.__pop_queue())

            # Cap active at 50 items
            self.active = self.active[:comment_count]

            pygame.display.update()
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    """
    This module requires the following to run:
    
    - TikTokLive
    - Pillow (PIL)
    - pygame
    
    """
    # Cek apakah ada file config
    config = ConfigParser(strict=True)
    print('Checking for config file...')
    config_file_name = 'config.ini'
    config_sec_tiktok_data = 'TikTok_data'
    config_sec_pygame_data = 'pygame_data'
    tiktok_id_default = '@vectorinaja'
    configs = [config_file_name]
    dataset = config.read(configs)

    # Jika tidak ada file config
    if len(dataset) != len(configs):
        print("Any file config(s) doesn't exist")

        # Buat file config.ini
        print('Creating file '+str(config_file_name)+'...')
        config.read(config_file_name)

        # Cek apakah ada section TikTok_data
        print('Checking for any section in '+str(config_file_name))
        if not config.has_section(config_sec_tiktok_data):

            # Jika tidak ada maka buatkan section
            print('Add section '+str(config_sec_pygame_data)+' in '+str(config_file_name)+' file')
            config.add_section(config_sec_tiktok_data)
        
        if not config.has_section(config_sec_pygame_data):

            # Jika tidak ada maka buatkan section
            print('Add section '+str(config_sec_pygame_data)+' in '+str(config_file_name)+' file')
            config.add_section(config_sec_pygame_data)

        # Tulis key_id pada Section TikTok_data
        print('Waiting user input for TikTok ID...')
        tiktok_id = pyautogui.prompt(text='Input TikTok ID pakai simbol @', title='TikTok LIVE ID', default=tiktok_id_default)
        print('Setup '+str(config_file_name))
        config.set(config_sec_tiktok_data, 'key_id', 'value_id')
        config.set(config_sec_pygame_data, 'py_window_size', 'value_id')

        # Simpan sebagai file config.ini
        print('Saving '+str(config_file_name))
        with open(config_file_name, 'w') as f:
            config.write(f)
            print('File '+str(config_file_name)+' saved')
    else:
        print('File '+str(config_file_name)+' is exist')
        print('Getting data from config...')
        conf_tiktok_id = config.get(config_sec_tiktok_data, 'key_id')
        print('Data loaded to the GUI.')
        print('Waiting user confirmation...')
        tiktok_id = pyautogui.prompt(text='Input TikTok ID pakai simbol @', title='TikTok LIVE ID', default=conf_tiktok_id)
        
    async def on_comment(comment: CommentEvent):
        """
        Add to the display case queue on comment
        :param comment: Comment event
        :return: None

        """

        display.queue.append(comment)

    # 👇 Check if my_var is not Null
    if tiktok_id is not None: # 👉️ Check if my_var is not None (null)
        print('Loading TikTok ID: ' + str(tiktok_id))

        config = ConfigParser(strict=True)

        config.read(config_sec_tiktok_data)
        if not config.has_section(config_sec_tiktok_data):
            config.add_section(config_sec_tiktok_data)
        config.set(config_sec_tiktok_data, 'key_id', tiktok_id)

        with open(config_file_name, 'w') as f:
            config.write(f)
        loop: AbstractEventLoop = asyncio.get_event_loop()
        client: TikTokLiveClient = TikTokLiveClient(tiktok_id, loop=loop)
        client.add_listener("comment", on_comment)
        display: DisplayCase = DisplayCase(loop)
        loop.create_task(client.start())
        loop.run_until_complete(display.start())
    else:
        text_cancel = 'ID Kosong, aplikasi akan di tutup'
        print(text_cancel)
        pyautogui.alert(text=text_cancel, title='Warning', button='OK')