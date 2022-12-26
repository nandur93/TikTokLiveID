from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, GiftEvent, LikeEvent, ConnectEvent
from PIL import ImageTk
from urllib.request import urlopen
from tkinter import *
from tkinter import ttk

# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="@skintific_id")

# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    text_connected = (f"Connected to Room ID:", client.room_id)
    print(text_connected)

# Notice no decorator?
async def on_like(event: LikeEvent):
    root = Tk()
    root.title("TikTokLike")
    user_name = f"{event.user.nickname}".encode("utf-8")
    #komentar = f"{event.comment}".encode("utf-8")
    print(f"{event.user.profilePicture.urls[1]}".encode("utf-8"))
    imgUrl = f"{event.user.profilePicture.urls[1]}"
    image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a0/Bill_Gates_2018.jpg"
    data = urlopen(imgUrl)
    # Read the Image
    image = ImageTk.PhotoImage(data=data.read())
    # Resize the image using resize() method
    user_img = ttk.Label(root, image=image)
    user_img.pack()
    #fuser_name = ttk.Label(root, text=user_name)
    #fuser_name.pack()
    #the_comment = ttk.Label(root, text=komentar)
    #the_comment.pack()

    # set the dimensions of the screen 
    # and where it is placed
    #root.geometry('%dx%d+%d+%d' % (w, h, 0, 0))
    #Automatically close the window after 3 seconds
    
    root.after(5000,lambda:root.destroy())
    root.mainloop()

async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname} berkomentar {event.comment}".encode("utf-8"))

@client.on("gift")
async def on_gift(event: GiftEvent):
    # If it's type 1 and the streak is over
    if event.gift.gift_type == 1:
        if event.gift.repeat_end == 1:
            print(f"{event.user.uniqueId} mengirim {event.gift.repeat_count}x \"{event.gift.extended_gift.name}\"")

    # It's not type 1, which means it can't have a streak & is automatically over
    elif event.gift.gift_type != 1:
        print(f"{event.user.uniqueId} mengirim \"{event.gift.extended_gift.name}\"")

# Define handling an event via "callback"
client.add_listener("comment", on_comment)
client.add_listener("like", on_like)
client.add_listener("gift", on_gift)


if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run()
