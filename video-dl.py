#!/usr/bin/env python3

"""
Tool to download video content

Configuration variables:
- user_id: User ID for authentication
- user_agent: HTTP user agent string
- x_bc: X-BC header value
- session_cookie: Session cookie for authentication
- verbosity: Logging verbosity level (0-4)
- download_dir: Directory to save downloaded content
- skip_accounts: List of accounts to skip downloading from
"""

import hashlib
import json
import os
import pathlib
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
import urllib3

urllib3.disable_warnings()

# Configuration

# Session variables
with open("config.json", "r") as file:
    config = json.load(file)

USER_ID = config["user_id"]
USER_AGENT = config["user_agent"]
X_BC = config["x_bc"]
SESSION_COOKIE = config["sess"]

# 0 = do not print file names or api calls
# 1 = print file names only when max_age is set
# 2 = always print file names
# 3 = print api calls
# 4 = print skipped files that already exist
VERBOSITY = 3
# Download Directory. Use CMD if null
DOWNLOAD_DIR = "/Users/sundalei/Downloads"
# List of accounts to skip
SKIP_ACCOUNTS: list[str] = []

# Separate photos into subdirectories by post/album
# Single photo posts are not put into subdirectories
SEPARATE_ALBUMS = True

# Use content type subfolders
USE_SUB_FOLDERS = True

# Content types to download
VIDEOS = True
PHOTOS = True
AUDIO = True
POSTS = True
STORIES = True
MESSAGES = True
ARCHIVED = True
PURCHASED = True

# End configurations

API_URL = "https://onlyfans.com/api2/v2"
new_files = 0
MAX_AGE = 0
LATEST = 0
API_HEADER = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate",
    "app-token": "33d57ade8c02dbc5a333db99ff9ae26a",
    "User-Agent": USER_AGENT,
    "x-bc": X_BC,
    "user-id": USER_ID,
    "Cookie": "auh_id=" + USER_ID + "; sess=" + SESSION_COOKIE,
    "Referer": "https://onlyfans.com/",
}


def create_signed_headers(link, queryParams):
    """
    Create signed headers for OnlyFans API
    """
    global API_HEADER
    path = "/api2/v2" + link
    if queryParams:
        query = "&".join("=".join((key, value)) for (key, value) in queryParams.items())
        path = f"{path}?{query}"

    unixtime = str(int(datetime.now().timestamp()))
    msg = "\n".join([dynamic_rules["static_param"], unixtime, path, str(USER_ID)])
    message = msg.encode("utf-8")
    hash_object = hashlib.sha1(message)
    sha_1_sign = hash_object.hexdigest()
    sha_1_b = sha_1_sign.encode("ascii")
    checksum = sum([sha_1_b[number] for number in dynamic_rules["checksum_indexes"]])
    checksum += dynamic_rules["checksum_constant"]
    API_HEADER["sign"] = dynamic_rules["format"].format(sha_1_sign, abs(checksum))
    API_HEADER["time"] = unixtime
    return


def show_age(ts):
    """Show the age of a timestamp"""
    print("show age:", ts)
    tmp = ts.split(".")
    part0 = int(tmp[0])
    dt_obj = datetime.fromtimestamp(part0, tz=timezone.utc)
    return dt_obj.strftime("%Y-%m-%d")


def api_request(endpoint, api_type):
    """
    Request endpoints
    """
    posts_limit = 50
    age = ""
    get_params = {
        "limit": str(posts_limit),
        "order": "publish_date_asc",
    }

    if api_type == "messages":
        get_params["order"] = "desc"
    if api_type == "subscriptions":
        get_params["type"] = "active"
    if MAX_AGE:
        if api_type != "messages" and api_type != "subscriptions" and api_type != "purchased":
            get_params["afterPublishTime"] = str(MAX_AGE) + ".000000"
            age = " age " + str(show_age(get_params["afterPublishTime"]))
            # Messages can only be limited by offset or last message ID.
    create_signed_headers(endpoint, get_params)
    if VERBOSITY >= 3:
        print(API_URL + endpoint + age)
    
    try:
        status = requests.get(API_URL + endpoint, headers=API_HEADER, params=get_params)
        if status.ok:
            list_base = status.json()
        else:
            return json.loads('{"error":{"message":"http ' + str(status.status_code) + '"}}')
    except requests.exceptions.ConnectTimeout as e:
        print("connection timeout")
        raise e

    return list_base


def get_subscriptions():
    """Get a list of all subscriptions"""
    subs = api_request("/subscriptions/subscribes", "subscriptions")
    if "error" in subs:
        print("\nSUBSCRIPTIONS ERROR: " + subs["error"]["message"])
        return
    return [row["username"] for row in subs]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " <list of profiles / all> <max age (optional)>")
        print("max age must be an integer. number of days back from today.")
        print("if max age = 0, the script will find the latest date amongst the files for each profile independantly.")
        print("Make sure to update the session variables at the top of this script (See readme).")
        print("Update Browser User Agent (Every time it updates): https://ipchicken.com/")
        sys.exit()

    if DOWNLOAD_DIR:
        try:
            os.chdir(DOWNLOAD_DIR)
        except OSError:
            print("Unable to use DOWNLOAD_DIR: " + DOWNLOAD_DIR)
    print("Download directory: " + os.getcwd())
    # Rules for the signed headers
    dynamic_rules = {
        "format": "51892:{}:{:x}:69406376",
        "app_token": "33d57ade8c02dbc5a333db99ff9ae26a",
        "static_param": "7HMjX3tp4B4JJDOryHAMCUIQCtmGq69D",
        "remove_headers": ["user-id"],
        "checksum_indexes": [
            15,
            35,
            3,
            7,
            21,
            26,
            39,
            35,
            4,
            0,
            6,
            29,
            35,
            28,
            37,
            27,
            22,
            4,
            9,
            10,
            37,
            21,
            27,
            13,
            17,
            31,
            28,
            24,
            0,
            14,
            9,
            0,
        ],
        "checksum_constant": 53,
    }
    PROFILE_LIST = sys.argv
    PROFILE_LIST.pop(0)

    if PROFILE_LIST[-1] == "0":
        LATEST = 1
        PROFILE_LIST.pop(-1)
    if len(PROFILE_LIST) > 1 and PROFILE_LIST[-1].isnumeric():
        MAX_AGE = int((datetime.today() - timedelta(int(PROFILE_LIST.pop(-1)))).timestamp())
        from_time = datetime.fromtimestamp(int(MAX_AGE), tz=timezone.utc)
        print("\nGetting posts newer than " + str(from_time) + " UTC")

    if PROFILE_LIST[0] == "all":
        PROFILE_LIST = get_subscriptions()
    print("profile list", PROFILE_LIST)
