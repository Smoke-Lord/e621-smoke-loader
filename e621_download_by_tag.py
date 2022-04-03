#!/usr/bin/env python3

"""
Downloads posts from e621.net

provide tags and the save directory, and the code will do the rest


"""

from requests.auth import HTTPBasicAuth
import requests
import time
import os
import sys
from urllib.parse import urljoin, urlparse
import time
import sys
import asyncio
import pickle
import _thread
import socket

"""def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])


import_or_install(requests)"""

headers = {"User-Agent": "E621-Mass-Post-Downloader (by smokelord on E621)"}

debug_messages = False


class PullOptions:
    def __init__(
            self,
            search_tags=None,
            target_directory=None,
            api_key_path=None,
            server_port_number=None):
        self.search_tags = search_tags
        self.target_directory = target_directory
        self.api_key_path = api_key_path
        self.server_port_number = server_port_number

    def get_search_tags(self):
        return self.search_tags

    def get_target_directory(self):
        return self.target_directory

    def get_key_path(self):
        return self.api_key_path

    def set_key_path(self, passed_key_path):
        self.api_key_path = passed_key_path

    def get_server_port_number(self):
        return self.server_port_number

    def set_server_port_number(self, passed_server_port_number):
        self.server_port_number = passed_server_port_number

#########################
# setup
#####################


arg_len = len(sys.argv)

if debug_messages:

    print("Total args passed: ", arg_len)


options_object = None

# html file options
tag_arg_position = None

# directory options
directory_arg_position = None
directory_for_output = None
search_tags = None

# api key file
currentFolder = os.path.dirname(os.path.realpath(__file__))
apiKeyFile = os.path.join(currentFolder, "apikey.txt")


####################################
#
# socket client
#
####################################

def socket_send_message(passed_message):

    IP = "localhost"
    #PORT = options_object.get_server_port_number()
    PORT = 8888
    sender_name = "tag downloader"

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((IP, PORT))

    client_socket.setblocking(False)

    if debug_messages:
        print(
            f"socket_send_message port - {options_object.get_server_port_number()}")
    data = {
        'sender': sender_name,
        'message': passed_message,

    }
    flatened_message = pickle.dumps(data)

    if debug_messages:
        print("socket_send_message - message sent")

    client_socket.send(flatened_message)
    # message appears on server when the socket closes
    client_socket.close()


def send_message_to_gui_server(passed_message):
    if debug_messages:
        print("starting thread")

    try:

        _thread.start_new_thread(socket_send_message, (passed_message,))

    except BaseException:
        if debug_messages:
            print(sys.exc_info())


def rateLimiting():
    global lastTime, rateLimit
    timeTaken = time.time() - lastTime
    if timeTaken <= rateLimit:
        time.sleep(rateLimit - timeTaken)
    lastTime = time.time()


# Setup variables:
global rateLimit, lastTime
defaultURL = "https://e621.net/posts.json"
pastURL = ""
currentFolder = os.path.dirname(os.path.realpath(__file__))
# fix file paths with spaces


apiKeyFile = os.path.join(currentFolder, "apikey.txt")

rateLimit = 1
lastTime = time.time()

# Get API key and Username from apikey.txt


def download_posts(passed_posts):
    for post in passed_posts:
        full_post_url = post["file"]["url"]
        if debug_messages:
            print(full_post_url)
        # calling the system wget to download files

        target_file = full_post_url[full_post_url.rindex("/"):]

        status_message = f"Downloading {target_file}"
        # send message if port number is not None
        if options_object.get_server_port_number():
            send_message_to_gui_server(status_message)

        os.system(
            "wget --no-check-certificate -nc {} --directory-prefix=\"{}\"".format(
                full_post_url, str(
                    options_object.get_target_directory())))


def download_process():

    # check if aki key file is present in directory

    # api key file
    currentFolder = os.path.dirname(os.path.realpath(__file__))
    apiKeyFile = os.path.join(currentFolder, "apikey.txt")

    if options_object.get_key_path():
        apiKeyFile = options_object.get_key_path()

        if debug_messages:
            print(f"options_object.get_key_path() : {apiKeyFile}")

    try:
        with open(apiKeyFile) as apiFile:
            apiKeys = apiFile.read().splitlines()

    except FileNotFoundError:
        with open(apiKeyFile, "w") as apiFile:
            apiFile.write("user=" + os.linesep + "api_key=")
            sys.exit()

    apiUser = apiKeys[0].split("=")[1]
    apiKey = apiKeys[2].split("=")[1]

    """
    #prints api key info for testing
    if debug_messages:

        print(apiUser)
        print(apiKey)
    """
    # check to make sure api data was entered
    if apiUser == "" or apiKey == "":
        print(text="Please actually put your username and API key into apikey.txt")

    posts_found_in_page = True
    page_number = 1
    all_posts = []
    rating = ""

    tag = str(options_object.get_search_tags())
    tags = tag.split(" ")
    if debug_messages:
        print(tags)

    while posts_found_in_page:

        grabURL = f"{defaultURL}?tags="
        x = " ".join(tags)
        grabURL += x
        grabURL += f" &page={page_number}&{rating}&limit=320"

        # after first request follow 1 second rate limit rule
        if page_number > 1:

            rateLimiting()

        # request to e621.net
        req = requests.get(
            grabURL,
            headers=headers,
            auth=HTTPBasicAuth(
                apiUser,
                apiKey))
        page_number += 1
        data = req.json()

        # if request passes check
        if req.status_code == 200:

            if data['posts']:
                # add the page of requests to collection to download
                all_posts += data['posts']
                # print the total posts retrieved from the last request
                if debug_messages:
                    print(len(data['posts']))
            else:
                # occures when no posts are found or all the post have been
                # already collected
                if debug_messages:
                    print("no posts found")

                posts_found_in_page = False
        else:
            if debug_messages:
                print("error status code did not return 200")
    # if posts were collected download them
    if len(all_posts) > 0:
        # download everypost
        download_posts(all_posts)


def setup_options_object():

    search_tags = None
    directory_for_output = None
    arg_count = 0
    key_path = None
    server_port_number = None

    command_line_args = sys.argv

    for arg in command_line_args:

        if debug_messages:

            print("arg[{}]: ".format(arg_count), arg)

        # check for html file arg
        if arg == "-t":
            if debug_messages:
                print("file arg passed")

        # mark position of file arg

            tag_arg_position = arg_count

            if arg_len > tag_arg_position + 1:

                search_tags = sys.argv[tag_arg_position + 1]

        if arg == "-d":
            if debug_messages:
                print("directory arg passed")

            directory_arg_position = arg_count

            if arg_len > directory_arg_position + 1:
                directory_for_output = command_line_args[directory_arg_position + 1]

        if arg == "-key":
            if debug_messages:
                print("key path arg passed")

            key_arg_position = arg_count

            if arg_len > key_arg_position + 1:
                key_path = command_line_args[key_arg_position + 1]

        if arg == "-port":
            if debug_messages:
                print("server port number arg passed")

            server_port_arg_position = arg_count
            if arg_len > server_port_arg_position + 1:
                server_port_number = command_line_args[server_port_arg_position + 1]

        arg_count = arg_count + 1

    # if key_path is not None create pull option with key_path
    if key_path:

        if server_port_number:
            return PullOptions(
                search_tags,
                directory_for_output,
                key_path,
                server_port_number)

        return PullOptions(search_tags, directory_for_output, key_path)

    return PullOptions(search_tags, directory_for_output)

#####################################
#
# start of code
#
#####################################


options_object = setup_options_object()


if options_object.get_search_tags():
    if debug_messages:
        print(f"search tags: {options_object.get_search_tags()}")

    if options_object.get_target_directory():
        # do thing
        if debug_messages:
            print(
                f"directory_for_output: {options_object.get_target_directory()}")
        # did not remove the option object creation

        """if debug_messages:
            print(options_object.get_search_tags())
            print(options_object.get_target_directory())"""
        # do process

        download_process()
    else:
        print("please provide a save directory")
        print("ie: code -d \"/special_folder/stuff\"")

else:
    print("please provide e621 search tags")
    print("ie: code -t \"banana \"")
