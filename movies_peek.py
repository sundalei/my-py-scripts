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

# config
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://vault.sundalei.tech")

print(VAULT_ADDR)
