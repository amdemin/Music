# pip install pyTelegramBotAPI, do not install telebot
import telebot
import requests
from pathlib import Path
from telebot import types
from music_process import extract_music_files
from re import search
import dropbox
import random as rand
from PIL import Image
from boto.s3.connection import S3Connection
import os
from telegram_bot_pagination import InlineKeyboardPaginator
import urllib.request as urllib2
import time
import re
import random as rd
import vk_api
from vk_api.audio import VkAudio
import traceback

def convert_photos(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        return downloaded_file
    except Exception:
        pass
    return None

def convert_videos(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        return downloaded_file
    except Exception:
        pass
    return None


# random name for mediafile to make it uniquely identified
def random_name():
    string = ""
    letters = 'abcdefhkmnoprstwxyzABCDEFHKMNOPRSTWXYZ'
    num = 0
    while num < 10:
        a = rand.randint(0, 1)
        if a == 0:
            a = rand.choice(letters)
            string += a
        else:
            a = rand.randint(0, 9)
            string += str(a)
        num += 1
    return string


# retrieve values from Config Vars in Heroku
tg_token = os.getenv('tg_token')
dbx_token = os.getenv('dbx_token')
vk_login = os.getenv('vk_login')
vk_password = os.getenv('vk_password')

vk_session = vk_api.VkApi(vk_login, vk_password)
vk_session.auth()
vk = vk_session.get_api()
vk_audio = VkAudio(vk_session)

# initiate telegram api
bot = telebot.TeleBot(tg_token)
# initiate dropbox api
dbx = dropbox.Dropbox(dbx_token)
#music_dict = {'#1' : 'cream soda', '#2' : 'lxst cxntury', '#3': 'f3rctak', '#4': 'low pulse', '#5': 'vacuum',
# '#6': 'don diablo', '#7': 'vvpskvd', '#8': 'phonk', '#9': 'apple music', '#10': 'monolithic'}
music_dict = {}
folders = dbx.files_list_folder("/Music").entries
# define tags for every folder of the music cloud
for i in range(0, len(folders)):
    music_dict['#' + str(i+1)] = folders[i].name


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.from_user.id, "This bot is created to search for music songs, please, enter the name of artist or song")

    
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, "Enter the name of artist or song correctly, e.g: Сream Soda")

@bot.message_handler(commands=['about'])
def about_command(message):
    try:
        about_keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Github", url="https://github.com/artem404/Music")
        about_keyboard.add(button)
        bot.send_message(message.chat.id, "The bot was made by Artem @artem_tg \nThis project can be found on: ", reply_markup=about_keyboard)
    except Exception as e:
        print(e)
        pass

    
@bot.message_handler(commands=['shot'])
def ask_word(message):
    try:
        bot.send_message(message.chat.id, "Enter a password for your files")
        bot.register_next_step_handler(message, shot_command)
    except Exception as e:
        print(e)
        pass
        
def shot_command(message):
    try:
        word = message.text
        input = message.content_type
        if input == 'text':
            if word == "/screen":
                photo_command(message)
            elif word == "/shot":
                ask_word(message)
            elif word == "/start":
                start_command(message)
            elif word == "/help":
                help_command(message)
            elif word == "/about":
                about_command(message)
            elif word == "/delete":
                delete_command(message)
            else:
                flag = False
                keyboard = types.InlineKeyboardMarkup()
                photos = []

    #         entries = Path('Photos/')
    #         for entry in entries.iterdir():

                for entry in dbx.files_list_folder('/Host').entries:
                    photos.append(entry.name)
                num = 0
                print(photos)
                for name_photo in range(0, len(photos)):
                    separate = photos[name_photo].split(".")  # to extract the password and format
                    format = separate[len(separate) - 1]
                    if format.lower() == "mp4":
                        if word == separate[0].lower():
                            button = types.InlineKeyboardButton(text=separate[1], callback_data="video" + str(num))
                            keyboard.add(button)
                            flag = True
                    elif format.lower() == "jpg":
                        if word == separate[0].lower():
                            button = types.InlineKeyboardButton(text=separate[1], callback_data="photo" + str(num))
                            keyboard.add(button)
                            flag = True
                    num += 1
                if flag:
                    bot.send_message(message.chat.id, "Found: ", reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id, "No results with this password, you may try again /shot")
        elif input == 'photo':
            bot.send_message(message.chat.id, "You sent a photo, not a password, you may try again /shot")
        elif input == 'video':
            bot.send_message(message.chat.id, "You sent a video, not a password, you may try again /shot")
        else:
            bot.send_message(message.chat.id, "You should enter a word, you may try again /shot")
    except Exception as e:
        print(e)
        pass

    
@bot.message_handler(commands=['screen'])
def photo_command(message):
    try:
        bot.send_message(message.from_user.id, "Create a password for your files")
        bot.register_next_step_handler(message, reply_command)
    except Exception as e:
        print(e)
        pass

def reply_command(message):
    try:
        word = message.text
        input = message.content_type
        if input == "text":
            if word == "/screen":
                photo_command(message)
            elif word == "/shot":
                ask_word(message)
            elif word == "/start":
                start_command(message)
            elif word == "/help":
                help_command(message)
            elif word == "/about":
                about_command(message)
            elif word == "/delete":
                delete_command(message)
            else:
                bot.send_message(message.from_user.id, "Sent as media, strictly one by one, otherwise will not work")
                bot.register_next_step_handler(message, process_photo, word)
        else:
            bot.send_message(message.from_user.id, "Firstly, create the password")
            bot.register_next_step_handler(message, reply_command)
    except Exception as e:
        print(e)
        pass

def process_photo(message, word):
    try:
        input = message.content_type
        if input == 'text':
            if message.text == "/screen":
                photo_command(message)
            elif message.text == "/shot":
                ask_word(message)
            elif message.text == "/start":
                start_command(message)
            elif message.text == "/help":
                help_command(message)
            elif message.text == "/about":
                about_command(message)
            elif message.text == "/delete":
                delete_command(message)
            else:
                bot.send_message(message.from_user.id, "You sent words, you may try again /screen")
        elif input == 'document':
            bot.send_message(message.from_user.id, "You send photo as file")
            bot.send_message(message.from_user.id, "Please, send as photo")
            bot.register_next_step_handler(message, process_photo, word)
        elif input == 'photo':
            bot.send_message(message.from_user.id, "Please, wait ...")
            content = convert_photos(message)
            rand_name = random_name()
            file_name = word + "." + rand_name
            dbx.files_upload(content, "/Host/" + file_name + ".jpg")
            bot.send_message(message.from_user.id, "Photo has been uploaded")
            bot.register_next_step_handler(message, process_photo, word)
        elif input == 'video':
            bot.send_message(message.from_user.id, "Please, wait ...")
            content = convert_videos(message)
            rand_name = random_name()
            file_name = word + "." + rand_name
            dbx.files_upload(content, "/Host/" + file_name + ".mp4")
            bot.send_message(message.from_user.id, "Video has been uploaded")
            bot.register_next_step_handler(message, process_photo, word)
        else:
            bot.send_message(message.from_user.id, "Please, enter the command again to upload files /screen")
    except Exception as e:
        print(e)

        
@bot.message_handler(commands=['delete'])
def delete_command(message):
    try:
        bot.send_message(message.from_user.id, "Enter a password for your files, they will be deleted from a database")
        bot.register_next_step_handler(message, delete_process)
    except Exception as e:
        print(e) 

def delete_process(message):
    try:
        word = message.text
        if word == "/screen":
                photo_command(message)
        elif word == "/shot":
            ask_word(message)
        elif word == "/start":
            start_command(message)
        elif word == "/help":
            help_command(message)
        elif word == "/about":
            about_command(message)
        elif word == "/delete":
            delete_command(message)
        else:
            num = 0
            for entry in dbx.files_list_folder('/Host').entries:  
                separate = entry.name.split('.')
                if word == separate[0]:
                    dbx.files_delete("/Host/" + entry.name)
                    num += 1
            if 0 < num < 2:
                bot.send_message(message.from_user.id, str(num) + " file '" + word + "' was successfully deleted")
            elif num > 1:
                bot.send_message(message.from_user.id, str(num) + " files '" + word + "' were successfully deleted")
            else:
                bot.send_message(message.from_user.id, "No results with this password, you may try again /delete")
    except Exception as e:
        print(e)

@bot.message_handler(content_types=['text', 'audio'])
def process_input(message, page=1, text=""):
    text = message.text
    try:

        # this code is used to identify repeated requests from one input
        text = text.split("• ")
        if len(text) > 1:
            text = text[1]
        else:
            text = text[0]

        keyboard = types.InlineKeyboardMarkup()

        # retrieve songs from the private dropbox cloud
        if 'dropbox' in text:
            result = extract_music_files(text, music_dict)
            # split list into small sublists limited by 10
            result_split_page = [result[x:x+10] for x in range(0, len(result), 10)]
            # add button to telegram according to page numeration
            page_file = page-1
        # retrieve songs from public vk
        else:
            result = []
            page_file = 0
            number_of_songs = len(list(vk_audio.search(text, count=15, offset=0)))
            time.sleep(rd.uniform(0.5,1.1))
            tracks = list(vk_audio.search(text, count=5, offset=5*(page-1)))
            for song in range(0, len(tracks)):
                row = []
                row.append(tracks[song]['artist'] + ' ' + tracks[song]['title'])
                row.append(tracks[song]['owner_id'])
                row.append(tracks[song]['id'])
                result.append(row)

        print(result)

        result_split_page = [result[x:x+5] for x in range(0, number_of_songs, 5)]
        audio_format = ".mp3"
        if len(result_split_page) != 0:  
            for i in range(0, len(result_split_page[page_file])):
                if ".mp3" in result_split_page[page_file][i][0]:
                    result_split_page[page_file][i][0] = result_split_page[page_file][i][0].replace(".mp3", "")
                    # audio_format = ".mp3"
                # callback_data API is limited to 64 bytes (64 letters long)
                button = types.InlineKeyboardButton(text=result_split_page[page_file][i][0], 
                            callback_data="audio_row;" + str(i)  + ";" + audio_format + ";" + str(result_split_page[page_file][i][1]) + ";" + str(result_split_page[page_file][i][2]))
                keyboard.add(button)

            # initiate paginator
            paginator = InlineKeyboardPaginator(int(len(result_split_page)), current_page=page, data_pattern='page;{page};' + str(text))

            bot.send_message(message.chat.id, "Found songs: ", reply_markup=keyboard)
            if len(result_split_page) > 1:
                # send number of pages when at least more than one
                bot.send_message(message.chat.id, "Page: " + str(page) + " • " + str(text), reply_markup=paginator.markup, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "No results")
    except Exception as e:
        print('Error in process_input:', e)
        print(traceback.format_exc())
        # bot.send_message(message.from_user.id, e)
        bot.send_message(message.chat.id, "Error occured, no results")

# this callback handler is only for paginator requests
@bot.callback_query_handler(func=lambda call: call.data.split(';')[0]=='page')
def page_callback(call):
    try:
        page = int(call.data.split(';')[1])
        text = call.data.split(';')[2]
        msg_code = call.message.message_id
        bot.delete_message(call.message.chat.id, msg_code-1)
        bot.delete_message(call.message.chat.id, msg_code)
        process_input(call.message, page, text)
    except Exception as e:
        print('Error in page_callback:', e)
        print(traceback.format_exc())


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0]=='audio_row')
def audio_row_callback(call):
    try:
        audio_split = call.data.split(';')
        row_number = int(audio_split[1])
        song_name = call.message.json["reply_markup"]["inline_keyboard"][row_number][0]["text"]
        if ".mp3" in audio_split[2]:
            song_name = song_name + ".mp3"

        # download the chosen song from the private dropbox cloud
        if '#' in audio_split[3]:
            tag = audio_split[3]
            folder = music_dict[tag]
            metadata, res = dbx.files_download(path="/Music/" + folder + "/" + song_name)
            bot.send_audio(call.from_user.id, res.content, title=song_name.replace(".mp3", ""))
        # download the chosen song from the public vk
        else:
            track = vk_audio.get_audio_by_id(int(audio_split[3]), int(audio_split[4]))
            res = requests.get(track['url'])
            bot.send_audio(call.from_user.id, res.content, title=track['artist'] + ' - ' + track['title'])

    except Exception as e:
        print('Error in audio_row_callback:', e)
        print(traceback.format_exc())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        msg = call.data
        
        if search("photo", msg):
            number = int(msg.replace("photo", ""))
            photos = []
            for entry in dbx.files_list_folder('/Host').entries:
                photos.append(entry.name)

            metadata, res = dbx.files_download(path="/Host/" + photos[number])
            # if problem occurs with sending photo, write from PIL import Image
            bot.send_photo(call.from_user.id, res.content)
            file_id = "snapshot" + str(number)
            bot.send_photo(call.from_user.id, file_id)

        elif search("video", msg):
            number = int(msg.replace("video", ""))
            files = []
            for file in dbx.files_list_folder('/Host').entries:
                files.append(file.name)
            metadata, res = dbx.files_download(path="/Host/" + files[number])
            bot.send_video(call.from_user.id, res.content)
            file_id = "video" + str(number)
            bot.send_photo(call.from_user.id, file_id)
        else:
            pass

bot.polling(none_stop=True, interval=1)
