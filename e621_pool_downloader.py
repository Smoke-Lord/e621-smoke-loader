#!/usr/bin/env python3

"""
A tool to download e621 pools

provide the pool id and the directory to save it to, and the code will do the rest

example:

    python3 pool_test_1.py -p "0000" -d ./Downloads
"""

from requests.auth import HTTPBasicAuth
import time
import os
import sys
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


headers = {"User-Agent": "E621-Pool-Downloader (by smokelord on E621)"}


debug_messages = False

# object to store pool args for download


class PullOptions:

    def __init__(
            self,
            pool_id=None,
            target_directory=None,
            api_key_path=None,
            server_port_number=None):
        self.pool_id = pool_id
        self.target_directory = target_directory
        self.pool_name = None
        self.api_key_path = api_key_path
        self.server_port_number = server_port_number

    def get_search_pool_id(self):
        return self.pool_id

    def get_target_directory(self):
        return self.target_directory

    def set_pool_name(self, passed_pool_name):
        self.pool_name = passed_pool_name

    def get_pool_name(self):
        return self.pool_name

    def get_key_path(self):
        return self.api_key_path

    def set_key_path(self, passed_key_path):
        self.api_key_path = passed_key_path

    def get_server_port_number(self):
        return self.server_port_number

    def set_server_port_number(self, passed_server_port_number):
        self.server_port_number = passed_server_port_number


# Setup variables:
global rateLimit, absoluteLimit, lastTime
defaultURL = "https://e621.net/pools.json"
#
# need directory calling this script

currentFolder = os.path.dirname(os.path.realpath(__file__))

# default key location
apiKeyFile = os.path.join(currentFolder, "apikey.txt")

absoluteLimit = 320
rateLimit = 1
lastTime = time.time()

arg_len = len(sys.argv)

target_directory = None

# pool arg options
pool_id_arg_position = None

# directory options
directory_arg_position = None

target_directory = None

# options object
options_object = None

# key path option
key_arg_position = None
key_path = None


####################################
#
# socket client
#
####################################

def socket_send_message(passed_message):

    IP = "localhost"
    PORT = options_object.get_server_port_number()
    #PORT = 8888
    sender_name = "pool downloader"

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


def get_post_urls(passed_pool_post_urls):

    pool_post_url_list = []

    for post in passed_pool_post_urls:
        # pause before doing another request
        rateLimiting()
        # request each post
        req = requests.get(
            post,
            headers=headers,
            auth=HTTPBasicAuth(
                apiUser,
                apiKey))
        response = req.json()

        """
            # check response
            if debug_messages:
                print(response)
            """

        # get image urls from response
        pool_post_url_list.append(response['post']['file']['url'])

    return pool_post_url_list


def download_pool_posts(pool_post_file_addresses):
    # a variable to name pool items in order
    pool_order_count = 1

    for post_url in pool_post_file_addresses:

        if debug_messages:

            print(
                f"{options_object.get_pool_name()}_page_{pool_order_count} : {post_url}")

        if post_url:

            # parse the file extension from the link
            file_extension = post_url[(post_url).rindex('.'):]

            selected_file_name = f"{options_object.get_pool_name()}_page_{pool_order_count}{file_extension}"
            if debug_messages:

                print(
                    f"the file found has the extension: \"{file_extension}\"")

            # download file after checks
            if options_object.get_target_directory():

                if options_object.get_search_pool_id():
                    if options_object.get_pool_name():
                        # download the file using the systems wget

                        # check if pool item alread exists
                        file_to_check = f"{options_object.get_target_directory()}/{options_object.get_pool_name()}/{selected_file_name}"
                        file_to_download_exist_in_directory = os.path.isfile(
                            file_to_check)

                        # if file_to_download_exist_in_directory is false. download the file
                         
                        wget_download_filename = post_url[(
                            post_url).rindex('/'):]

                        # send message to gui
                        status_message = f"Downloading {wget_download_filename}"

                        send_message_to_gui_server(status_message)

                        if not file_to_download_exist_in_directory:

                            os.system(
                                f"wget --no-check-certificate -nc {post_url} -P \"{options_object.get_target_directory()}/{options_object.get_pool_name()}\"")

                            # rename_output_file
                            os.rename(
                                f"{options_object.get_target_directory()}/{options_object.get_pool_name()}/{wget_download_filename}",
                                f"{options_object.get_target_directory()}/{options_object.get_pool_name()}/{selected_file_name}")

                        elif file_to_download_exist_in_directory:
                            if debug_messages:
                                print(
                                    f"skipping {wget_download_filename} file: {file_to_check} exists in directory")

        pool_order_count += 1


def clean_pool_name(passed_pool_name):
    # remove characters from pool name that is rejected on windows

    symbol_list = [
        '#',
        '%',
        '&',
        '{',
        '}',
        '\\',
        '<',
        '>',
        '*',
        '?',
        '/',
        ' ',
        '$',
        '!',
        '\'',
        '\"',
        ':',
        '@',
        '+',
        '|',
        '=']
    cleaned_pool_name = passed_pool_name
    for character in passed_pool_name:

        if character in ['%', '!', '?', '\'', '\"', '', ]:
            if character in passed_pool_name:
                # erase bad character if found
                cleaned_pool_name = cleaned_pool_name.replace(character, '')

        elif character in ['#', '&', '{', '}', '\\', '<', '>', '*', '/', '$', ':', '@', '+', '|', '=']:
            if character in passed_pool_name:
                # erase bad character if found
                cleaned_pool_name = cleaned_pool_name.replace(character, '_')

    return cleaned_pool_name


def start_pool_search():
    # in update
    # check if an integer was provided

    if debug_messages:
        print(options_object.get_search_pool_id())

    pool = str(options_object.get_search_pool_id())

    page_num = 1

    get_pool = f"{defaultURL}?search[id]={pool}"

    # get the pool data
    req = requests.get(
        get_pool,
        headers=headers,
        auth=HTTPBasicAuth(
            apiUser,
            apiKey))
    page_num += 1
    pool_search_response_data = req.json()

    """
    if debug_messages:
        #prints pool response
        print(pool_search_response_data)

    """

    # get pool name, and make sure the pool name does not have problem
    # characters for the output file
    pool_name = clean_pool_name(pool_search_response_data[0]['name'])

    # set the cleaned pool name in options object
    options_object.set_pool_name(pool_name)

    # prints all post ids in pool

    """
    if debug_messages:
        print(pool_search_response_data[0]['post_ids'])

    """

    # post_post_url = "https://e621.net/posts/<Post_ID>.json"
    pool_post_urls = []

    # get post info for each post id in pool

    for post_id in pool_search_response_data[0]['post_ids']:
        # works
        pool_post_urls.append(f"https://e621.net/posts/{post_id}.json")

        """
        if debug_messages:
            #prints the post id iterated from the request
            print(post_id)
        """

    pool_post_file_addresses = []

    if pool_post_urls:

        pool_post_file_addresses = get_post_urls(pool_post_urls)

    if pool_post_file_addresses:

        download_pool_posts(pool_post_file_addresses)


def setup_options_object():

    target_pool_id = None
    directory_for_output = None
    arg_count = 0
    key_path = None
    server_port_number = None

    command_line_args = sys.argv

    for arg in command_line_args:

        if debug_messages:

            print("arg[{}]: ".format(arg_count), arg)

        # check for html file arg
        if arg == "-p":
            if debug_messages:
                print("file arg passed")

            # mark position of file arg

            pool_id_arg_position = arg_count

            if arg_len > pool_id_arg_position + 1:

                # quoates needed for  for multiple comands
                target_pool_id = command_line_args[pool_id_arg_position + 1]

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
                target_pool_id,
                directory_for_output,
                key_path,
                server_port_number)

        return PullOptions(target_pool_id, directory_for_output, key_path)

    return PullOptions(target_pool_id, directory_for_output)


##########################################################################
#
#   Start of the code
#
##########################################################################


# set options object directory and pool id
options_object = setup_options_object()

"""
API user and key setup

"""
# Get API key and Username from apikey.txt


# apiKeyFile

if options_object.get_key_path():
    apiKeyFile = options_object.get_key_path()

    if debug_messages:
        print(f"options_object.get_key_path() : {apiKeyFile}")

apiKeys = None
try:
    with open(apiKeyFile) as apiFile:
        apiKeys = apiFile.read().splitlines()
except FileNotFoundError:
    with open(apiKeyFile, "w") as apiFile:
        apiFile.write("user=" + os.linesep + "api_key=")


apiUser = apiKeys[0].split("=")[1]
apiKey = apiKeys[2].split("=")[1]

"""
if debug_messages:
    print(apiUser)
    print(apiKey)
"""



all_posts = []


# start download if provided a pool id

if options_object.get_search_pool_id():

    start_pool_search()
