"""
Shared Elasticsearch configuration and environment loader.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Required settings. os.environ raises KeyError if one is missing.
BASE_URL = os.environ["ELASTIC_BASE_URL"]
USERNAME = os.environ["ELASTIC_USER"]
PASSWORD = os.environ["ELASTIC_PASSWORD"]

# Optional CA certificate path for direct Elasticsearch TLS.
# Behind a reverse proxy such as Caddy, Requests can use the system CA bundle.
CA_CERT_PATH = os.getenv("ELASTIC_CERT_PATH")
VERIFY_CERT = CA_CERT_PATH or True
