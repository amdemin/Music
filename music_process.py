from pathlib import Path
from re import search
# from config import dbx_token
import dropbox
from boto.s3.connection import S3Connection
import os


def check_text(text):
    try:
        words = text.split(' ')
        for i in range(0, len(words)):
            if words[i] == "ferctak" or words[i] == "фэрстак":
                words[i] = "f3rctak"
        text = " ".join(words)
        return text
    except Exception as e:
        print(e)
        pass


def extract_music_files(text, music_dict):
    try:

        text = check_text(text)

        data = []
        # to search songs by input
        for i in range(0, len(music_dict)):
            # dropbox search function (path, request)
            result = dbx.files_search("/Music/" + music_dict['#' + str(i+1)], text)
            # song metadata
            result = result.matches
            if result != []:
                for k in range(0, len(result)):
                    row = []
                    # retrieve song name from metadata
                    row.append(result[k].metadata.name)
                    row.append('#' + str(i+1))
                    row.append('')
                    data.append(row)
        data.sort()
        return data

    except Exception as e:
        print(e)
        pass


dbx_token = os.getenv('dbx_token')
# initiate dropbox api
dbx = dropbox.Dropbox(dbx_token)
