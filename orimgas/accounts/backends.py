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
    log_message = f"{timezone.now()} - Vartotojas {username} prisijungė iš IP: {ip_address}\n"
    
    # Append the log message to the file
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Get the user's real IP address
        ip_address = self.get_client_ip(request)
        
        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        if user is not None:
            # Log successful login
            log_user_activity(username, ip_address, "logged in")
            return user
        else:
            # Log failed login attempt
            log_user_activity(username, ip_address, "failed to log in")
            return None

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip