"""
Shared Elasticsearch configuration and environment loader.
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ELASTIC_BASE_URL")
USERNAME = os.getenv("ELASTIC_USER")
PASSWORD = os.getenv("ELASTIC_PASSWORD")
CA_CERT_PATH = os.getenv("ELASTIC_CERT_PATH")

if USERNAME is None or PASSWORD is None:
    raise ValueError("Missing Elastic credentials! Check your .env file.")
