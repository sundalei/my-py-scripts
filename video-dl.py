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
APP_TOKEN = config["app_token"]

with open("dynamic_rules.json", "r") as file:
    dynamic_rules = json.load(file)

# 0 = do not print file names or api calls
# 1 = print file names only when max_age is set
# 2 = always print file names
# 3 = print api calls
# 4 = print skipped files that already exist
VERBOSITY = 2
# Download Directory. Use CMD if null
DOWNLOAD_DIR = ""
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
    "app-token": APP_TOKEN,
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


def latest(profile):
    """Latest"""
    latest = "0"
    for dirpath, dirs, files in os.walk(profile):
        for f in files:
            if f.startswith("20"):
                latest = f if f > latest else latest
    return latest[:10]


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
        print(API_URL + endpoint + age + "\n")
    
    try:
        status = requests.get(API_URL + endpoint, headers=API_HEADER, params=get_params)
        if status.ok:
            list_base = status.json()
        else:
            return json.loads('{"error":{"message":"http ' + str(status.status_code) + '"}}')
    except requests.exceptions.ConnectTimeout as e:
        print("connection timeout")
        raise e

    # Fixed the issue with the maximum limit of 50
    if(len(list_base) >= posts_limit and api_type != "user-info") or ("hasMore" in list_base and list_base["hasMore"]):
        if api_type == "messages":
            get_params['id'] = str(list_base['list'][len(list_base['list'])-1]['id'])
        elif api_type == "purchased" or api_type == "subscriptions":
            get_params["offset"] = str(posts_limit)
        else:
            get_params["afterPublishTime"] = list_base[len(list_base) - 1]["postedAtPrecise"]
        
        while True:
            create_signed_headers(endpoint, get_params)
            if VERBOSITY >= 3:
                print(API_URL + endpoint + age)
            status = requests.get(API_URL + endpoint, headers=API_HEADER, params=get_params)
            if status.ok:
                list_extend = status.json()
            if api_type == "messages":
                list_base['list'].extend(list_extend['list'])
                if list_extend['hasMore'] == False or len(list_extend['list']) < posts_limit or not status.ok:
                    break
                get_params['id'] = str(list_base['list'][len(list_base['list']) - 1]['id'])
                continue
            list_base.extend(list_extend) # Merge with previous posts
            if len(list_extend) < posts_limit:
                break
            if api_type == 'purchased' or api_type == 'subscriptions':
                get_params['offset'] = str(int(get_params['offset']) + posts_limit)
            else:
                get_params['afterPublishTime'] = list_extend[len(list_extend) - 1]['postedAtPrecise']
            
    return list_base


def get_user_info(profile):
    """Get user info"""
    info = api_request("/users/" + profile, "user-info")
    if "error" in info:
        print("\nFailed to get user: " + profile + "\n" + info["error"]["message"] + "\n")
    return info


def get_subscriptions():
    """Get a list of all subscriptions"""
    subs = api_request("/subscriptions/subscribes", "subscriptions")
    if "error" in subs:
        print("\nSUBSCRIPTIONS ERROR: " + subs["error"]["message"])
        return
    return [row["username"] for row in subs]


def download_media():
    """Download media"""
    pass


def get_content(media_type, api_location):
    """Get content"""
    posts = api_request(api_location, media_type)

    if "error" in posts:
        print("\nERROR: " + API_LOCATION + " :: " + posts["error"]["message"])

    if media_type == "messages":
        posts = post["list"]

    if len(posts) > 0:
        print("Found " + str(len(posts)) + " " + media_type)
        for post in posts:
            if "media" not in post or ("canViewMedia" in post and not post["canViewMedia"]):
                continue
            if "postedAt" in post:
                post_date = str(post["postedAt"][:10])
            elif "createdAt" in post:
                post_date = str(post["createdAt"][:10])
            else:
                post_date = "1970-01-01"
            if len(post["media"]) > 1:
                album = str(post["id"])
            else:
                album = ""
            for media in post["media"]:
                if "files" in media and "canView" in media and media["canView"]:
                    download_media()            

    return posts


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
    
    for profile in PROFILE_LIST:
        if profile in SKIP_ACCOUNTS:
            if VERBOSITY > 0:
                print("Skipping " + profile)
            continue
        user_info = get_user_info(profile)

        if "id" in user_info:
            PROFILE_ID = str(user_info["id"])
        else:
            continue
        
        if LATEST:
            latestDate = latest(profile)
            if latestDate != "0":
                MAX_AGE = int(datetime.strftime(latestDate + " 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
                print("\nGetting posts newer than " + latestDate + " 00:00:00 UTC")
        
        if os.path.isdir(profile):
            print("\n" + profile + " exists.\nDownloading new media, skipping pre-existing.")
        else:
            print("\nDownloading content to " + profile)

        if POSTS:
            posts = get_content("posts", "/users/" + PROFILE_ID + "/posts")
