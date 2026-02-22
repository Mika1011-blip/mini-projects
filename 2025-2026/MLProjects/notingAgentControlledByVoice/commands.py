from datetime import datetime
import os
# Compile regex
# EN

vault_fname = "vault.txt"

def create_vault():
    if not os.path.exists(vault_fname):
        with open(vault_fname, "w", encoding="utf-8") as f:
            f.write("")

def open_vault():
    create_vault()
    with open(vault_fname, "r", encoding="utf-8") as f:
        return f.read()

def empty_vault():
    with open(vault_fname, "w", encoding="utf-8") as f:
        f.write("")

def insert_vault(content : str):
    create_vault()
    content = (content or "").strip()
    if not content :
        return
    #timestamp
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(vault_fname, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {content}\n")
