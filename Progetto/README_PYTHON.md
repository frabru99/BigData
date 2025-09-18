# Voice2Care - Python Flask Application

This directory contains the standalone Python version of the Voice2Care application, extracted from the original Jupyter notebook for easier testing and deployment.

## 🐍 Python Version Features

- **Standalone Flask Application**: No need for Jupyter notebook environment
- **Environment-based Configuration**: Uses `.env` files instead of Colab secrets
- **Comprehensive Testing**: Unit tests and integration tests included
- **Easy Deployment**: Can be run on any Python environment
- **Modular Design**: Clean separation of concerns for better maintainability

## 📋 Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (optional, for faster AI processing)
- MongoDB Atlas account (for data storage)
- Google Gemini API key (for AI text processing)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_python.txt
```

### 2. Configure Environment

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
MONGO_USER=your_mongodb_username
MONGO_PASSWORD=your_mongodb_password
```

### 3. Run the Application

**Simple startup:**
```bash
python run_voice2care.py
```

**With automatic dependency installation:**
```bash
python run_voice2care.py --install
```

**With testing:**
```bash
python run_voice2care.py --test
```

**Custom host/port:**
```bash
python run_voice2care.py --host 0.0.0.0 --port 5000
```

### 4. Access the Application

Open your browser and go to: http://localhost:8051

## 🧪 Testing

### Quick Test (No External Dependencies)
```bash
python test_simple.py
```

### Full Test Suite (Requires pytest)
```bash
pytest test_voice2care.py -v
```

### Test Coverage
```bash
pytest test_voice2care.py --cov=voice2care_app
```

## 📁 File Structure

```
.
├── voice2care_app.py          # Main Flask application
├── run_voice2care.py          # Startup script
├── test_voice2care.py         # Comprehensive test suite  
├── test_simple.py             # Simple functionality tests
├── requirements_python.txt    # Python dependencies
├── .env.example              # Environment configuration template
├── templates/
│   └── page.html             # Web interface template
├── static/
│   ├── style.css             # Styling
│   └── Voice2Care.png        # Logo
└── report.pdf                # PDF template (if available)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes (for AI features) |
| `MONGO_USER` | MongoDB Atlas username | Yes (for data storage) |
| `MONGO_PASSWORD` | MongoDB Atlas password | Yes (for data storage) |
| `NGROK_TOKEN` | Ngrok tunnel token | No |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `FLASK_DEBUG` | Enable Flask debug mode | No |

### API Keys Setup

#### Gemini AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

#### MongoDB Atlas
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Create a database user
4. Get connection credentials
5. Add them to your `.env` file

## 🔍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/health` | GET | Health check and status |
| `/get_audio` | POST | Process audio input |
| `/send_json` | POST | Process patient data |

### Health Check Response
```json
{
  "status": "healthy",
  "whisper_loaded": true,
  "mongodb_connected": true,
  "gemini_configured": true
}
```

## 🎯 Testing Features

### Mock Mode
When API keys are not configured, the application runs in mock mode:
- Mock speech recognition results
- Mock AI text processing
- Mock database operations
- Full UI functionality preserved

### Test Scenarios
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Mock Tests**: Testing without external dependencies
- **Configuration Tests**: Environment setup validation

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Install missing dependencies
pip install -r requirements_python.txt
```

**2. CUDA Issues**
```bash
# For CPU-only PyTorch (if GPU issues)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**3. Port Already in Use**
```bash
# Use different port
python run_voice2care.py --port 5000
```

**4. Permission Errors**
```bash
# Make scripts executable
chmod +x run_voice2care.py
chmod +x test_simple.py
```

### Debug Mode
Run with debug enabled to see detailed error messages:
```bash
python run_voice2care.py --test
```

### Log Output
Check console output for detailed information about:
- Model loading status
- API connection status
- Processing pipeline steps
- Error messages

## 🔄 Differences from Notebook Version

| Feature | Notebook Version | Python Version |
|---------|------------------|----------------|
| Configuration | Colab secrets | Environment variables |
| Dependencies | Cell-by-cell install | requirements.txt |
| Testing | Manual | Automated test suite |
| Deployment | Colab-specific | Any Python environment |
| Development | Jupyter cells | Standard Python files |
| Debugging | Print statements | Proper logging + debug mode |

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_python.txt .
RUN pip install -r requirements_python.txt

COPY . .
EXPOSE 8051

CMD ["python", "voice2care_app.py"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8051 "voice2care_app:create_app().app"
```

### Environment Variables for Production
```env
FLASK_ENV=production
FLASK_DEBUG=False
```

## 📞 Support

For issues with the Python version:
1. Check the troubleshooting section above
2. Run the simple test: `python test_simple.py`
3. Check logs for detailed error messages
4. Ensure all environment variables are properly configured

## 🤝 Contributing

When contributing to the Python version:
1. Run tests before submitting: `python test_simple.py`
2. Follow PEP 8 style guidelines
3. Add tests for new features
4. Update documentation as needed