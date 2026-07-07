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
from pymongo import MongoClient

# config
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://vault.sundalei.tech")
VAULT_TOKEN = os.environ["VAULT_TOKEN"]
KV_MOUNT = "secret"
SECRET_PATH = "mongo-es-demo"
MONGO_KEY = "spring.mongodb.uri"
COLLECTION = "movies"

# read the Mongo URI from vault
vault = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
assert vault.is_authenticated(), "Vault auth failed - check VAULT_TOKEN"

secret = vault.secrets.kv.v2.read_secret_version(path=SECRET_PATH, mount_point=KV_MOUNT)
mongo_uri = secret["data"]["data"][MONGO_KEY]
print(mongo_uri)
print(f"Got {MONGO_KEY} from Vault (len={len(mongo_uri)})")

# connect to Mongo
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=50000)
client.admin.command("ping")
print("Connected to MongoDB")

try:
    db = client.get_default_database()
    if db is None:
        raise ValueError
except (ValueError, Exception):
    names = [n for n in client.list_database_names() if n not in ('admin', 'local', 'config')]
    print(f"URI has no default DB; databases found: {names}")
    db = client[names[0]]

print(f"Using database: {db.name}")
print(f"Collections: {db.list_collection_names()}")

movies = db[COLLECTION]
count = movies.estimated_document_count()
print(f"\n '{COLLECTION}' collection: ~{count} documents\n")

for doc in movies.find({}).limit(5):
    print(doc)

client.close()
