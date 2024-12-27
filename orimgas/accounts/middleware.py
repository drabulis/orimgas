# accounts/middleware.py

import os
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class LogoutLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the user is logged out
        if request.path == '/accounts/logout/' and request.method == 'POST':
            username = request.user.email if request.user.is_authenticated else 'Unknown'
            ip_address = self.get_client_ip(request)
            self.log_user_logout(username, ip_address)

    def log_user_logout(self, username, ip_address):
        # Define the path for the log file in the current directory of this file
        log_file_path = os.path.join(os.path.dirname(__file__), 'user_login.log')
        
        # Create a log message with timestamp
        log_message = f"{timezone.now()} - Vartotojas {username} atsijunge iš IP: {ip_address}\n"
        
        # Append the log message to the file
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_message)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip