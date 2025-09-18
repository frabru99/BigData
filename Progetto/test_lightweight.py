#!/usr/bin/env python3
"""
Lightweight test script for Voice2Care application
Tests basic Flask functionality without requiring heavy AI dependencies
"""

import sys
import os
import json
import tempfile
from unittest.mock import patch, Mock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flask_app_basic():
    """Test basic Flask app functionality with all dependencies mocked"""
    print("🧪 Testing Flask App (Mocked Dependencies)")
    print("=" * 50)
    
    # Mock ALL heavy dependencies before importing
    mock_modules = [
        'torch',
        'transformers', 
        'scipy',
        'pymongo',
        'PyPDF2',
        'fitz',
        'ffmpeg',
        'datasets'
    ]
    
    # Create mock modules
    mocks = {}
    for module in mock_modules:
        mocks[module] = Mock()
        sys.modules[module] = mocks[module]
    
    # Mock specific functions that are called
    mocks['torch'].cuda = Mock()
    mocks['torch'].cuda.is_available = Mock(return_value=False)
    mocks['torch'].float32 = 'float32'
    mocks['torch'].float16 = 'float16'
    
    mocks['transformers'].AutoModelForSpeechSeq2Seq = Mock()
    mocks['transformers'].AutoProcessor = Mock()
    mocks['transformers'].pipeline = Mock()
    
    mocks['pymongo'].MongoClient = Mock()
    
    try:
        # Now import our app
        from voice2care_app import Voice2CareApp
        print("✅ Successfully imported Voice2CareApp with mocked dependencies")
        
        # Create app instance
        app = Voice2CareApp()
        print("✅ Successfully created Voice2CareApp instance")
        
        # Test Flask app is created
        assert app.app is not None
        assert app.socketio is not None
        print("✅ Flask app and SocketIO initialized")
        
        # Test basic configuration
        assert hasattr(app, 'gemini_api_key')
        assert hasattr(app, 'mongo_user')
        assert hasattr(app, 'mongo_password')
        print("✅ Configuration attributes exist")
        
        # Test mock NER response
        test_text = "Il paziente Mario Rossi ha mal di testa"
        result = app.get_mock_ner_response(test_text)
        assert isinstance(result, dict)
        assert 'testo' in result
        assert result['testo'] == test_text
        print("✅ Mock NER response working")
        
        # Test Flask test client
        client = app.app.test_client()
        app.app.config['TESTING'] = True
        
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        health_data = json.loads(response.data)
        assert health_data['status'] == 'healthy'
        print("✅ Health endpoint working")
        
        # Test main page
        response = client.get('/')
        assert response.status_code == 200
        assert b'Voice2Care' in response.data or b'html' in response.data
        print("✅ Main page endpoint working")
        
        # Test refactoring with no API key
        app.gemini_api_key = None
        result = app.refactoring_gemini("test text")
        assert result == "test text"
        print("✅ Refactoring fallback working")
        
        # Test NER with no API key
        app.gemini_api_key = None
        result = app.get_name_entity_recognition_gemini("test text")
        assert isinstance(result, dict)
        assert result['testo'] == "test text"
        print("✅ NER fallback working")
        
        print("\n🎉 All Flask functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up mocked modules
        for module in mock_modules:
            if module in sys.modules:
                del sys.modules[module]

def test_template_files():
    """Test that template files are properly structured"""
    print("\n📄 Testing Template Files")
    print("=" * 30)
    
    # Test page.html
    try:
        with open('templates/page.html', 'r') as f:
            content = f.read()
            assert 'Voice2Care' in content
            assert 'socket' in content  # Should have socket.io references
            assert 'audio' in content  # Should have audio functionality
            print("✅ page.html has expected content")
    except Exception as e:
        print(f"❌ page.html test failed: {e}")
        return False
    
    # Test style.css
    try:
        with open('static/style.css', 'r') as f:
            content = f.read()
            assert len(content) > 0
            print("✅ style.css exists and has content")
    except Exception as e:
        print(f"❌ style.css test failed: {e}")
        return False
    
    # Test logo image
    try:
        import os
        size = os.path.getsize('static/Voice2Care.png')
        assert size > 1000  # Should be a reasonable size image
        print(f"✅ Voice2Care.png exists (size: {size} bytes)")
    except Exception as e:
        print(f"❌ Voice2Care.png test failed: {e}")
        return False
    
    return True

def test_configuration_loading():
    """Test configuration and environment variable loading"""
    print("\n🔧 Testing Configuration Loading")
    print("=" * 35)
    
    # Test .env.example exists and has correct format
    try:
        with open('.env.example', 'r') as f:
            content = f.read()
            assert 'GEMINI_API_KEY' in content
            assert 'MONGO_USER' in content
            assert 'MONGO_PASSWORD' in content
            print("✅ .env.example has required variables")
    except Exception as e:
        print(f"❌ .env.example test failed: {e}")
        return False
    
    # Test environment variable loading
    try:
        from dotenv import load_dotenv
        
        # Test with temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("TEST_VAR=test_value\n")
            f.write("GEMINI_API_KEY=test_key\n")
            temp_file = f.name
        
        # Load and test
        load_dotenv(temp_file)
        assert os.getenv('TEST_VAR') == 'test_value'
        print("✅ Environment variable loading working")
        
        # Cleanup
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Environment loading test failed: {e}")
        return False
    
    return True

def test_requirements_file():
    """Test that requirements file is properly formatted"""
    print("\n📦 Testing Requirements File")
    print("=" * 30)
    
    try:
        with open('requirements_python.txt', 'r') as f:
            lines = f.readlines()
            
        # Check for essential packages
        content = ''.join(lines).lower()
        required_packages = ['flask', 'torch', 'transformers', 'pymongo', 'pytest']
        
        missing = []
        for package in required_packages:
            if package not in content:
                missing.append(package)
        
        if missing:
            print(f"❌ Missing packages in requirements: {missing}")
            return False
        
        print(f"✅ Requirements file has {len(lines)} packages including essentials")
        return True
        
    except Exception as e:
        print(f"❌ Requirements file test failed: {e}")
        return False

def main():
    """Run lightweight test suite"""
    print("🚀 Voice2Care Lightweight Test Suite")
    print("=====================================")
    print("(Testing without heavy AI dependencies)")
    
    tests = [
        ("Template Files", test_template_files),
        ("Configuration Loading", test_configuration_loading),
        ("Requirements File", test_requirements_file),
        ("Flask App (Mocked)", test_flask_app_basic),
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
        print("\n🎉 All lightweight tests passed!")
        print("📋 Next steps:")
        print("  1. Install full dependencies: pip install -r requirements_python.txt")
        print("  2. Configure .env file with your API keys")
        print("  3. Run: python run_voice2care.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)