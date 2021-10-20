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
        # folders = dbx.files_list_folder("/Music").entries
        # folder_names= []
        
        # to retrieve folder names from folder metadata
        #for i in range(0, len(folders)):
        #    folder_names.append(folders[i].name)

        # check f3rctak unique name
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

                    # to get the right tag whatever the order is
                    # for tag, value in music_dict.items():
                    #if value == folder_names[i]:
                    #        row.append(tag)
                    row.append('#' + str(i+1))

                    data.append(row)
        data.sort()
        return data

    except Exception as e:
        print(e)
        pass

# retrieve value from config vars in Heroku
dbx_token = os.getenv('dbx_token')
# initiate dropbox api
dbx = dropbox.Dropbox(dbx_token)
