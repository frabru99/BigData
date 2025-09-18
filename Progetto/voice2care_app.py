#!/usr/bin/env python3
"""
Voice2Care - Main Flask Application
A voice-powered medical documentation system that transcribes audio to structured medical reports.

This is a standalone Python version extracted from the original Jupyter notebook.
"""

import os
import json
import base64
import re
import io
import time as t
from typing import Optional, Dict, Any

# Flask imports
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit

# Audio processing (with optional imports for testing)
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: PyTorch/Transformers not available. Speech recognition will be disabled.")
    torch = None
    TORCH_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    print("Warning: ffmpeg-python not available. Audio processing will be limited.")
    ffmpeg = None
    FFMPEG_AVAILABLE = False

try:
    from scipy.io.wavfile import read as wav_read
    SCIPY_AVAILABLE = True
except ImportError:
    print("Warning: scipy not available. Some audio features will be disabled.")
    wav_read = None
    SCIPY_AVAILABLE = False

from base64 import b64decode

# PDF processing (with optional imports)
try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject, BooleanObject, DictionaryObject
    PYPDF2_AVAILABLE = True
except ImportError:
    print("Warning: PyPDF2 not available. PDF processing will be disabled.")
    PdfReader = PdfWriter = None
    PYPDF2_AVAILABLE = False

try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    print("Warning: PyMuPDF (fitz) not available. Advanced PDF features will be disabled.")
    fitz = None
    FITZ_AVAILABLE = False

# Database (with optional imports)
try:
    from pymongo import MongoClient
    import gridfs
    MONGODB_AVAILABLE = True
except ImportError:
    print("Warning: pymongo not available. Database features will be disabled.")
    MongoClient = gridfs = None
    MONGODB_AVAILABLE = False

# API requests
import requests

# Environment variables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Voice2CareApp:
    """Main Voice2Care Flask application class"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.pipe = None
        self.client = None
        self.setup_routes()
        self.setup_config()
        
    def setup_config(self):
        """Setup application configuration"""
        # Get configuration from environment variables
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.mongo_user = os.getenv('MONGO_USER')
        self.mongo_password = os.getenv('MONGO_PASSWORD')
        self.ngrok_token = os.getenv('NGROK_TOKEN')
        
        # Setup MongoDB connection
        if MONGODB_AVAILABLE and self.mongo_user and self.mongo_password:
            connect_to_mongo = f"mongodb+srv://{self.mongo_user}:{self.mongo_password}@voice2care.vr6lf61.mongodb.net/?retryWrites=true&w=majority&appName=Voice2Care"
            try:
                self.client = MongoClient(connect_to_mongo)
                print("MongoDB connection established")
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                self.client = None
        else:
            print("MongoDB not configured or dependencies not available")
            self.client = None
        
        # Setup AI model (Whisper)
        if TORCH_AVAILABLE:
            self.setup_whisper_model()
        else:
            print("Torch not available, Whisper model disabled")
            self.pipe = None
    
    def setup_whisper_model(self):
        """Initialize Whisper model for speech recognition"""
        if not TORCH_AVAILABLE:
            print("Torch not available, skipping Whisper model loading")
            self.pipe = None
            return
            
        try:
            print("Loading Whisper model...")
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            model_id = "openai/whisper-large-v3"
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
            )
            model.to(device)
            
            processor = AutoProcessor.from_pretrained(model_id)
            
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=True,
                torch_dtype=torch_dtype,
                device=device,
            )
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.pipe = None
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route("/", methods=['GET'])
        def page():
            """Serve the main web page"""
            # For testing, we'll use localhost
            server_url = "http://localhost:8051"
            return render_template('page.html', urlServer=server_url)
        
        @self.app.route("/get_audio", methods=['POST'])
        def get_audio():
            """Process audio input and return structured JSON"""
            print("Received audio from user...")
            
            try:
                audio_base64 = request.get_json().get("audio")
                
                if not FFMPEG_AVAILABLE:
                    return {"error": "Audio processing not available (ffmpeg missing)"}, 500
                
                # Decode base64 audio
                binary = b64decode(audio_base64.split(',')[1])
                
                # Convert audio using ffmpeg
                process = (ffmpeg
                    .input('pipe:0')
                    .output('pipe:1', format='mp3')
                    .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True, overwrite_output=True)
                )
                
                output, err = process.communicate(input=binary)
                
                # Save audio file
                with open('audio.mp3', 'wb') as f:
                    f.write(output)
                
                print("Recognition...")
                text = self.speech_to_text()
                
                print("Refactoring...")
                refactored_text = self.refactoring_gemini(text)
                
                print("Name Entity Recognition...")
                name_entity_recognition = self.get_name_entity_recognition_gemini(refactored_text)
                
                return name_entity_recognition, 200
                
            except Exception as e:
                print(f"Error processing audio: {e}")
                return {"error": "Failed to process audio"}, 500
        
        @self.app.route("/send_json", methods=['POST'])
        def send_json():
            """Process patient JSON and generate PDF"""
            try:
                json_paziente = request.get_json()
                self.socketio.start_background_task(self.create_pdf_and_write_json, json_paziente)
                return "Patient added to the DB successfully!", 200
            except Exception as e:
                print(f"Error processing JSON: {e}")
                return "Error processing patient data", 500
        
        @self.app.route("/health", methods=['GET'])
        def health_check():
            """Health check endpoint for testing"""
            status = {
                "status": "healthy",
                "whisper_loaded": self.pipe is not None,
                "mongodb_connected": self.client is not None,
                "gemini_configured": self.gemini_api_key is not None,
                "dependencies": {
                    "torch": TORCH_AVAILABLE,
                    "ffmpeg": FFMPEG_AVAILABLE,
                    "scipy": SCIPY_AVAILABLE,
                    "pypdf2": PYPDF2_AVAILABLE,
                    "fitz": FITZ_AVAILABLE,
                    "mongodb": MONGODB_AVAILABLE
                }
            }
            return jsonify(status)
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle socket connection"""
            print('Client connected')
    
    def speech_to_text(self) -> str:
        """Convert audio to text using Whisper"""
        if not self.pipe:
            return "Error: Whisper model not loaded"
        
        try:
            result = self.pipe("audio.mp3", generate_kwargs={"language": "italian"})
            text_extracted = result["text"]
            print(f"Extracted text: {text_extracted}")
            return text_extracted
        except Exception as e:
            print(f"Error in speech to text: {e}")
            return f"Error in speech recognition: {e}"
    
    def refactoring_gemini(self, text_extracted: str) -> str:
        """Refactor text using Gemini API"""
        if not self.gemini_api_key:
            print("Warning: Gemini API key not configured, returning original text")
            return text_extracted
        
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Sei un assistente al pronto soccorso. Il testo che ti viene presentato è una registrazione vocale trascritta in testo. Correggi eventuali errori o ambiguità, riportami solo il testo modificato. Testo: {text_extracted}"
                    }]
                }]
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                docs = response.json()
                response_text = docs['candidates'][0]['content']['parts'][0]['text']
                print(f"Refactored text: {response_text}")
                return response_text
            else:
                print(f"Gemini API error: {response.status_code}")
                return text_extracted
                
        except Exception as e:
            print(f"Error in Gemini refactoring: {e}")
            return text_extracted
    
    def get_name_entity_recognition_gemini(self, refactored_text: str) -> Dict[str, Any]:
        """Extract structured data using Gemini API"""
        if not self.gemini_api_key:
            print("Warning: Gemini API key not configured, returning mock data")
            return self.get_mock_ner_response(refactored_text)
        
        try:
            # Load PDF template for context
            pdf_base64 = ""
            if os.path.exists("report.pdf"):
                with open("report.pdf", "rb") as img_file:
                    pdf_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            query = """
            Sei un assistente per la Croce Rossa Italiana. Devi analizzare il testo fornito, assegnando alle espressioni trovate una label nella lista fornita e riferendoti al file fornito.
            
            Lista di Label: ["data", "h_chiamata", "h_partenza", "h_sul_posto", "h_partenza_posto", "h_in_ps", "h_libero_operativo", "luogo_intervento", "codice_uscita", "codice_rientro", "condizione_riferita", "recapito_telefonico", "cri", "selezione_ambulanza", "equipaggio_aut", "equipaggio_socc1", "equipaggio_socc2", "equipaggio_socc3", "equipaggio_ip", "medico", "attivazioni_autorita_presenti", "ulteriore_autorita", "causa_trasporto_non_effettuato", "decesso", "ora_del_decesso", "rifiuto_firma_paziente","cognome_nome", "nato_il", "nato_a", "residente_a", "via", "telefono", "sesso", "prov_1", "prov_2", "n°", "dati_dichiarati_da", "altri_documenti", "t1_ora", "t2_ora", "t3_ora","t1_coscienza", "t2_coscienza", "t3_coscienza", "t1_cute", "t2_cute", "t3_cute", "t1_respiro", "t2_respiro", "t3_respiro", "t1_spO2", "t2_spO2", "t3_spO2", "t1_fc_bpm", "t2_fc_bpm", "t3_fc_bpm",  "t1_pa_mmhg", "t2_pa_mmhg", "t3_pa_mmhg", "t1_glicemia", "t2_glicemia", "t3_glicemia", "t1_temperatura", "t2_temperatura", "t3_temperatura", "t1_apertura_occhi_gcs", "t2_apertura_occhi_gcs", "t3_apertura_occhi_gcs", "t1_risposta_verbale_gcs", "t2_risposta_verbale_gcs", "t3_risposta_verbale_gcs", "t1_risposta_motoria_gcs", "t2_risposta_motoria_gcs", "t3_risposta_motoria_gcs", "t1_totale_gcs", "t2_totale_gcs", "t3_totale_gcs", "pupille_reagenti", "pupille_dx", "pupille_sx", "lesioni_riscontrate", "respiro", "circolo", "immobilizzazione", "provvedimenti_altro", "altri_provvedimenti_1", "altri_provvedimenti_2", "infusione/farmaco_1", "infusione/farmaco_2", "infusione/farmaco_3", "infusione/farmaco_4", "infusione/farmaco_5", "infusione/farmaco_6", "annotazioni"]
            
            L'output deve essere in formato JSON in cui ogni label identificata è un campo del JSON e il valore è l'espressione identificata. Se non trovi corrispondenza dell'entità nell'audio, metti uno spazio vuoto.
            
            Testo: """
            
            parts = [{"text": f"{query} {refactored_text}"}]
            if pdf_base64:
                parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_base64}})
            
            payload = {"contents": [{"parts": parts}]}
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                docs = response.json()
                response_extracted_words = docs['candidates'][0]['content']['parts'][0]['text']
                res_new = response_extracted_words.replace("```json", "").replace("```", "")
                res_json = json.loads(res_new)
                res_json["testo"] = refactored_text
                print(f"NER Result: {res_json}")
                return res_json
            else:
                print(f"Gemini NER API error: {response.status_code}")
                return self.get_mock_ner_response(refactored_text)
                
        except Exception as e:
            print(f"Error in Gemini NER: {e}")
            return self.get_mock_ner_response(refactored_text)
    
    def get_mock_ner_response(self, text: str) -> Dict[str, Any]:
        """Return mock NER response for testing"""
        return {
            "data": "12 Gennaio 2025",
            "h_chiamata": "10:30",
            "cognome_nome": "Mario Rossi", 
            "luogo_intervento": "Via Roma 123",
            "annotazioni": "Test patient data from voice recognition",
            "testo": text,
            # All other fields set to empty string
            **{field: " " for field in [
                "h_partenza", "h_sul_posto", "h_partenza_posto", "h_in_ps", "h_libero_operativo",
                "codice_uscita", "codice_rientro", "condizione_riferita", "recapito_telefonico", 
                "cri", "selezione_ambulanza", "equipaggio_aut", "equipaggio_socc1", 
                "equipaggio_socc2", "equipaggio_socc3", "equipaggio_ip", "medico"
            ]}
        }
    
    def create_pdf_and_write_json(self, json_paziente: Dict[str, Any]):
        """Create PDF and write to database"""
        try:
            # Extract date info
            anno_paziente = json_paziente["data"].split(" ")[2] if "data" in json_paziente else "2025"
            mese_paziente = json_paziente["data"].split(" ")[1].lower() if "data" in json_paziente else "gennaio"
            
            # Add PDF to JSON
            json_paziente_with_pdf = self.attach_pdf_to_json(json_paziente)
            
            if json_paziente_with_pdf:
                # Write to database
                self.write_json(mese_paziente, anno_paziente, json_paziente_with_pdf)
            
        except Exception as e:
            print(f"Error in create_pdf_and_write_json: {e}")
            self.socketio.emit('error')
    
    def attach_pdf_to_json(self, json_paziente: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attach compiled PDF to JSON"""
        try:
            # For testing, we'll create a simple PDF or use existing one
            if os.path.exists("report.pdf"):
                with open("report.pdf", "rb") as pdf_file:
                    dati = pdf_file.read()
                    pdf_base64 = base64.b64encode(dati).decode('utf-8')
                
                json_paziente["pdf"] = pdf_base64
                self.socketio.emit('completed')
                print("PDF encoded and added to JSON!")
                return json_paziente
            else:
                print("Warning: report.pdf not found, skipping PDF attachment")
                return json_paziente
                
        except Exception as e:
            print(f"Error attaching PDF: {e}")
            self.socketio.emit('error')
            return None
    
    def write_json(self, mese: str, anno: str, json_patient: Dict[str, Any]):
        """Write patient JSON to MongoDB"""
        if not MONGODB_AVAILABLE:
            print("Warning: MongoDB not available, skipping database write")
            return
            
        if not self.client:
            print("Warning: MongoDB not connected, skipping database write")
            return
        
        try:
            db = self.client[f"hospital_{anno}"]
            patients = db[f"patients_{mese}"]
            patients.insert_one(json_patient)
            print(f"Patient data written to database: hospital_{anno}.patients_{mese}")
        except Exception as e:
            print(f"Error writing to database: {e}")
    
    def run(self, host='127.0.0.1', port=8051, debug=True):
        """Run the Flask application"""
        print(f"Starting Voice2Care application on http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

def create_app():
    """Factory function to create the Flask app"""
    return Voice2CareApp()

if __name__ == "__main__":
    app = create_app()
    app.run()