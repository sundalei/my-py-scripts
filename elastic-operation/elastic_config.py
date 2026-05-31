"""
Shared Elasticsearch configuration and environment loader.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Using os.environ guarantees a strict 'str' type for MyPy.
# It will automatically raise a KeyError if the variable is missing from your .env file.
BASE_URL = os.environ["ELASTIC_BASE_URL"]
USERNAME = os.environ["ELASTIC_USER"]
PASSWORD = os.environ["ELASTIC_PASSWORD"]
CA_CERT_PATH = os.environ["ELASTIC_CERT_PATH"]

if USERNAME is None or PASSWORD is None:
    raise ValueError("Missing Elastic credentials! Check your .env file.")
