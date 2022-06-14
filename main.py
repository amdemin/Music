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
import traceback


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

# initiate telegram api
bot = telebot.TeleBot(tg_token)
# initiate dropbox api
dbx = dropbox.Dropbox(dbx_token)

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
def help_command(message):
    bot.send_message(message.from_user.id, "The bot is created by Kamilla, Karina and Maria, enjoy))")


@bot.message_handler(content_types=['text', 'audio'])
def process_input(message, page=1, text=""):
    text = message.text
    try:

        text = text.split("^ ")
        if len(text) > 1:
            text = text[1]
        else:
            text = text[0]

        
        keyboard = types.InlineKeyboardMarkup()

        result = extract_music_files(text, music_dict)
        # split list into small sublists limited by 10
        result_split_page = [result[x:x+10] for x in range(0, len(result), 10)]
        # add button to telegram according to page numeration
        page_file = page-1

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
        print(e)
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

    except Exception as e:
        print('Error in audio_row_callback:', e)
        print(traceback.format_exc())


bot.polling(none_stop=True, interval=1)
