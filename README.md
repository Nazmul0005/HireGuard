AI-Powered HR Assistant

It is a sophisticated HR assistant system that combines resume processing, face verification, and an intelligent chatbot to streamline HR operations. The system leverages advanced AI technologies including OpenAI's GPT models, Face++ API for biometric verification, and FAISS for efficient knowledge retrieval.

## Features

- **Intelligent Chatbot**: Advanced conversational AI powered by OpenAI's GPT models
- **Resume Processing**: Automated resume analysis and information extraction
- **Face Verification System**: Secure biometric verification using Face++ API
- **Knowledge Base Integration**: FAISS-powered vector storage for efficient information retrieval
- **Containerized Deployment**: Docker and Nginx configuration for scalable deployment
- **Database Integration**: MongoDB for storing verification data and user information
- **RESTful API**: FastAPI-based endpoints for all services

## Prerequisites

- Python 3.12
- Docker and Docker Compose
- OpenAI API key
- Face++ API credentials
- MongoDB instance

## Installation

1. Clone the repository
2. Set up environment variables in `.env` file with required configurations:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MODEL=gpt-5
   API_KEY=your_faceplus_api_key
   API_SECRET=your_faceplus_secret
   MONGODB_URI=your_mongodb_uri
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place your knowledge base documents in `data/knowledge_base/`
5. Run the ingestion script:
   ```bash
   python ingest.py
   ```

## Running the Application

### Local Development
```bash
uvicorn com.mhire.app.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
docker-compose up --build
```

The application will be available at `http://localhost:3014`

## API Endpoints

The system exposes several RESTful endpoints:

- `/chat` - Intelligent chatbot interface
- `/resume` - Resume processing and analysis
- `/verification` - User verification endpoints
- `/face-verification` - Face detection and verification system

Each endpoint is documented with OpenAPI/Swagger specifications available at `/docs` when running the application.

## Project Structure

```
├── com/
│   └── mhire/
│       └── app/
│           ├── main.py              # FastAPI application entry point
│           ├── config/              # Configuration management
│           ├── database/            # Database connections and management
│           └── services/
│               ├── chatbot/         # Chatbot implementation
│               ├── resume/          # Resume processing service
│               ├── verification/     # User verification
│               └── verification_system/
│                   └── face_verification/
├── data/
│   └── knowledge_base/             # Knowledge base documents
├── faiss_index/                    # Vector store indices
├── nginx/                          # Nginx configuration
├── docker-compose.yml              # Docker composition file
├── Dockerfile                      # Container configuration
├── requirements.txt                # Python dependencies
└── ingest.py                       # Knowledge base ingestion script
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **FAISS**: Efficient similarity search and clustering of dense vectors
- **OpenAI**: Advanced language models for natural language processing
- **Face++**: Face detection and recognition
- **MongoDB**: Document database for storing verification data
- **Docker**: Containerization
- **Nginx**: Reverse proxy and load balancer

## Security

- API keys and sensitive data are managed through environment variables
- Nginx configured as a reverse proxy
- Face verification for enhanced security
- MongoDB authentication required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. All rights reserved.