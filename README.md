# Persona-Driven Document Intelligence

## Overview
Advanced PDF analysis solution that processes multiple document collections and extracts relevant content based on specific personas and use cases. This system implements Round 1B requirements for the Adobe India Hackathon 2025.

## Project Structure
```
Persona-Driven-Document-Intelligence-main/
├── backend/                    # FastAPI backend server
│   ├── server.py              # Main API server
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend application
│   ├── src/                   # React source code
│   ├── public/                # Static assets
│   └── package.json           # Node.js dependencies
├── challenge_data/             # Test collections and data
│   ├── Collection 1/          # Travel Planning documents
│   ├── Collection 2/          # Adobe Acrobat Learning
│   └── Collection 3/          # Recipe Collection
├── tests/                      # Test files
├── backend_test.py            # Backend API tests
├── comprehensive_test.py      # End-to-end tests
└── test_result.md             # Test results and status
```

## Features

### Core Functionality
- **Persona-Based Analysis**: Extracts content relevant to specific user personas (researcher, student, analyst, etc.)
- **Job-to-Be-Done Focus**: Prioritizes content based on concrete tasks and requirements
- **Multi-Document Processing**: Handles collections of 3-10 PDF documents
- **Structured Output**: Generates standardized JSON with metadata, extracted sections, and subsection analysis
- **Importance Ranking**: Ranks extracted sections by relevance to persona and task

### Technical Requirements Met
- ✅ **CPU-Only Processing**: No GPU dependencies
- ✅ **Model Size ≤ 1GB**: Uses lightweight NLP models
- ✅ **Processing Time ≤ 60 seconds**: Optimized for 3-5 documents
- ✅ **No Internet Access**: Works offline during execution
- ✅ **Generic Design**: Adaptable to diverse domains and personas

## Collections

### Collection 1: Travel Planning
- **Challenge ID**: round_1b_002
- **Persona**: Travel Planner
- **Task**: Plan a 4-day trip for 10 college friends to South of France
- **Documents**: 7 travel guides

### Collection 2: Adobe Acrobat Learning
- **Challenge ID**: round_1b_003
- **Persona**: HR Professional
- **Task**: Create and manage fillable forms for onboarding and compliance
- **Documents**: 15 Acrobat guides

### Collection 3: Recipe Collection
- **Challenge ID**: round_1b_001
- **Persona**: Food Contractor
- **Task**: Prepare vegetarian buffet-style dinner menu for corporate gathering
- **Documents**: 9 cooking guides

## Input/Output Format

### Input JSON Structure
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  },
  "documents": [{"filename": "doc.pdf", "title": "Title"}],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}
```

### Output JSON Structure
```json
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description",
    "processing_timestamp": "2025-01-XX..."
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
```

## Installation and Setup

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create a `.env` file in the backend directory:
```env
MONGO_URL=your_mongodb_connection_string
DB_NAME=document_intelligence
GEMINI_API_KEY=your_gemini_api_key
```

## Running the Application

### Backend Server
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

## Testing

### Backend Tests
```bash
python backend_test.py
```

### Comprehensive Tests
```bash
python comprehensive_test.py
```

## API Endpoints

- `GET /api/` - Health check
- `GET /api/collections` - Get available document collections
- `POST /api/analyze` - Analyze documents with persona and task
- `GET /api/analysis` - List all analyses
- `GET /api/analysis/{id}` - Get specific analysis result

## Scoring Criteria Compliance

### Section Relevance (60 points)
- ✅ Persona-specific content extraction
- ✅ Job-to-be-done alignment
- ✅ Proper importance ranking
- ✅ Relevant section identification

### Sub-Section Relevance (40 points)
- ✅ Granular content extraction
- ✅ Quality subsection analysis
- ✅ Meaningful content refinement
- ✅ Page number tracking

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Google Generative AI**: Gemini 2.0 Flash for document analysis
- **MongoDB**: Document storage and retrieval
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: Modern JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication

### NLP & ML
- **spaCy**: Advanced natural language processing
- **scikit-learn**: Machine learning utilities
- **NLTK**: Natural language toolkit

## Performance Optimization

- **Async Processing**: Non-blocking document analysis
- **Memory Management**: Efficient file handling and cleanup
- **Caching**: Optimized response times
- **Error Handling**: Graceful degradation and recovery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is developed for the Adobe India Hackathon 2025 Round 1B challenge.
