#!/usr/bin/env python3

"""
OnlyFans Downloader - A tool to download content from OnlyFans accounts

Configuration variables:
- user_id: User ID for authentication
- user_agent: HTTP user agent string
- x_bc: X-BC header value
- session_cookie: Session cookie for authentication
- verbosity: Logging verbosity level (0-4)
- download_dir: Directory to save downloaded content
- skip_accounts: List of accounts to skip downloading from
"""

import os
import sys
import json
import shutil
import pathlib
import hashlib
from datetime import datetime, timedelta
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
DOWNLOAD_DIR = ""
# List of accounts to skip
SKIP_ACCOUNTS = []

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
print("API_BASE_URL:", API_BASE_URL)

print(urllib3)
print(os)
print(sys)
print(json)
print(shutil)
print(pathlib)
print(requests)
print(hashlib)
print(datetime)
print(timedelta)
