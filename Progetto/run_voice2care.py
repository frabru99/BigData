#!/usr/bin/env python3
"""
Voice2Care Application Startup Script
This script helps set up and run the Voice2Care Flask application
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        # Try importing key packages
        import flask
        import torch
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install dependencies with:")
        print("pip install -r requirements_python.txt")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("⚠️  .env file not found. Creating from .env.example...")
            import shutil
            shutil.copy('.env.example', '.env')
            print("📋 Please edit .env file with your actual API keys")
        else:
            print("❌ Neither .env nor .env.example found")
            return False
    
    # Load and check environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        mongo_user = os.getenv('MONGO_USER')
        mongo_password = os.getenv('MONGO_PASSWORD')
        
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            print("✅ Gemini API key configured")
        else:
            print("⚠️  Gemini API key not configured (AI features will use mock data)")
        
        if mongo_user and mongo_user != 'your_mongo_username':
            print("✅ MongoDB credentials configured")
        else:
            print("⚠️  MongoDB credentials not configured (data won't be saved)")
        
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def install_dependencies():
    """Install dependencies from requirements file"""
    print("\n📥 Installing dependencies...")
    
    requirements_file = 'requirements_python.txt'
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    
    if os.path.exists('test_simple.py'):
        try:
            result = subprocess.run([sys.executable, 'test_simple.py'], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Failed to run tests: {e}")
            return False
    else:
        print("⚠️  test_simple.py not found, skipping tests")
        return True

def start_application(host='127.0.0.1', port=8051, debug=True):
    """Start the Voice2Care application"""
    print(f"\n🚀 Starting Voice2Care application on http://{host}:{port}")
    print("Press Ctrl+C to stop the application")
    
    try:
        from voice2care_app import create_app
        app = create_app()
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='Voice2Care Application Startup')
    parser.add_argument('--install', action='store_true', 
                       help='Install dependencies before starting')
    parser.add_argument('--test', action='store_true',
                       help='Run tests before starting')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8051,
                       help='Port to bind to (default: 8051)')
    parser.add_argument('--no-debug', action='store_true',
                       help='Disable debug mode')
    
    args = parser.parse_args()
    
    print("🏥 Voice2Care Application Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install:
        if not install_dependencies():
            sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nTry running with --install to install dependencies")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run tests if requested
    if args.test:
        if not run_tests():
            print("❌ Tests failed. Fix issues before starting application.")
            sys.exit(1)
        print("✅ All tests passed!")
    
    # Start application
    try:
        start_application(
            host=args.host,
            port=args.port,
            debug=not args.no_debug
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()