from flask import session, request
from datetime import timedelta
import logging
import uuid
import hashlib
from config import ALLOWABLE_PROJECT_TYPES

class UserManagement:
    def __init__(self, app):
        self.app = app
        self.setup_session_config()
        
        # Ensure the app has a secret key
        if not app.secret_key:
            logging.warning("No app.secret_key set. Using a random key (not suitable for production)")
            app.secret_key = uuid.uuid4().hex

    def setup_session_config(self):
        """Configure session settings"""
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_FILE_DIR'] = './flask_session_data'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.permanent_session_lifetime = timedelta(days=1)

    def _generate_fingerprint(self):
        """Generate a digital fingerprint from request data"""
        fingerprint_data = {
            'user_agent': request.headers.get('User-Agent', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'ip': request.remote_addr,
            # Add more fingerprint components as needed
        }
        
        # Create a unique fingerprint hash
        fingerprint_string = '|'.join(str(v) for v in fingerprint_data.values())
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def ensure_user_session(self):
        """Ensure that a user session is established."""
        if 'user' not in session:
            unique_id = self._generate_user_id()
            fingerprint = self._generate_fingerprint()
            
            # Setup initial session data structure
            session['user'] = {
                'username': unique_id,
                'is_authenticated': True,
                'fingerprint': fingerprint,
                'secret_key': None,  # Will be set when user provides it
                'portfolio': {
                    'projects': []
                }
            }
            
            session['current_project'] = {
                'name': None,
                'type': None,
                'metadata': None
            }
            
            session['application'] = {
                'available_project_types': ALLOWABLE_PROJECT_TYPES,
                'is_initialized': False
            }
            
            session.permanent = True
            logging.debug(f"Created new session for user: {unique_id}")
        else:
            # Verify fingerprint on each request
            current_fingerprint = self._generate_fingerprint()
            stored_fingerprint = session['user'].get('fingerprint')
            
            if stored_fingerprint and stored_fingerprint != current_fingerprint:
                logging.warning(f"Fingerprint mismatch for user: {session['user'].get('username')}")
                # For now, just log the mismatch. Later you can add more security measures

    def set_user_secret_key(self, secret_key):
        """Set or update the user's secret key"""
        if 'user' in session:
            session['user']['secret_key'] = secret_key
            logging.debug(f"Updated secret key for user: {session['user'].get('username')}")
            return True
        return False

    def get_user_fingerprint(self):
        """Get the current user's digital fingerprint"""
        if 'user' in session:
            return session['user'].get('fingerprint')
        return None

    def _generate_user_id(self):
        """Generate a unique user ID"""
        return str(uuid.uuid4())

    def get_current_user(self):
        """Get current user information"""
        return session.get('user', {})

    def get_current_project(self):
        """Get current project information"""
        return session.get('current_project', {})

    def validate_user_session(self):
        """Validate user session exists and is properly formatted"""
        if 'user' not in session:
            return False
        if 'username' not in session['user']:
            return False
        if 'is_authenticated' not in session['user']:
            return False
        if 'fingerprint' not in session['user']:
            return False
        return True