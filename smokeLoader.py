#!/usr/bin/env python3
"""
A e621 gui to download post collections and pools

- to add:
ask for username and api_key if the file is blank or does not have it - done

add a picture for the index page

"""

from tkinter import *
from tkinter import filedialog
import _thread
import os
import platform
from PIL import ImageTk, Image
import pickle
import asyncio
import _thread
import socket


# A vector like class for positioning widgets


class GridPosition:
    def __init__(self, passed_row=None, passed_column=None):
        self.row = passed_row
        self.column = passed_column

    def get_row(self):
        return self.row

    def set_row(self, passed_row):
        self.row = passed_row

    def get_column(self):
        return self.column

    def set_column(self, passed_column):
        self.column = passed_column

# Cell_Widget custom class for setting widgets to add to display or remove
# easier


class Cell_Widget:
    def __init__(
            self,
            passed_widget,
            passed_grid_position,
            passed_cell_id_name):
        self.cell_widget = passed_widget
        self.cell_position = passed_grid_position
        self.cell_id_name = passed_cell_id_name

    def get_cell_widget(self):
        return self.cell_widget

    def get_cell_position(self):
        return self.cell_position

    def get_cell_id_name(self):
        return self.cell_id_name

    def show_widget(self):
        if self.cell_widget:
            if self.cell_position:
                self.cell_widget.grid(
                    row=self.cell_position.row,
                    column=self.cell_position.column)

    def hide_widget(self):
        if self.cell_widget:
            if self.cell_widget.winfo_ismapped():
                self.cell_widget.grid_remove()

            if self.cell_widget.winfo_exists():
                self.cell_widget.grid_remove()


debug_messages = False
test_debuging = False
currentFolder = os.path.dirname(os.path.realpath(__file__))

server_port_number = 8888

cleaned_current_directory_path = currentFolder.replace(' ', '\\ ')

download_gui_modes = ["tag download", "pool download"]

global current_mode

current_mode = download_gui_modes[1]

# dictionary to store setup tools

app_setup_tools = {}

# check for api key setup

currentFolder = os.path.dirname(os.path.realpath(__file__))
apiKeyFile = os.path.join(currentFolder, "apikey.txt")

app_setup_tools["currentFolder"] = currentFolder

# app page

app_pages = ["", "index_page", "ask_for_api_key_page", "download_page"]

global current_app_page

# set app pages to ""
current_app_page = app_pages[0]

# dictionary to store widgets for the download page

download_page_gui_objects = {}

# dictionary to store submit key widgets

submit_key_page_gui_objects = {}

# dictionary to store index

index_page_gui_objects = {}


####################################################
#
# Ask for api key code
#
####################################################


def record_provided_credentials_to_file():

    passed_username = submit_key_page_gui_objects["api_username_entry"].get_cell_widget(
    ).get()

    passed_api_key = submit_key_page_gui_objects["api_key_entry"].get_cell_widget(
    ).get()
    if debug_messages:
        print(f"user passed: {passed_username}")
        print(f"api key passed: {passed_api_key}")

    with open(apiKeyFile, "w") as apiFile:
        apiFile.write(
            f"user={passed_username}\n" +
            "\n" +
            f"api_key={passed_api_key}")

    clear_ask_for_api_info_page()
    present_gui_download_page()


####################################################
#
# GUI code for when Key is found
#
####################################################


def change_label_text(passed_label, passed_text):

    passed_label.config(text=passed_text)


def download_start():
    global current_mode

    change_label_text(
        download_page_gui_objects["download_message_label"].get_cell_widget(),
        "download started...")

    # Stop the button from being clicked again until downloading is done

    download_page_gui_objects["download_button"].get_cell_widget().config(
        state=DISABLED)

    # gui_modes = ["tag download","pool download"]

    # if in tag download mode download tags
    if current_mode == download_gui_modes[0]:
        if debug_messages:
            print(f"mode:{current_mode} running tag download")

        _thread.start_new_thread(tag_e621_download, ())
    # if in pool download mode dowload pool
    elif current_mode == download_gui_modes[1]:
        if debug_messages:
            print(f"mode:{current_mode} running pool pull")

        _thread.start_new_thread(pull_e621_pool, ())


def tag_e621_download():

    # get the entered search tags
    tags_entry_input = download_page_gui_objects["search_entry"].get_cell_widget(
    ).get()

    # get the destination for the file what will be downloaded
    passed_save_directory = download_page_gui_objects["save_directory_entry"].get_cell_widget(
    ).get()

    fail_pool_id_conditions = [
        "",
        "Enter the pools id",
        "Enter the search tags"]
    fail_passed_save_directory_conditions = ["", "Enter the save directory"]

    ready_status = True

    for bad_tag_input in fail_pool_id_conditions:
        if bad_tag_input == tags_entry_input:
            ready_status = False

    for bad_directory_input in fail_passed_save_directory_conditions:
        if bad_directory_input == passed_save_directory:
            ready_status = False

    # input pass checks
    if ready_status:

        if debug_messages:

            print(tags_entry_input)

        # call tag downloader
        # python source call

        target_system = platform.system()

        if target_system == 'Linux':
            # linux
            if server_port_number:
                command = f"\"{currentFolder}\"/e621_download_by_tag -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt -port {server_port_number}"
            else:
                command = f"\"{currentFolder}\"/e621_download_by_tag -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"
        elif target_system == 'Darwin':
            # OS X mac
            idk = ":>"
        elif target_system == 'Windows':
            # Windows...
            if test_debuging:

                # server_port_number
                if server_port_number:
                    command = f"python3 e621_download_by_tag.py -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt -port {server_port_number}"
                #command = f"python3 e621_download_by_tag.py -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"
                else:
                    command = f"python3 e621_download_by_tag.py -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"
            else:
                command = f"\"{cleaned_current_directory_path}\"/e621_download_by_tag.exe -t \"{tags_entry_input}\" -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"

        # send the command to system
        os.system(command)

        # after download program is either finish from error of completed
        # downloading

        download_page_gui_objects["download_button"].get_cell_widget().config(
            state=NORMAL)

        # good or fail process is done send download complete message

        change_label_text(
            download_page_gui_objects["download_message_label"].get_cell_widget(),
            "download is complete")
    else:
        # download_button.config(state=NORMAL)

        download_page_gui_objects["download_button"].get_cell_widget().config(
            state=NORMAL)
        """change_label_text(
            download_message_label,
            "error invalid entry detected")"""

        change_label_text(
            download_page_gui_objects["download_message_label"].get_cell_widget(),
            "error invalid entry detected")


def pull_e621_pool():
    #passed_pool_id = search_entry.get()
    passed_pool_id = download_page_gui_objects["search_entry"].get_cell_widget(
    ).get()
    #passed_save_directory = save_directory_entry.get()
    passed_save_directory = download_page_gui_objects["save_directory_entry"].get_cell_widget(
    ).get()

    fail_pool_id_conditions = [
        "",
        "Enter the pools id",
        "Enter the search tags"]

    fail_passed_save_directory_conditions = ["", "Enter the save directory"]

    ready_status = True

    for bad_pool_input in fail_pool_id_conditions:
        if bad_pool_input == passed_pool_id:
            ready_status = False

    for bad_directory_input in fail_passed_save_directory_conditions:
        if bad_directory_input == passed_save_directory:
            ready_status = False

    # input pass checks
    if ready_status:

        target_sysetem = platform.system()

        if target_sysetem == 'Linux':
            # linux
            if server_port_number:
                command = f"\"{currentFolder}\"/e621_pool_downloader -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt -port {server_port_number}"
            else:
                command = f"\"{currentFolder}\"/e621_pool_downloader -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"

        elif target_sysetem == 'Darwin':
            # OS X mac
            idk = ":>"
        elif target_sysetem == 'Windows':
            # Windows...
            if test_debuging:
                # runs .py instead of exe
                if server_port_number:
                    command = f"\"python3 e621_pool_downloader.py -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt -port {server_port_number}"
                else:
                    command = f"python3 e621_pool_downloader.py -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"

            else:

                if server_port_number:
                    command = f"\"{currentFolder}\"/e621_pool_downloader.exe -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt -port {server_port_number}"
                else:
                    command = f"\"{currentFolder}\"/e621_pool_downloader.exe -p {passed_pool_id} -d {passed_save_directory} -key \"{currentFolder}\"/apikey.txt"
        os.system(command)

        download_page_gui_objects["download_button"].get_cell_widget().config(
            state=NORMAL)

        change_label_text(
            download_page_gui_objects["download_message_label"].get_cell_widget(),
            "download is complete")
    else:
        # download_button.config(state=NORMAL)

        download_page_gui_objects["download_button"].get_cell_widget().config(
            state=NORMAL)

        change_label_text(
            download_page_gui_objects["download_message_label"].get_cell_widget(),
            "error invalid entry detected")


def switch_downloader_mode():
    global current_mode
    # gui_modes = ["tag download","pool download"]

    # if on tag download mode switch to pool download mode
    if current_mode == download_gui_modes[0]:

        current_mode = download_gui_modes[1]

        # change switch text

        download_page_gui_objects["pool_tag_switch"].get_cell_widget().config(
            text="switch to tags")
        # change search_entry label

        download_page_gui_objects["search_label"].get_cell_widget().config(
            text="Pool ID#")

        # change search_entry text

        download_page_gui_objects["search_entry"].get_cell_widget().delete(
            0, "end")

        # enter pool id message

        download_page_gui_objects["search_entry"].get_cell_widget().insert(
            0, "Enter the pools id")

    # if on pool download mode switch to tag download mode
    elif current_mode == download_gui_modes[1]:

        current_mode = download_gui_modes[0]

        # change switch text

        download_page_gui_objects["pool_tag_switch"].get_cell_widget().config(
            text="switch to pool")

        # change search_entry label

        download_page_gui_objects["search_label"].get_cell_widget().config(
            text="Search tags")

        # change search_entry text

        download_page_gui_objects["search_entry"].get_cell_widget().delete(
            0, "end")

        # enter search tags message

        download_page_gui_objects["search_entry"].get_cell_widget().insert(
            0, "Enter the search tags")


"""

Download page functions


"""


def clear_search_entry():

    # change search_entry text

    download_page_gui_objects["search_entry"].get_cell_widget().delete(
        0, "end")


def clear_directory_entry():

    # change search_entry text

    download_page_gui_objects["save_directory_entry"].get_cell_widget().delete(
        0, "end")


def clear_current_page():

    #app_pages = ["index_page","ask_for_api_key_page","download_page"]
    if current_app_page == "index_page":
        mmh = "do a thing"
        hide_index_page_objects()
    elif current_app_page == "ask_for_api_key_page":

        clear_ask_for_api_info_page()

    elif current_app_page == "download_page":

        hide_gui_download_elements()


def explorer_directory_select():
    selected_save_directory = filedialog.askdirectory()

    # clear entry if a directory is chosen
    if selected_save_directory:

        download_page_gui_objects["save_directory_entry"].get_cell_widget().delete(
            0, "end")
        download_page_gui_objects["save_directory_entry"].get_cell_widget().insert(
            0, selected_save_directory)


def load_gui_download_page():

    switch_text = None
    search_text = None

    # gui_modes = ["tag download","pool download"]
    if current_mode == download_gui_modes[0]:
        switch_text = "switch to pool"
        search_text = "Search tags"

    elif current_mode == download_gui_modes[1]:

        switch_text = "switch to tags"
        search_text = "Pool ID#"

    if ("pool_tag_switch" in download_page_gui_objects) == False:

        download_page_gui_objects["pool_tag_switch"] = Cell_Widget(Button(
            root,
            text=switch_text,
            command=switch_downloader_mode,
            fg="blue"), GridPosition(0, 0), "pool_tag_switch")

    # search label
    # starts in pool mode , maybe it should start in tags?
    if ("search_label" in download_page_gui_objects) == False:
        download_page_gui_objects["search_label"] = Cell_Widget(
            Label(root, text=search_text), GridPosition(1, 0), "search_label")

    # search entry
    if ("search_entry" in download_page_gui_objects) == False:
        download_page_gui_objects["search_entry"] = Cell_Widget(
            Entry(root, width=50), GridPosition(2, 0), "search_entry")

        download_page_gui_objects["search_entry"].get_cell_widget().insert(
            0, "Enter the pools id")

    # clear search button

    if ("clear_search_input_button" in download_page_gui_objects) == False:

        download_page_gui_objects["clear_search_input_button"] = Cell_Widget(
            Button(root, text="X", command=clear_search_entry, fg="red"),
            GridPosition(2, 1),
            "clear_search_input_button"
        )

    download_page_gui_objects["save_directory_label"] = Cell_Widget(
        Label(root, text="Save Directory"), GridPosition(3, 0), "save_directory_label")

    # save directory entry
    #
    download_page_gui_objects["save_directory_entry"] = Cell_Widget(
        Entry(root, width=50), GridPosition(4, 0), "save_directory_entry")

    download_page_gui_objects["save_directory_entry"].get_cell_widget().insert(
        0, "Enter the save directory")

    # clear directory input button

    download_page_gui_objects["clear_directory_input_button"] = Cell_Widget(
        Button(
            root, text="X", command=clear_directory_entry, fg="red"), GridPosition(
            4, 1), "clear_directory_input_button")

    # select directory button

    # folder image lol this thing is a problem tbh
    # windows / univeral?
    folder_image = PhotoImage(
        # file=f"{currentFolder}/images/folder_image/folder.png")
        # exe version
        file=f"{currentFolder}/images/folder.png")
    # linux
    #folder_image = PhotoImage(file = r"/usr/local/lib/e621_smoke_gui_downloaders/images/folder_image/folder.png")

    resized_folder_image = folder_image.subsample(3, 3)

    download_page_gui_objects["select_directory_button_folder_image"] = resized_folder_image

    download_page_gui_objects["select_directory_button"] = Cell_Widget(
        Button(
            root,
            image=resized_folder_image,
            command=explorer_directory_select),
        GridPosition(4, 2),
        "select_directory_button"
    )

    """folder_image = Image.open(f"{currentFolder}/images/folder.png")

    folder_image_x, folder_image_y = folder_image.size

    resized_folder_image= folder_image.resize(( int(folder_image_x/3), int(folder_image_y /3)))

    my_img=ImageTk.PhotoImage(resized_folder_image)

    download_page_gui_objects["select_directory_button"] = Cell_Widget(
        Button(
        root,
        image=my_img,
        command=explorer_directory_select),
        GridPosition(4,2),
        "select_directory_button"
        )"""

    # save input directory for future use

    # download button

    download_page_gui_objects["download_button"] = Cell_Widget(Button(
        root,
        text="Download",
        command=download_start,
        fg="blue"),
        GridPosition(5, 0),
        "download_button"
    )

    download_page_gui_objects["download_message_label"] = Cell_Widget(
        Label(root, text=""),
        GridPosition(6, 0),
        "download_message_label"
    )

# perhaps check for tools, the downloaders (pool and tag downloaders)


def present_gui_download_page():
    global current_app_page
    """app_pages = ["","index_page","ask_for_api_key_page","download_page"]

    current_app_page = app_pages[0] """
    # if the app is not currently displaying the download page
    if current_app_page != "download_page":

        # clear the current page, then show download page

        clear_current_page()

        load_gui_download_page()

        current_app_page = "download_page"

        download_page_gui_objects["pool_tag_switch"].show_widget()

        download_page_gui_objects["search_label"].show_widget()

        download_page_gui_objects["search_entry"].show_widget()

        download_page_gui_objects["clear_search_input_button"].show_widget()

        download_page_gui_objects["save_directory_label"].show_widget()

        download_page_gui_objects["save_directory_entry"].show_widget()

        download_page_gui_objects["clear_directory_input_button"].show_widget()

        # readd image to folder button
        download_page_gui_objects["select_directory_button"].get_cell_widget().config(
            image=download_page_gui_objects["select_directory_button_folder_image"])
        download_page_gui_objects["select_directory_button"].show_widget()

        download_page_gui_objects["download_button"].show_widget()

        download_page_gui_objects["download_message_label"].show_widget()

# removes the download page widgits from the grid


def hide_gui_download_elements():

    download_page_gui_objects["pool_tag_switch"].hide_widget()

    download_page_gui_objects["search_label"].hide_widget()

    download_page_gui_objects["search_entry"].hide_widget()

    download_page_gui_objects["clear_search_input_button"].hide_widget()

    download_page_gui_objects["save_directory_label"].hide_widget()

    download_page_gui_objects["save_directory_entry"].hide_widget()

    download_page_gui_objects["clear_directory_input_button"].hide_widget()

    download_page_gui_objects["select_directory_button"].hide_widget()

    download_page_gui_objects["download_button"].hide_widget()

    download_page_gui_objects["download_message_label"].hide_widget()


"""

API Key page functions

"""

################################################
#
# Ask for api key info widgits
#
################################################

# present widits to download stuff

# shows for to ask for missing "apikey.txt" file


def load_ask_for_api_info_page():
    """app_pages = ["","index_page","ask_for_api_key_page","download_page"]

    current_app_page = app_pages[0] """

    if ("missing_api_key_message_label" in submit_key_page_gui_objects) == False:
        missing_key_text = "\"apikey.txt\" was not found please enter your api info to continue"
        submit_key_page_gui_objects["missing_api_key_message_label"] = Cell_Widget(
            Label(
                root, text=missing_key_text, font=('Mistral 10 bold')), GridPosition(
                0, 0), "missing_api_key_message_label")
    if ("enter_username_label" in submit_key_page_gui_objects) == False:
        submit_key_page_gui_objects["enter_username_label"] = Cell_Widget(
            Label(
                root,
                text="Please enter your E621 username",
                font=('Mistral 10 bold')),
            GridPosition(
                1,
                0),
            "enter_username_label")

    if ("api_username_entry" in submit_key_page_gui_objects) == False:
        submit_key_page_gui_objects["api_username_entry"] = Cell_Widget(
            Entry(root, width=50), GridPosition(2, 0), "api_username_entry")

    if ("enter_api_key_label" in submit_key_page_gui_objects) == False:

        submit_key_page_gui_objects["enter_api_key_label"] = Cell_Widget(
            Label(
                root,
                text="Please enter your E621 API key",
                font=('Mistral 10 bold')),
            GridPosition(
                3,
                0),
            "enter_api_key_label")

    if ("api_key_entry" in submit_key_page_gui_objects) == False:
        submit_key_page_gui_objects["api_key_entry"] = Cell_Widget(
            Entry(root, width=50),
            GridPosition(4, 0),
            "api_key_entry"
        )

    if ("api_key_page_submit_button" in submit_key_page_gui_objects) == False:

        submit_key_page_gui_objects["api_key_page_submit_button"] = Cell_Widget(
            Button(root, text="submit", command=record_provided_credentials_to_file),
            GridPosition(5, 0),
            "api_key_page_submit_button"
        )


def present_ask_for_api_info_page():

    global current_app_page

    if current_app_page != "ask_for_api_key_page":

        # clear the current page, then show download page

        clear_current_page()

        current_app_page = "ask_for_api_key_page"

    # app_pages = ["","index_page","ask_for_api_key_page","download_page"]

        load_ask_for_api_info_page()

        # check for API Key file currently unused
        currentFolder = os.path.dirname(os.path.realpath(__file__))
        apiKeyFile = os.path.join(currentFolder, "apikey.txt")

        api_key_file_found = os.path.isfile(apiKeyFile)

        if api_key_file_found is False:

            submit_key_page_gui_objects["missing_api_key_message_label"].show_widget(
            )

        if api_key_file_found:
            apiKeys = None
            with open(apiKeyFile) as apiFile:
                apiKeys = apiFile.read().splitlines()

            if apiKeys:
                # print(len(apiKeys))
                api_username = ""
                api_key = ""

                if len(apiKeys) > 0:
                    api_username = apiKeys[0].split("=")[1]
                if len(apiKeys) > 2:
                    api_key = apiKeys[2].split("=")[1]
                # show api username entry with username inside

                submit_key_page_gui_objects["enter_username_label"].show_widget(
                )
                submit_key_page_gui_objects["api_username_entry"].show_widget()
                submit_key_page_gui_objects["api_username_entry"].get_cell_widget().insert(
                    0, api_username)

                # show api key entry with key inside

                submit_key_page_gui_objects["enter_api_key_label"].show_widget(
                )
                submit_key_page_gui_objects["api_key_entry"].show_widget()
                submit_key_page_gui_objects["api_key_entry"].get_cell_widget().insert(
                    0, api_key)

        else:

            submit_key_page_gui_objects["enter_username_label"].show_widget()

            submit_key_page_gui_objects["api_username_entry"].show_widget()

            submit_key_page_gui_objects["enter_api_key_label"].show_widget()

            submit_key_page_gui_objects["api_key_entry"].show_widget()

        submit_key_page_gui_objects["api_key_page_submit_button"].show_widget()


def clear_ask_for_api_info_page():
    """ app_pages = ["","index_page","ask_for_api_key_page","download_page"]

    current_app_page = app_pages[0] """
    # if the app is not currently displaying the download page

    submit_key_page_gui_objects["missing_api_key_message_label"].hide_widget()

    submit_key_page_gui_objects["enter_username_label"].hide_widget()

    submit_key_page_gui_objects["enter_api_key_label"].hide_widget()

    submit_key_page_gui_objects["api_username_entry"].hide_widget()

    submit_key_page_gui_objects["api_key_entry"].hide_widget()

    submit_key_page_gui_objects["api_key_page_submit_button"].hide_widget()

    if debug_messages:
        print("clear complete")


"""

Index page functions

"""


def load_index_page():

    if ("index_page_image_label" in index_page_gui_objects) == False:

        # Using tkinter.PhotoImage
        """fun_image = PhotoImage(file = f"{app_setup_tools['currentFolder']}/images/folder.png")
        print(fun_image)
        resized_fun_image = fun_image.subsample(2, 2)
        print(resized_fun_image)
        index_page_gui_objects["index_page_image_label"] = Cell_Widget(
            Label(app_setup_tools["root"], image = fun_image),
            GridPosition(0,0),
            "index_page_image_label" )

        if debug_messages:
            print("index_page_image was loaded")
            """
        # cannot read jpg
        """base_image_file = PhotoImage(file = f"{app_setup_tools['currentFolder']}/images/bb.jpg")

        size_alt_image = base_image_file.subsample(2, 2)
        dope_bun_image = ImageTk.PhotoImage(size_alt_image)

        index_page_gui_objects["index_page_image"] = dope_bun_image

        index_page_gui_objects["index_page_image_label"] = Cell_Widget(
            Label(app_setup_tools["root"], image=dope_bun_image),
            GridPosition(0, 0),
            "index_page_image_label")"""

        # using PIL.ImageTk.PhotoImage
        if debug_messages:
            print("index_page_image was loaded")

        base_image_file = Image.open(
            f"{app_setup_tools['currentFolder']}/images/bb.jpg")
        bb_width, bb_height = base_image_file.size
        size_alt_image = base_image_file.resize(
            (int(bb_width / 3), int(bb_height / 3)))
        dope_bun_image = ImageTk.PhotoImage(size_alt_image)

        index_page_gui_objects["index_page_image"] = dope_bun_image

        index_page_gui_objects["index_page_image_label"] = Cell_Widget(
            Label(app_setup_tools["root"], image=dope_bun_image),
            GridPosition(0, 0),
            "index_page_image_label")


def present_index_page_objects():
    """app_pages = app_pages = ["","index_page","ask_for_api_key_page","download_page"]

    current_app_page = app_pages[0] """
    global current_app_page
    # set app page as index page
    if current_app_page != app_pages[1]:
        current_app_page = app_pages[1]

        load_index_page()

        # readd image to index page image label
        index_page_gui_objects["index_page_image_label"].get_cell_widget().config(
            image=index_page_gui_objects["index_page_image"])
        index_page_gui_objects["index_page_image_label"].show_widget()


def hide_index_page_objects():
    if ("index_page_image_label" in index_page_gui_objects):

        index_page_gui_objects["index_page_image_label"].hide_widget()


def setup_app_menu():
    menubar = Menu(
        root,
        background='#ff8000',
        foreground='black',
        activebackground='white',
        activeforeground='black')

    file = Menu(menubar, tearoff=1, background='#ffcc99', foreground='black')
    file.add_command(
        label="Download Posts and Pools",
        command=present_gui_download_page)
    file.add_command(
        label="Add API Key",
        command=present_ask_for_api_info_page)

    file.add_separator()
    file.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file)

    root.config(menu=menubar)


####################################################
#
# server for tool communication
#
####################################################

async def handle_server_calls(reader, writer):
    data = await reader.read(100)
    message = data
    addr = writer.get_extra_info('peername')

    inflated_message = pickle.loads(message)

    if debug_messages:
        print(f"Received {inflated_message} from {addr!r}")

    #print(f"Send: {message!r}")
    # writer.write(data)

    # execute command based on the recieved output

    # change download text from recieved output

    await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(
        handle_server_calls, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    if debug_messages:
        print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()


def socket_server():
    HEADER_LENGTH = 100
    HEADERSIZE = 10

    DATA_LENGTH = None

    IP = "localhost"
    PORT = server_port_number
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port

    serversocket.bind((IP, PORT))
    # become a server socket
    serversocket.listen()

    while True:

        try:
            # accept connections from outside
            (clientsocket, address) = serversocket.accept()
            # now do something with the clientsocket
            # in this case, we'll pretend this is a threaded server
            if debug_messages:
                print(f"{clientsocket}: {address} accepted")

            full_msg = b''
            all_data = None
            new_msg = True

            while True:

                msg = clientsocket.recv(18)
                if len(msg) <= 0:
                    print("break called")
                    break
                else:
                    full_msg += msg

                    """if len(full_msg) > 0:
                        print(full_msg)
                        # read data size
                        if full_msg.isnumeric():

                            print("data amount recieved")"""
            inflated = pickle.loads(full_msg)

            if debug_messages:
                print(inflated)
            # print(str(full_msg).find('\\'))
            #inflated = pickle.loads(all_data)
            # change download message text
            change_label_text(
                download_page_gui_objects["download_message_label"].get_cell_widget(),
                inflated['message'])
            if debug_messages:
                print(inflated['message'])
        except KeyboardInterrupt:
            # end code
            serversocket.close()
            exit()


def run_server():

    # asyncio.run(main())
    socket_server()


def open_tool_communication():
    try:
        _thread.start_new_thread(run_server, ())

    except BaseException:
        print("Error: unable to start server thread")

#########################################################################
#
# Start of tkinter functions
#
#########################################################################


open_tool_communication()
root = Tk()

app_setup_tools["root"] = root
root.title("SmokeLoader e621 downloader")

# setup menu

setup_app_menu()


# show the idex page
present_index_page_objects()

# check for API Key file currently unused
currentFolder = os.path.dirname(os.path.realpath(__file__))
apiKeyFile = os.path.join(currentFolder, "apikey.txt")

api_key_file_found = os.path.isfile(apiKeyFile)


root.mainloop()
