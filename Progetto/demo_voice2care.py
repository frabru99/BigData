#!/usr/bin/env python3
"""
Voice2Care Demo Script
This script demonstrates the key functionality of the Voice2Care application
"""

import json
import sys
import os
from unittest.mock import patch, Mock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_health_check():
    """Demo the health check functionality"""
    print("🏥 Voice2Care Health Check Demo")
    print("=" * 40)
    
    try:
        from voice2care_app import create_app
        
        app = create_app()
        client = app.app.test_client()
        app.app.config['TESTING'] = True
        
        response = client.get('/health')
        health_data = json.loads(response.data)
        
        print("📊 System Status:")
        print(f"  Overall Status: {health_data['status']}")
        print(f"  Whisper Model: {'✅ Loaded' if health_data['whisper_loaded'] else '❌ Not Loaded'}")
        print(f"  MongoDB: {'✅ Connected' if health_data['mongodb_connected'] else '❌ Not Connected'}")
        print(f"  Gemini API: {'✅ Configured' if health_data['gemini_configured'] else '❌ Not Configured'}")
        
        print("\n🔧 Dependencies:")
        for dep, available in health_data['dependencies'].items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"  {dep}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def demo_mock_processing():
    """Demo the mock AI processing functionality"""
    print("\n🤖 Voice2Care AI Processing Demo (Mock Mode)")
    print("=" * 50)
    
    try:
        from voice2care_app import create_app
        
        app = create_app()
        
        # Demo text processing
        test_text = "Il paziente Mario Rossi, nato il 15 marzo 1980, residente a Roma in Via Nazionale 123, ha chiamato per mal di testa e febbre alta. Pressione arteriosa 140/90, frequenza cardiaca 95 bpm."
        
        print(f"📝 Input text: {test_text[:100]}...")
        
        # Demo refactoring (fallback mode)
        refactored = app.refactoring_gemini(test_text)
        print(f"🔄 Refactored: {refactored[:100]}...")
        
        # Demo NER extraction
        ner_result = app.get_name_entity_recognition_gemini(refactored)
        
        print("\n📋 Extracted Information:")
        important_fields = ['data', 'cognome_nome', 'luogo_intervento', 'annotazioni']
        for field in important_fields:
            if field in ner_result and ner_result[field].strip():
                print(f"  {field}: {ner_result[field]}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI processing demo failed: {e}")
        return False

def demo_flask_endpoints():
    """Demo the Flask web endpoints"""
    print("\n🌐 Voice2Care Web Endpoints Demo")
    print("=" * 40)
    
    try:
        from voice2care_app import create_app
        
        app = create_app()
        client = app.app.test_client()
        app.app.config['TESTING'] = True
        
        # Test main page
        response = client.get('/')
        print(f"📄 Main page (GET /): {response.status_code}")
        
        # Test health endpoint  
        response = client.get('/health')
        print(f"🔍 Health check (GET /health): {response.status_code}")
        
        # Test JSON processing endpoint (with mock data)
        mock_patient_data = {
            "data": "12 Gennaio 2025",
            "cognome_nome": "Mario Rossi",
            "luogo_intervento": "Via Roma 123, Roma",
            "annotazioni": "Paziente con mal di testa e febbre"
        }
        
        response = client.post('/send_json', 
                             json=mock_patient_data,
                             content_type='application/json')
        print(f"💾 JSON processing (POST /send_json): {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask endpoints demo failed: {e}")
        return False

def demo_configuration():
    """Demo configuration options"""
    print("\n⚙️ Voice2Care Configuration Demo")
    print("=" * 40)
    
    # Show environment variable configuration
    print("📋 Environment Variables:")
    env_vars = ['GEMINI_API_KEY', 'MONGO_USER', 'MONGO_PASSWORD', 'FLASK_ENV']
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        display_value = value[:10] + '...' if len(value) > 10 else value
        print(f"  {var}: {display_value}")
    
    # Show .env file example
    if os.path.exists('.env.example'):
        print("\n📄 Configuration template (.env.example) found:")
        with open('.env.example', 'r') as f:
            lines = f.readlines()[:5]  # Show first 5 lines
            for line in lines:
                if line.strip():
                    print(f"  {line.strip()}")
        if len(lines) == 5:
            print("  ...")
    
    return True

def main():
    """Run the complete demo"""
    print("🚀 Voice2Care Application Demo")
    print("==============================")
    print("This demo shows the Voice2Care application running in test mode")
    print("with all external dependencies mocked for demonstration purposes.\n")
    
    demos = [
        ("Health Check", demo_health_check),
        ("Configuration", demo_configuration),
        ("Flask Endpoints", demo_flask_endpoints), 
        ("AI Processing (Mock)", demo_mock_processing),
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Demo Results Summary")  
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status} - {demo_name}")
    
    print(f"\nTotal: {passed}/{total} demos successful")
    
    if passed == total:
        print("\n🎉 All demos completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Install full dependencies: pip install -r requirements_python.txt")
        print("2. Configure your API keys in .env file")
        print("3. Start the application: python run_voice2care.py")
        print("4. Access the web interface at: http://localhost:8051")
    else:
        print(f"\n⚠️  {total - passed} demos failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)