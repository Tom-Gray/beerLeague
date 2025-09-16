#!/usr/bin/env python3
"""
Yahoo Fantasy API Authentication Setup Guide

This script helps you set up Yahoo Developer credentials for the fantasy data extractor.
"""

import os
import webbrowser
from pathlib import Path

def create_yahoo_app_guide():
    """Display step-by-step instructions for creating a Yahoo Developer app."""
    
    print("=" * 60)
    print("YAHOO FANTASY API SETUP GUIDE")
    print("=" * 60)
    print()
    
    print("Follow these steps to set up Yahoo Developer credentials:")
    print()
    
    print("1. Go to Yahoo Developer Console:")
    print("   https://developer.yahoo.com/apps/")
    print()
    
    print("2. Sign in with your Yahoo account")
    print()
    
    print("3. Click 'Create an App'")
    print()
    
    print("4. Fill out the application form:")
    print("   - Application Name: 'Fantasy League Stats Extractor' (or any name)")
    print("   - Application Type: 'Web Application'")
    print("   - Description: 'Extract historical fantasy league data'")
    print("   - Home Page URL: 'http://localhost:8080'")
    print("   - Redirect URI(s): 'http://localhost:8080'")
    print("   - API Permissions: Check 'Fantasy Sports' and 'Read'")
    print()
    
    print("5. After creating the app, you'll get:")
    print("   - Client ID")
    print("   - Client Secret")
    print()
    
    print("6. Copy these credentials and run the setup:")
    print("   python setup_auth.py --configure")
    print()
    
    # Ask if user wants to open the URL
    response = input("Would you like to open the Yahoo Developer Console now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        webbrowser.open('https://developer.yahoo.com/apps/')
        print("Opening Yahoo Developer Console in your browser...")

def configure_credentials():
    """Interactive setup for Yahoo API credentials."""
    
    print("=" * 60)
    print("CONFIGURE YAHOO API CREDENTIALS")
    print("=" * 60)
    print()
    
    # Get credentials from user
    client_id = input("Enter your Yahoo Client ID: ").strip()
    client_secret = input("Enter your Yahoo Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Error: Both Client ID and Client Secret are required!")
        return False
    
    # Create .env file
    env_path = Path(__file__).parent / '.env'
    
    env_content = f"""# Yahoo Fantasy API Credentials
YAHOO_CLIENT_ID={client_id}
YAHOO_CLIENT_SECRET={client_secret}

# League Configuration
LEAGUE_ID=848590
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Credentials saved to {env_path}")
        print("\nYou can now run the main extractor:")
        print("   python main.py")
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving credentials: {e}")
        return False

def main():
    """Main setup function."""
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--configure':
        configure_credentials()
    else:
        create_yahoo_app_guide()

if __name__ == '__main__':
    main()
