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
            api_key_path=None):
        self.search_tags = search_tags
        self.target_directory = target_directory
        self.api_key_path = api_key_path

    def get_search_tags(self):
        return self.search_tags

    def get_target_directory(self):
        return self.target_directory

    def get_key_path(self):
        return self.api_key_path

    def set_key_path(self, passed_key_path):
        self.api_key_path = passed_key_path


#########################
# setup
#####################


arg_len = len(sys.argv)

if debug_messages:

    print("Total args passed: ", arg_len)


opt_obj = None

# html file options
tag_arg_position = None

# directory options
directory_arg_position = None
directory_for_output = None
search_tags = None

# api key file
currentFolder = os.path.dirname(os.path.realpath(__file__))
apiKeyFile = os.path.join(currentFolder, "apikey.txt")


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
        os.system(
            "wget --no-check-certificate -nc {} --directory-prefix=\"{}\"".format(
                full_post_url, str(
                    opt_obj.get_target_directory())))


def download_process():

    # check if aki key file is present in directory

    # api key file
    currentFolder = os.path.dirname(os.path.realpath(__file__))
    apiKeyFile = os.path.join(currentFolder, "apikey.txt")

    if opt_obj.get_key_path():
        apiKeyFile = opt_obj.get_key_path()

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

    tag = str(opt_obj.get_search_tags())
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

        arg_count = arg_count + 1

    # if key_path is not None create pull option with key_path
    if key_path:
        return PullOptions(search_tags, directory_for_output, key_path)

    return PullOptions(search_tags, directory_for_output)

#
# start of code
#


opt_obj = setup_options_object()


if opt_obj.get_search_tags():
    if debug_messages:
        print(f"search tags: {opt_obj.get_search_tags()}")

    if opt_obj.get_target_directory():
        # do thing
        if debug_messages:
            print(f"directory_for_output: {opt_obj.get_target_directory()}")
        # did not remove the option object creation
        #opt_obj = PullOptions(opt_obj.get_search_tags(), opt_obj.get_target_directory())

        """if debug_messages:
            print(opt_obj.get_search_tags())
            print(opt_obj.get_target_directory())"""
        # do process

        download_process()
    else:
        print("please provide a save directory")
        print("ie: code -d \"/special_folder/stuff\"")

else:
    print("please provide e621 search tags")
    print("ie: code -t \"banana \"")
