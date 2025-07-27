from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import json
from datetime import datetime
import asyncio
import google.generativeai as genai
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment variables
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Create the main app without a prefix
app = FastAPI(title="Persona-Driven Document Intelligence API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Data Models
class DocumentInfo(BaseModel):
    filename: str
    title: str

class PersonaInfo(BaseModel):
    role: str

class JobToBeDone(BaseModel):
    task: str

class ChallengeInfo(BaseModel):
    challenge_id: str
    test_case_name: str
    description: Optional[str] = None

class AnalysisRequest(BaseModel):
    challenge_info: ChallengeInfo
    documents: List[DocumentInfo]
    persona: PersonaInfo
    job_to_be_done: JobToBeDone

class ExtractedSection(BaseModel):
    document: str
    section_title: str
    importance_rank: int
    page_number: int

class SubsectionAnalysis(BaseModel):
    document: str
    refined_text: str
    page_number: int

class AnalysisMetadata(BaseModel):
    input_documents: List[str]
    persona: str
    job_to_be_done: str
    processing_timestamp: str

class AnalysisResult(BaseModel):
    metadata: AnalysisMetadata
    extracted_sections: List[ExtractedSection]
    subsection_analysis: List[SubsectionAnalysis]

class AnalysisResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    result: AnalysisResult
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Document analysis service
class DocumentAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def analyze_documents(self, files: List[UploadFile], analysis_request: AnalysisRequest) -> AnalysisResult:
        """Analyze documents using Gemini LLM"""
        try:
            # Save uploaded files temporarily
            temp_files = []
            file_contents = []
            
            for file in files:
                content = await file.read()
                temp_files.append(content)
                
                # Convert PDF content to base64 for Gemini
                file_content = {
                    "mime_type": file.content_type,
                    "data": base64.b64encode(content).decode('utf-8')
                }
                file_contents.append(file_content)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(analysis_request)
            
            # Prepare content for Gemini
            content_parts = [prompt]
            for file_content in file_contents:
                content_parts.append({
                    "mime_type": file_content["mime_type"],
                    "data": file_content["data"]
                })
            
            # Generate response using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                content_parts
            )
            
            # Parse the response
            result = self._parse_gemini_response(response.text, analysis_request)
            
            return result
            
        except Exception as e:
            logging.error(f"Error in document analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        finally:
            # Clean up temporary files
            for content in temp_files:
                del content
    
    def _create_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Create structured prompt for Gemini analysis"""
        prompt = f"""
        You are a document intelligence system that analyzes multiple PDFs based on a specific persona and job-to-be-done.
        
        **PERSONA**: {request.persona.role}
        **JOB TO BE DONE**: {request.job_to_be_done.task}
        
        **DOCUMENTS PROVIDED**: {len(request.documents)} PDFs
        {chr(10).join([f"- {doc.filename}: {doc.title}" for doc in request.documents])}
        
        **ANALYSIS REQUIREMENTS**:
        1. Extract and rank the most relevant sections from each document based on the persona and job-to-be-done
        2. Identify 3-5 most important sections across all documents
        3. For each important section, provide refined text that's most relevant to the task
        4. Rank sections by importance (1 = most important)
        
        **OUTPUT FORMAT** (JSON):
        {{
            "extracted_sections": [
                {{
                    "document": "filename.pdf",
                    "section_title": "Section Title",
                    "importance_rank": 1,
                    "page_number": 1
                }}
            ],
            "subsection_analysis": [
                {{
                    "document": "filename.pdf", 
                    "refined_text": "Key relevant content extracted and refined for the persona's needs",
                    "page_number": 1
                }}
            ]
        }}
        
        Focus on extracting content that directly helps the {request.persona.role} accomplish: {request.job_to_be_done.task}
        
        Provide only the JSON output, no additional text.
        """
        return prompt
    
    def _parse_gemini_response(self, response: str, request: AnalysisRequest) -> AnalysisResult:
        """Parse Gemini response and create structured result"""
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                # Fallback: create basic structure
                analysis_data = {
                    "extracted_sections": [],
                    "subsection_analysis": []
                }
            
            # Create metadata
            metadata = AnalysisMetadata(
                input_documents=[doc.filename for doc in request.documents],
                persona=request.persona.role,
                job_to_be_done=request.job_to_be_done.task,
                processing_timestamp=datetime.utcnow().isoformat()
            )
            
            # Parse extracted sections
            extracted_sections = []
            for section in analysis_data.get("extracted_sections", []):
                extracted_sections.append(ExtractedSection(
                    document=section.get("document", ""),
                    section_title=section.get("section_title", ""),
                    importance_rank=section.get("importance_rank", 1),
                    page_number=section.get("page_number", 1)
                ))
            
            # Parse subsection analysis
            subsection_analysis = []
            for subsection in analysis_data.get("subsection_analysis", []):
                subsection_analysis.append(SubsectionAnalysis(
                    document=subsection.get("document", ""),
                    refined_text=subsection.get("refined_text", ""),
                    page_number=subsection.get("page_number", 1)
                ))
            
            return AnalysisResult(
                metadata=metadata,
                extracted_sections=extracted_sections,
                subsection_analysis=subsection_analysis
            )
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {str(e)}")
            # Return basic structure with error
            return AnalysisResult(
                metadata=AnalysisMetadata(
                    input_documents=[doc.filename for doc in request.documents],
                    persona=request.persona.role,
                    job_to_be_done=request.job_to_be_done.task,
                    processing_timestamp=datetime.utcnow().isoformat()
                ),
                extracted_sections=[],
                subsection_analysis=[]
            )

# Initialize analyzer
analyzer = DocumentAnalyzer()

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Persona-Driven Document Intelligence API", "version": "1.0.0"}

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_documents(
    files: List[UploadFile] = File(...),
    analysis_request: str = Form(...)
):
    """Analyze multiple PDF documents based on persona and job-to-be-done"""
    try:
        # Parse analysis request
        request_data = json.loads(analysis_request)
        analysis_req = AnalysisRequest(**request_data)
        
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        # Perform analysis
        result = await analyzer.analyze_documents(files, analysis_req)
        
        # Create response
        response = AnalysisResponse(result=result)
        
        # Store in database
        await db.analysis_results.insert_one(response.dict())
        
        return response
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid analysis request JSON")
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis result by ID"""
    result = await db.analysis_results.find_one({"id": analysis_id})
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

@api_router.get("/analysis")
async def list_analyses():
    """List all analyses"""
    analyses = await db.analysis_results.find().to_list(100)
    return analyses

@api_router.get("/collections")
async def get_sample_collections():
    """Get sample document collections for testing"""
    collections = [
        {
            "id": "collection_1",
            "name": "Travel Planning - South of France",
            "description": "7 travel guides for South of France",
            "persona": "Travel Planner",
            "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends",
            "document_count": 7
        },
        {
            "id": "collection_2", 
            "name": "Adobe Acrobat Learning",
            "description": "15 Adobe Acrobat tutorials",
            "persona": "HR Professional",
            "job_to_be_done": "Create and manage fillable forms for onboarding and compliance",
            "document_count": 15
        },
        {
            "id": "collection_3",
            "name": "Recipe Collection",
            "description": "9 cooking guides",
            "persona": "Food Contractor",
            "job_to_be_done": "Prepare vegetarian buffet-style dinner menu for corporate gathering",
            "document_count": 9
        }
    ]
    return collections

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()