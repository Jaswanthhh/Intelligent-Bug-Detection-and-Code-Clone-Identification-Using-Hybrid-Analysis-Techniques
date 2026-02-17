import os

def delete_system():
    # CRITICAL: Deleting system files
    os.system("rm -rf /")

def hardcoded_secret():
    # CRITICAL: Hardcoded API key
    api_key = "sk-1234567890abcdef1234567890abcdef"
    print(api_key)
