import asyncio
import time
from doctest import Example
from enum import unique
import io
from asyncio import AbstractEventLoop
from typing import List, Optional

import aiohttp
import pygame
from PIL import Image, ImageDraw, ImageFilter
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import JoinEvent
from nandur_lib import *

author_font = str("Segoe UI Emoji") #font
favicon_game = pygame.image.load('examples\Img\Icons\icon_join.png')

class Join:
    """
    Comment object for displaying to screen
    
    """

    def __init__(self, author: str, uniqueid: str, image: bytes):
        """
        Initialize comment object
        
        :param author: Author name
        :param uniqueid: Author nickname
        :param image: Comment image (as bytes)
        
        """
        self.icon: Optional[pygame.image] = None
        self.author: str = author
        self.uid: str = uniqueid
        self.uniqueid: pygame.surface = pygame.font.SysFont(author_font, 20, bold=False).render(self.uid, True, (255, 0, 80))
        self.name: pygame.surface = pygame.font.SysFont(author_font, 20, bold=False).render(self.author, True, (255, 0, 80))

        try:
            image = self.__mask_circle_transparent(Image.open(io.BytesIO(image)), 2)
            self.icon = pygame.transform.scale(pygame.image.frombuffer(image.tobytes(), image.size, image.mode), (200, 200))
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

        offset += blur_radius * 0
        mask = Image.new("L", original.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((offset, offset, original.size[0] - offset, original.size[1] - offset), fill=255)
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
            screen.blit(self.icon, (x, y-1))
            screen.blit(self.name, (x+5, y + self.icon.get_height()-45)) #jarak profil ke komentar
            screen.blit(self.uniqueid, (x+5, y + self.icon.get_height()-25))
        # screen.blit(self.name, (x + 125, y)) #jarak profil_pic ke nama
        # screen.blit(self.comment, (x + self.name.get_width() + 135, y + self.comment.get_height() / 4)) #jarak profil ke komentar


class DisplayCase:
    """
    DisplayCase class for managing pygame 
    
    """

    def __init__(self, loop: AbstractEventLoop, height: int = 200, width: int = 200):
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
        self.queue: List[JoinEvent] = list()
        self.active: List[Join] = list()

    async def start(self):
        """
        Start the loop
        :return: None
        
        """

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("JoinTokLive")
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

        join = self.queue.pop(0)

        async with aiohttp.ClientSession() as session:
            async with session.get(join.user.profilePicture.avatar_url) as request:
                print(join.user.profilePicture.avatar_url)
                print(join.user.nickname)
                show_event_picture(join.user.profilePicture.avatar_url, 'JOIN')
                c = Join(author=join.user.nickname, uniqueid='@'+join.user.uniqueId, image=await request.read())
                self.active.insert(0, c)

    async def __screen_loop(self):
        """
        Main loop for screen
        :return: None

        """

        while self._running:
            # Clear screen
            self.screen.fill((0, 0, 0))

            # Get events
            events: List[pygame.event] = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.stop()
                    return

            # Enumerate through & display data
            for idx, join in enumerate(self.active):
                y: int = int(self.height - (idx + 1) * 199)#jarak antar chat
                if y > 0:
                    join.blit(self.screen, 0, y) #jarak picture ke border kiri

            # Pop from the queue
            if len(self.queue) > 0:
                self.loop.create_task(self.__pop_queue())

            # Cap active at 50 items
            self.active = self.active[:1]

            pygame.display.update()
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    """
    This module requires the following to run:
    
    - TikTokLive
    - Pillow (PIL)
    - pygame
    
    """
    tiktok_id = tiktok_id_target()
    print('tar: '+str(tiktok_id))
    async def on_join(join: JoinEvent):
        """
        Add to the display case queue on comment
        :param comment: Comment event
        :return: None

        """

        display.queue.append(join)
        # play_mp3_file('Notification')
        # read_username(join.user.nickname, 'id', 'co.id', False)
        # show_profile_picture(join.user.profilePicture.avatar_url, 'join_profile.jpeg')

    loop: AbstractEventLoop = asyncio.get_event_loop()
    client: TikTokLiveClient = TikTokLiveClient(tiktok_id, loop=loop)
    client.add_listener("join", on_join)
    display: DisplayCase = DisplayCase(loop)
    loop.create_task(client.start())
    loop.run_until_complete(display.start())
