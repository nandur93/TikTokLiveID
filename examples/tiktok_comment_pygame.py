import asyncio
import io
from asyncio import AbstractEventLoop
from typing import List, Optional

import aiohttp
import pygame
from PIL import Image, ImageDraw, ImageFilter
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent

author_font = str("examples\Futura-Maxi-CGBold-Regular.otf")
background = pygame.image.load('examples\img_comment.png')
favicon_game = pygame.image.load('examples\icon_comment.png')

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
        self.name: pygame.surface = pygame.font.SysFont(author_font, 35, bold=False).render(self.author, True, (255, 0, 80))
        self.comment: pygame.surface = pygame.font.SysFont("Segoe UI Emoji", 35, bold=False).render(self.text, True, (0, 242, 234))
        self.icon: Optional[pygame.image] = None

        try:
            image = self.__mask_circle_transparent(Image.open(io.BytesIO(image)), 2)
            self.icon = pygame.transform.scale(pygame.image.frombuffer(image.tobytes(), image.size, image.mode), (75, 75))
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
        screen.blit(self.name, (x + 100, y + 5)) #jarak profil_pic ke nama
        screen.blit(self.comment, (x + 100, y + self.comment.get_height())) #jarak profil ke komentar
        # screen.blit(self.name, (x + 125, y)) #jarak profil_pic ke nama
        # screen.blit(self.comment, (x + self.name.get_width() + 135, y + self.comment.get_height() / 4)) #jarak profil ke komentar


class DisplayCase:
    """
    DisplayCase class for managing pygame 
    
    """

    def __init__(self, loop: AbstractEventLoop, height: int = 720, width: int = 1280):
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

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("CommentRealLive")
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
                c = Comment(author=comment.user.nickname, text=comment.comment, image=await request.read())
                self.active.insert(0, c)

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
                y: int = int(self.height - (15 + ((idx + 1) * 80)))#jarak antar chat
                if y > 0:
                    comment.blit(self.screen, 20, y)

            # Pop from the queue
            if len(self.queue) > 0:
                self.loop.create_task(self.__pop_queue())

            # Cap active at 50 items
            self.active = self.active[:50]

            pygame.display.update()
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    """
    This module requires the following to run:
    
    - TikTokLive
    - Pillow (PIL)
    - pygame
    
    """


    async def on_comment(comment: CommentEvent):
        """
        Add to the display case queue on comment
        :param comment: Comment event
        :return: None

        """

        display.queue.append(comment)


    loop: AbstractEventLoop = asyncio.get_event_loop()
    client: TikTokLiveClient = TikTokLiveClient("@ewing.3gp", loop=loop)
    client.add_listener("comment", on_comment)
    display: DisplayCase = DisplayCase(loop)
    loop.create_task(client.start())
    loop.run_until_complete(display.start())
