# accounts/backends.py

import os
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def log_user_activity(username, ip_address, action):
    # Define the path for the log file in the current directory of this file
    log_file_path = os.path.join(os.path.dirname(__file__), 'user_login.log')
    
    # Create a log message with timestamp
    log_message = f"{timezone.now()} - User {username} {action} from IP: {ip_address}\n"
    
    # Append the log message to the file
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')
        
        # Print statement for debugging

        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        if user is not None:
            # Log successful login
            log_user_activity(username, ip_address, "logged in")
            return user
        else:
            # Log failed login attempt
            log_user_activity(username, ip_address, "failed to log in")
            return None

