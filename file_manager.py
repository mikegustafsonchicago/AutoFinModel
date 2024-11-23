# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:09:12 2024

@author: mikeg
"""

# file_manager.py
import os
import json
import logging
from config import RUNNING_SUMMARY_FILE

def ensure_directory_exists(path):
    """Ensure a directory exists, create it if it doesn't."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def read_file(file_path, default=""):
    """Read a file and return its contents. Return a default value if the file does not exist."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return default

def write_file(file_path, content):
    """Write content to a file, ensuring the directory exists."""
    ensure_directory_exists(file_path)
    with open(file_path, "w") as file:
        file.write(content)

def read_json(file_path):
    """Read a JSON file and return its contents."""
    with open(file_path, "r") as file:
        return json.load(file)

def write_json(file_path, data):
    """Write data to a JSON file."""
    ensure_directory_exists(file_path)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def initialize_session_files(project_name, json_manager):
    json_manager.initialize_json_files(project_name)
    #TODO: Move this to running summary manager
    running_summary = "This is the first call for this project and there is no running summary."
    with open(RUNNING_SUMMARY_FILE, "w") as file:
        file.write(running_summary)
