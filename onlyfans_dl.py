#!/usr/bin/env python3

"""
Tool to download content from OnlyFans accounts

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
from datetime import datetime, timedelta, timezone

import requests
import urllib3

urllib3.disable_warnings()

# Configuration

# Session variables
USER_ID = ""
USER_AGENT = ""
X_BC = ""
SESSION_COOKIE = ""

# 0 = do not print file names or api calls
# 1 = print file names only when max_age is set
# 2 = always print file names
# 3 = print api calls
# 4 = print skipped files that already exist
VERBOSITY = 2
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

API_BASE_URL = "https://onlyfans.com/api2/v2"

print(sys)
print(json)
print(shutil)
print(pathlib)
print(requests)
print(hashlib)
print(datetime)
print(timedelta)

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
        "end": "67a0ec50",
        "start": "36587",
        "format": "36587:{}:{:x}:67a0ec50",
        "prefix": "36587",
        "suffix": "67a0ec50",
        "revision": "202502031617-af2daeeb87",
        "app_token": "33d57ade8c02dbc5a333db99ff9ae26a",
        "static_param": "r0COhCenVY6tUCrcnkbwz727f1m0UHsv",
        "remove_headers": ["user_id"],
        "checksum_indexes": [
            1,
            1,
            1,
            2,
            2,
            5,
            5,
            6,
            6,
            7,
            7,
            11,
            12,
            12,
            13,
            14,
            14,
            16,
            17,
            20,
            20,
            20,
            21,
            23,
            24,
            25,
            25,
            25,
            29,
            30,
            31,
            39,
        ],
        "checksum_constant": 118,
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
