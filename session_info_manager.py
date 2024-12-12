# -*- coding: utf-8 -*-
"""
Created on Wed Nov 6 12:09:12 2024

@author: mikeg
"""

import os
import logging
from datetime import datetime
from config import SESSION_LOG_FOLDER

class SessionInfoManager:
    def __init__(self):
        """Initialize the session info manager with a log directory path"""
        self.session_log_path = SESSION_LOG_FOLDER
        self.current_log_file = None
        self._initialize_session()

    def _initialize_session(self):
        """Create session log directory and file"""
        # Create logs directory if it doesn't exist
        os.makedirs(self.session_log_path, exist_ok=True)

        # Create new log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = os.path.join(self.session_log_path, f"session_{timestamp}.txt")

        # Write session start entry
        self.add_to_session_log("SESSION_START", f"New session started at {datetime.now()}")

    def add_to_session_log(self, function_name, message, log_type="INFO"):
        """Add an entry to the session log file"""
        if not self.current_log_file:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {log_type} - {function_name}: {message}\n"

        try:
            with open(self.current_log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Failed to write to session log: {e}")

    def close_session(self):
        """Close the current session with final log entry"""
        if self.current_log_file:
            self.add_to_session_log("SESSION_END", f"Session ended at {datetime.now()}")
            self.current_log_file = None

    def get_current_log_path(self):
        """Return the path of the current session log file"""
        return self.current_log_file
