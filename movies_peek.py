#!/usr/bin/env python3
"""
Fetch the Mongo URI from Vault, connect, and peek at the movies connection.

Setup:
    pip install hvac "pymongo[srv]"

Run (token via env so it isn't hard-coded):
    export VAULT_TOKEN='hvs....'   # root token for now; scoped token later
    python movies_peek.py
"""

import os
import hvac

# config
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://vault.sundalei.tech")
VAULT_TOKEN = os.environ["VAULT_TOKEN"]
KV_MOUNT = "secret"
SECRET_PATH = "mongo-es-demo"

# read the Mongo URI from vault
vault = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
assert vault.is_authenticated(), "Vault auth failed - check VAULT_TOKEN"

secret = vault.secrets.kv.v2.read_secret_version(path=SECRET_PATH, mount_point=KV_MOUNT)
print(secret)
