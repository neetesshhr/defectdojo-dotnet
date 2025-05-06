#!/usr/bin/env python

"""
Patch for DefectDojo API to fix the '>' not supported between instances of 'list' and 'int' error
"""

import sys
import os
from importlib import import_module
import inspect
import types

def patch_defectdojo_api():
    """
    Apply a monkey patch to fix the defectdojo_api module's host handling
    """
    # Try to import the module
    try:
        from defectdojo_api import defectdojo
    except ImportError:
        print("DefectDojo API module not found. Make sure it's installed.")
        return False

    # Define the patched __init__ method
    def patched_init(self, host, api_key, user, verify_ssl=True, timeout=30, proxies=None, user_agent=None, cert=None, debug=False):
        """
        Initialize the DefectDojo API client with patched host parsing
        """
        self.host = host
        self.api_key = api_key
        self.user = user
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self.timeout = timeout
        self.user_agent = user_agent
        self.cert = cert
        self.debug = debug

        # Fix the host URL format if necessary
        if not self.host.endswith('/'):
            self.host = self.host + '/'
            
        # Check if the host already has the '/api/v2/' endpoint
        # Replace the problematic list comparison that was causing the TypeError
        host_parts = self.host.split('/')
        if 'api' not in host_parts and 'v2' not in host_parts:
            self.host = self.host + 'api/v2/'

    # Apply the patch to the class
    defectdojo.DefectDojoAPI.__init__ = patched_init
    
    print("DefectDojo API has been patched successfully")
    return True

if __name__ == "__main__":
    patch_defectdojo_api()