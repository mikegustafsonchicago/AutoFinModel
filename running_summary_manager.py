# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:14:01 2024

@author: mikeg
"""
import os
import logging
from config import RUNNING_SUMMARY_FILE

# running_summary_manager.py
from file_manager import write_file

class RunningSummaryManager:
    def __init__(self, file_path):
        self.file_path = file_path
        
        
    def get_summary(self):
        # Load the current running summary from a file, or start with an empty string if the file doesn't exist
        if os.path.exists(RUNNING_SUMMARY_FILE):
            with open(RUNNING_SUMMARY_FILE, "r") as file:
                self.running_summary = file.read()
        else:
            # Initialize the running summary content
            self.running_summary = "This is the first call for this project and there is no running summary."
            
            # Create the file and write the initial content
            logging.debug(f"Summary rewrite call. Here it is \n{self.running_summary}")
            with open(RUNNING_SUMMARY_FILE, "w") as file:
                file.write(self.running_summary)
        return self.running_summary

    def update_summary(self, new_content):
        """Append new content to the running summary."""
        self.running_summary = new_content
        logging.debug(f"Update summary call. Here it is \n{self.running_summary}\n here's new content \n{new_content}")
        write_file(self.file_path, self.running_summary)
    
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:14:01 2024

@author: mikeg
"""
import os
import logging
from config import RUNNING_SUMMARY_FILE

# running_summary_manager.py
from file_manager import write_file

class RunningSummaryManager:
    def __init__(self, file_path):
        self.file_path = file_path
        
        
    def get_summary(self):
        # Load the current running summary from a file, or start with an empty string if the file doesn't exist
        if os.path.exists(RUNNING_SUMMARY_FILE):
            with open(RUNNING_SUMMARY_FILE, "r") as file:
                self.running_summary = file.read()
        else:
            # Initialize the running summary content
            self.running_summary = "This is the first call for this project and there is no running summary."
            
            # Create the file and write the initial content
            logging.debug(f"Summary rewrite call. Here it is \n{self.running_summary}")
            with open(RUNNING_SUMMARY_FILE, "w") as file:
                file.write(self.running_summary)
        return self.running_summary

    def update_summary(self, new_content):
        """Append new content to the running summary."""
        self.running_summary = new_content
        logging.debug(f"Update summary call. Here it is \n{self.running_summary}\n here's new content \n{new_content}")
        write_file(self.file_path, self.running_summary)
    