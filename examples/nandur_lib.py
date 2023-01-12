import requests
import os
import pyglet
from gtts import gTTS
from configparser import ConfigParser

def show_event_picture(pic_url: str, event_name: str):
    """
    Download the TikTok event picture then save it as temporary file like profile picture and gift icon.
    :param ``pic_url``: url from the ``TikTok Event``
    :param ``event_name``: is a picture file name from the event e.g. ``GIFT``, ``LIKE``, ``JOIN``, ``GIFT_NAME``.
    """
    prf = '_profile_picture.png'
    GIFT = 'gift'+str(prf)
    LIKE = 'like'+str(prf)
    JOIN = 'join'+str(prf)
    GIFT_NAME = 'gift_icon'+str('.png')

    if event_name == 'GIFT':
        event_name = GIFT
    elif event_name == 'LIKE':
        event_name = LIKE
    elif event_name == 'JOIN':
        event_name = JOIN
    elif event_name == 'GIFT_NAME':
        event_name = GIFT_NAME
    else: 
        event_name
    with open(event_name, 'wb') as handle:
        response = requests.get(pic_url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
    
def save_tiktok_event_to_text_file(text_file_name: str, text_containts: str):
    """
    Save TikTok username to the ``*.txt`` file
    :param ``text_file_name``: is the desired file name without extension
    :param ``text_containts``: is the contain of the text
    """
    with open(text_file_name+str('.txt'), "w", encoding="utf-8") as file:
        file.write(text_containts)



def read_username(filename: str, lang='id', tld='co.id'):
    """
    Read the TikTok username
    :param ``filename``: is the file name that stored to the disk
    :param ``lang``: is the language of the google voice
    :param ``tld``: is the top level domain of the domain
    """
    filename_ = str(filename)+'.mp3'
    tts = gTTS(filename, lang=lang, tld=tld)
    tts.save(filename_)

    music = pyglet.media.load(filename_, streaming=False)
    music.play()

    # sleep(music.duration) #prevent from killing
    os.remove(filename_) #remove temperory file

def play_mp3_file(filename: str):
    filename_ = str(filename)+'.mp3'
    file_mp3 = pyglet.media.load(filename_, streaming=False)
    file_mp3.play()

def tiktok_id_target():
    """
    Target username from the config file.
    Use string variable ``ret = tiktok_id_target()`` to get return value.
        ret = tiktok_id_target()
    """
    # Cek apakah ada file config
    config = ConfigParser(strict=True)
    print('Checking for config file...')
    config_file_name = 'config.ini'
    config_section_name = 'TikTok_data'
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
        if not config.has_section(config_section_name):

            # Jika tidak ada maka buatkan section
            print('Add section in '+str(config_file_name)+' file')
            config.add_section(config_section_name)

        # Tulis key_id pada Section TikTok_data
        ret = tiktok_id_default
        print('Setup '+str(config_file_name))
        config.set(config_section_name, 'key_id', 'value_id')

        # Simpan sebagai file config.ini
        print('Saving '+str(config_file_name))
        with open(config_file_name, 'w') as f:
            config.write(f)
            print('File '+str(config_file_name)+' saved')
        print('Connected to: '+str(ret))
        return ret
    else:
        print('File '+str(config_file_name)+' is exist')
        conf_tiktok_id = config.get(config_section_name, 'key_id')
        ret = conf_tiktok_id
        print('Connected to: '+str(ret))
        return ret