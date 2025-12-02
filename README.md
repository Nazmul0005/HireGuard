# AI-Powered HR Assistant

<div align="center">

**A sophisticated, enterprise-grade HR assistant system that revolutionizes recruitment and employee management**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)]()

</div>

## 📋 Overview

This AI-powered HR assistant combines cutting-edge artificial intelligence, biometric verification, and intelligent document processing to streamline HR operations. Built with enterprise scalability in mind, it provides a comprehensive solution for resume screening, candidate verification, and intelligent HR query handling.

### Key Capabilities

- **🤖 Intelligent Conversational AI**: Context-aware chatbot powered by OpenAI's GPT models for natural HR interactions
- **📄 Automated Resume Processing**: Extract, analyze, and categorize candidate information with high accuracy
- **🔐 Biometric Verification**: Secure face verification using Face++ API for identity authentication
- **🔍 Smart Knowledge Retrieval**: FAISS-powered vector search for instant access to HR policies and documentation
- **🚀 Production-Ready**: Containerized architecture with Nginx for scalable, enterprise deployment
- **💾 Robust Data Management**: MongoDB integration for secure storage of verification records and user profiles
- **🔌 RESTful Architecture**: Clean, well-documented API endpoints for seamless integration

## 🏗️ Architecture

```
┌─────────────────┐
│   Nginx Proxy   │
└────────┬────────┘
         │
┌────────▼────────────────────────────┐
│         FastAPI Application         │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │   Chatbot Service (GPT-5)    │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │   Resume Processing Engine   │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Face Verification (Face++)  │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │   FAISS Knowledge Base       │  │
│  └──────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
      ┌───────▼────────┐
      │    MongoDB     │
      └────────────────┘
```

## 🎯 Use Cases

- **Recruitment Automation**: Screen hundreds of resumes in minutes
- **Identity Verification**: Verify candidate identity during virtual interviews
- **HR Query Management**: Instant answers to policy and procedure questions
- **Onboarding Support**: Guide new employees through documentation and processes
- **Compliance Tracking**: Maintain verification records for audit purposes

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed and configured:

- **Python**: Version 3.12 or higher
- **Docker**: Latest stable version
- **Docker Compose**: Version 2.0+
- **API Credentials**:
  - OpenAI API key with GPT-5 access
  - Face++ API key and secret
  - MongoDB connection URI

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ai-hr-assistant
   ```

2. **Configure Environment Variables**
   
   Create a `.env` file in the project root:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-openai-api-key
   MODEL=gpt-5
   
   # Face++ Configuration
   API_KEY=your-faceplus-api-key
   API_SECRET=your-faceplus-secret
   
   # Database Configuration
   MONGODB_URI=mongodb://username:password@localhost:27017/hr_assistant
   
   # Application Configuration
   APP_HOST=0.0.0.0
   APP_PORT=8000
   LOG_LEVEL=INFO
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Knowledge Base**
   
   Place your HR documents (policies, procedures, FAQs) in the knowledge base directory:
   ```bash
   mkdir -p data/knowledge_base
   # Copy your documents to data/knowledge_base/
   ```

5. **Build Knowledge Base Index**
   ```bash
   python ingest.py
   ```
   
   This creates FAISS vector indices for efficient document retrieval.

## 🖥️ Running the Application

### Development Mode

For local development with hot-reload:

```bash
uvicorn com.mhire.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application at `http://localhost:8000`

### Production Deployment

Deploy using Docker Compose for production environments:

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Production endpoint: `http://localhost:3014`

### Health Check

Verify the application is running:
```bash
curl http://localhost:8000/health
```

## 📚 API Documentation

### Interactive Documentation

Once running, access comprehensive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Chatbot Interface
```http
POST /chat
Content-Type: application/json

{
  "message": "What is the company's leave policy?",
  "session_id": "user-123"
}
```

#### Resume Processing
```http
POST /resume
Content-Type: multipart/form-data

file: resume.pdf
```

#### Face Verification
```http
POST /face-verification
Content-Type: multipart/form-data

image: photo.jpg
user_id: "candidate-456"
```

#### User Verification
```http
GET /verification/{user_id}
```

### Response Format

All endpoints return JSON responses with consistent structure:
```json
{
  "status": "success",
  "data": { /* response data */ },
  "message": "Operation completed successfully"
}
```

## 📁 Project Structure

```
ai-hr-assistant/
│
├── com/mhire/app/
│   ├── main.py                    # FastAPI application & routing
│   ├── config/
│   │   └── settings.py            # Configuration management
│   ├── database/
│   │   └── mongodb.py             # Database connection handler
│   ├── models/
│   │   ├── chat.py                # Chat data models
│   │   ├── resume.py              # Resume data models
│   │   └── verification.py        # Verification data models
│   └── services/
│       ├── chatbot/
│       │   ├── chain.py           # LangChain conversation chain
│       │   └── prompts.py         # System prompts
│       ├── resume/
│       │   ├── parser.py          # Resume parsing logic
│       │   └── analyzer.py        # Resume analysis
│       ├── verification/
│       │   └── handler.py         # User verification logic
│       └── verification_system/
│           └── face_verification/
│               ├── detector.py    # Face detection
│               └── comparator.py  # Face comparison
│
├── data/
│   └── knowledge_base/            # HR documents & policies
│
├── faiss_index/                   # Vector store indices (generated)
│
├── nginx/
│   └── nginx.conf                 # Nginx configuration
│
├── tests/                         # Unit & integration tests
│   ├── test_chatbot.py
│   ├── test_resume.py
│   └── test_verification.py
│
├── docker-compose.yml             # Multi-container orchestration
├── Dockerfile                     # Container image definition
├── requirements.txt               # Python dependencies
├── ingest.py                      # Knowledge base indexing script
├── .env.example                   # Example environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🛠️ Technology Stack

### Core Framework
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance async web framework
- **[Uvicorn](https://www.uvicorn.org/)**: Lightning-fast ASGI server

### AI & Machine Learning
- **[OpenAI GPT-5](https://openai.com/)**: State-of-the-art language understanding
- **[LangChain](https://www.langchain.com/)**: LLM application framework
- **[FAISS](https://github.com/facebookresearch/faiss)**: Efficient similarity search (Facebook AI)

### Biometric & Verification
- **[Face++](https://www.faceplusplus.com/)**: Enterprise face detection and recognition

### Data & Storage
- **[MongoDB](https://www.mongodb.com/)**: Document-oriented database
- **[PyMongo](https://pymongo.readthedocs.io/)**: MongoDB driver for Python

### Infrastructure
- **[Docker](https://www.docker.com/)**: Containerization platform
- **[Nginx](https://nginx.org/)**: Reverse proxy and load balancer

## 🔒 Security & Compliance

### Data Protection
- All sensitive credentials stored in environment variables
- API keys never committed to version control
- MongoDB authentication enforced
- HTTPS recommended for production deployments

### Biometric Data
- Face verification data encrypted at rest
- Temporary face images deleted after processing
- Compliance with GDPR and CCPA regulations

### Access Control
- API key authentication for all endpoints
- Rate limiting configured in Nginx
- Session management for chatbot conversations

### Best Practices
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use strong MongoDB passwords
# Rotate API keys regularly
# Enable MongoDB encryption at rest
# Configure HTTPS with valid SSL certificates
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=com.mhire.app --cov-report=html

# Run specific test file
pytest tests/test_chatbot.py -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication key | ✅ | - |
| `MODEL` | OpenAI model identifier | ✅ | `gpt-5` |
| `API_KEY` | Face++ API key | ✅ | - |
| `API_SECRET` | Face++ API secret | ✅ | - |
| `MONGODB_URI` | MongoDB connection string | ✅ | - |
| `APP_HOST` | Application host | ❌ | `0.0.0.0` |
| `APP_PORT` | Application port | ❌ | `8000` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |

### Knowledge Base Configuration

Update `ingest.py` to customize document processing:
```python
# Supported document types
SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.md']

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

## 📈 Performance & Scaling

### Optimization Tips

1. **FAISS Index**: Use GPU-accelerated FAISS for large knowledge bases
2. **Caching**: Implement Redis for chatbot session caching
3. **Load Balancing**: Deploy multiple Nginx instances behind a load balancer
4. **Database**: Configure MongoDB replica sets for high availability

### Monitoring

Integrate monitoring tools:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Sentry**: Error tracking and reporting

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 🐛 Troubleshooting

### Common Issues

**Issue**: FAISS index not found
```bash
# Solution: Rebuild the index
python ingest.py
```

**Issue**: MongoDB connection failed
```bash
# Solution: Verify MongoDB is running
docker ps | grep mongo
# Check connection string in .env
```

**Issue**: Face++ API rate limit exceeded
```bash
# Solution: Implement request queuing or upgrade plan
```

## 📞 Support

For issues and questions:
- **Bug Reports**: Open an issue on GitHub
- **Feature Requests**: Submit via GitHub issues
- **Security Concerns**: Contact nazmulislam45213@gmail.com

## 📄 License

This project is proprietary and confidential. All rights reserved.

**© 2024 [Nazmul Islam]. Unauthorized copying, distribution, or use is strictly prohibited.**

---

<div align="center">

**Built with ❤️ by the HR Innovation Team**

[Documentation](docs/) • [API Reference](docs/api/) • [Changelog](CHANGELOG.md)

</div>
