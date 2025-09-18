#!/usr/bin/env python3
"""
Test suite for Voice2Care Flask application
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the current directory to Python path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice2care_app import Voice2CareApp, create_app


class TestVoice2CareApp:
    """Test suite for Voice2Care application"""
    
    @pytest.fixture
    def app(self):
        """Create a test app instance"""
        # Set test environment variables
        os.environ['GEMINI_API_KEY'] = 'test_key'
        os.environ['MONGO_USER'] = 'test_user'
        os.environ['MONGO_PASSWORD'] = 'test_password'
        
        # Mock the heavy dependencies
        with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
             patch('voice2care_app.AutoProcessor'), \
             patch('voice2care_app.pipeline'), \
             patch('voice2care_app.MongoClient'):
            
            voice_app = create_app()
            voice_app.app.config['TESTING'] = True
            return voice_app.app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client"""
        return app.test_client()
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'whisper_loaded' in data
        assert 'mongodb_connected' in data
        assert 'gemini_configured' in data
    
    def test_main_page_renders(self, client):
        """Test that the main page renders correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Voice2Care' in response.data
    
    def test_get_audio_endpoint_structure(self, client):
        """Test the structure of the get_audio endpoint"""
        # Test with invalid JSON
        response = client.post('/get_audio', 
                             json={}, 
                             content_type='application/json')
        assert response.status_code == 500  # Should fail without proper audio data
    
    def test_send_json_endpoint_structure(self, client):
        """Test the structure of the send_json endpoint"""
        # Test with sample patient data
        sample_data = {
            "data": "12 Gennaio 2025",
            "cognome_nome": "Test Patient",
            "luogo_intervento": "Test Location"
        }
        
        response = client.post('/send_json',
                             json=sample_data,
                             content_type='application/json')
        assert response.status_code == 200
        assert b'Patient added to the DB successfully!' in response.data


class TestVoice2CareLogic:
    """Test suite for Voice2Care business logic"""
    
    @pytest.fixture
    def voice_app(self):
        """Create a Voice2Care app instance with mocked dependencies"""
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
             patch('voice2care_app.AutoProcessor'), \
             patch('voice2care_app.pipeline'), \
             patch('voice2care_app.MongoClient'):
            
            app = Voice2CareApp()
            return app
    
    def test_mock_ner_response(self, voice_app):
        """Test the mock NER response function"""
        test_text = "Patient has a headache"
        result = voice_app.get_mock_ner_response(test_text)
        
        assert isinstance(result, dict)
        assert 'testo' in result
        assert result['testo'] == test_text
        assert 'data' in result
        assert 'cognome_nome' in result
        assert 'luogo_intervento' in result
    
    @patch('voice2care_app.requests.post')
    def test_refactoring_gemini_success(self, mock_post, voice_app):
        """Test successful Gemini API refactoring"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Refactored text'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        result = voice_app.refactoring_gemini("Original text")
        assert result == "Refactored text"
    
    @patch('voice2care_app.requests.post')
    def test_refactoring_gemini_failure(self, mock_post, voice_app):
        """Test Gemini API refactoring failure handling"""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        original_text = "Original text"
        result = voice_app.refactoring_gemini(original_text)
        assert result == original_text  # Should return original text on failure
    
    def test_refactoring_gemini_no_api_key(self):
        """Test refactoring when no API key is configured"""
        # Create app without API key
        with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
             patch('voice2care_app.AutoProcessor'), \
             patch('voice2care_app.pipeline'), \
             patch('voice2care_app.MongoClient'):
            
            app = Voice2CareApp()
            app.gemini_api_key = None
            
            original_text = "Original text"
            result = app.refactoring_gemini(original_text)
            assert result == original_text
    
    @patch('voice2care_app.requests.post')
    def test_ner_gemini_success(self, mock_post, voice_app):
        """Test successful Gemini NER"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '```json\n{"data": "12 Gennaio 2025", "cognome_nome": "Mario Rossi"}\n```'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        result = voice_app.get_name_entity_recognition_gemini("Test text")
        assert isinstance(result, dict)
        assert result['data'] == "12 Gennaio 2025"
        assert result['cognome_nome'] == "Mario Rossi"
        assert result['testo'] == "Test text"
    
    def test_attach_pdf_no_file(self, voice_app):
        """Test PDF attachment when report.pdf doesn't exist"""
        test_json = {"data": "12 Gennaio 2025"}
        
        # Ensure report.pdf doesn't exist
        if os.path.exists("report.pdf"):
            os.rename("report.pdf", "report.pdf.backup")
        
        try:
            result = voice_app.attach_pdf_to_json(test_json)
            assert result == test_json  # Should return original JSON
        finally:
            # Restore backup if it exists
            if os.path.exists("report.pdf.backup"):
                os.rename("report.pdf.backup", "report.pdf")
    
    def test_speech_to_text_no_model(self, voice_app):
        """Test speech to text when model is not loaded"""
        voice_app.pipe = None
        result = voice_app.speech_to_text()
        assert "Error: Whisper model not loaded" in result


class TestVoice2CareIntegration:
    """Integration tests for Voice2Care"""
    
    @pytest.fixture
    def voice_app_real(self):
        """Create a real Voice2Care app instance for integration testing"""
        # Only run if we have real credentials
        if not all([os.getenv('GEMINI_API_KEY'), os.getenv('MONGO_USER'), os.getenv('MONGO_PASSWORD')]):
            pytest.skip("Real credentials not available for integration testing")
        
        return Voice2CareApp()
    
    def test_full_pipeline_mock(self):
        """Test the full pipeline with mocked external dependencies"""
        with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
             patch('voice2care_app.AutoProcessor'), \
             patch('voice2care_app.pipeline') as mock_pipeline, \
             patch('voice2care_app.MongoClient'), \
             patch('voice2care_app.requests.post') as mock_post:
            
            # Setup mocks
            mock_whisper = Mock()
            mock_whisper.return_value = {"text": "Patient Mario Rossi has a headache"}
            mock_pipeline.return_value = mock_whisper
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'candidates': [{
                    'content': {
                        'parts': [{
                            'text': 'Patient Mario Rossi has a severe headache'
                        }]
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # Set environment
            os.environ['GEMINI_API_KEY'] = 'test_key'
            
            # Create app and test
            app = Voice2CareApp()
            app.pipe = mock_whisper
            
            # Test speech to text
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(b'fake audio data')
                f.flush()
                
                # Copy to expected location
                import shutil
                shutil.copy(f.name, 'audio.mp3')
                
                try:
                    result = app.speech_to_text()
                    assert "Patient Mario Rossi has a headache" in result
                finally:
                    # Cleanup
                    if os.path.exists('audio.mp3'):
                        os.remove('audio.mp3')
                    os.unlink(f.name)


def test_app_creation():
    """Test that the app can be created"""
    with patch('voice2care_app.AutoModelForSpeechSeq2Seq'), \
         patch('voice2care_app.AutoProcessor'), \
         patch('voice2care_app.pipeline'), \
         patch('voice2care_app.MongoClient'):
        
        app = create_app()
        assert app is not None
        assert hasattr(app, 'app')
        assert hasattr(app, 'socketio')


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])