#!/usr/bin/env python3
"""
Simple test script for Voice2Care application
This script provides basic functionality testing without requiring external APIs
"""

import sys
import os
import json
import time
from unittest.mock import patch, Mock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic app functionality with mocked dependencies"""
    print("🧪 Testing Voice2Care Basic Functionality")
    print("=" * 50)
    
    # Mock heavy dependencies
    with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
         patch('voice2care_app.AutoProcessor'), \
         patch('voice2care_app.pipeline'), \
         patch('voice2care_app.MongoClient'):
        
        try:
            from voice2care_app import Voice2CareApp
            print("✅ Successfully imported Voice2CareApp")
        except ImportError as e:
            print(f"❌ Failed to import Voice2CareApp: {e}")
            return False
        
        try:
            # Create app instance
            app = Voice2CareApp()
            print("✅ Successfully created Voice2CareApp instance")
        except Exception as e:
            print(f"❌ Failed to create Voice2CareApp: {e}")
            return False
        
        # Test mock NER response
        try:
            test_text = "Il paziente Mario Rossi ha mal di testa"
            result = app.get_mock_ner_response(test_text)
            assert isinstance(result, dict)
            assert 'testo' in result
            assert result['testo'] == test_text
            print("✅ Mock NER response working correctly")
        except Exception as e:
            print(f"❌ Mock NER response failed: {e}")
            return False
        
        # Test Flask routes (basic structure)
        try:
            client = app.app.test_client()
            
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200
            health_data = json.loads(response.data)
            assert health_data['status'] == 'healthy'
            print("✅ Health check endpoint working")
            
            # Test main page
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Main page endpoint working")
            
        except Exception as e:
            print(f"❌ Flask routes test failed: {e}")
            return False
        
        print("✅ All basic functionality tests passed!")
        return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    # Test environment variable loading
    os.environ['TEST_GEMINI_API_KEY'] = 'test_key_123'
    os.environ['TEST_MONGO_USER'] = 'test_user'
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("⚠️  python-dotenv not available (install with: pip install python-dotenv)")
    
    # Test configuration values
    test_config = {
        'GEMINI_API_KEY': os.getenv('TEST_GEMINI_API_KEY'),
        'MONGO_USER': os.getenv('TEST_MONGO_USER'),
    }
    
    for key, value in test_config.items():
        if value:
            print(f"✅ {key} configuration loaded: {value[:8]}...")
        else:
            print(f"⚠️  {key} not configured")
    
    return True

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing Dependencies")
    print("=" * 25)
    
    required_packages = [
        'flask',
        'flask_socketio', 
        'requests',
        'torch',
        'transformers',
        'scipy',
        'pymongo',
        'PyPDF2',
        'fitz',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements_python.txt")
        return False
    else:
        print("\n✅ All required dependencies available!")
        return True

def test_file_structure():
    """Test required file structure"""
    print("\n📁 Testing File Structure") 
    print("=" * 30)
    
    required_files = [
        'voice2care_app.py',
        'templates/page.html',
        'static/style.css',
        'static/Voice2Care.png',
        'requirements_python.txt',
        '.env.example'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

def main():
    """Run all tests"""
    print("🚀 Voice2Care Application Test Suite")
    print("====================================")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies), 
        ("Configuration", test_configuration),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Voice2Care is ready to run.")
        print("\nTo start the application:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run: python voice2care_app.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)