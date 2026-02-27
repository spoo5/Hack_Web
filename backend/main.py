"""
DataSage - Conversational Data Intelligence Platform
Main FastAPI Application
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn

from csv_manager import CSVManager
from schema_analyzer import SchemaAnalyzer
from query_parser import QueryParser
from analytics_engine import AnalyticsEngine
from response_formatter import ResponseFormatter

app = FastAPI(title="DataSage API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
csv_manager = CSVManager()
schema_analyzer = SchemaAnalyzer()
query_parser = QueryParser()
analytics_engine = AnalyticsEngine()
response_formatter = ResponseFormatter()

# Conversation history
conversation_history: List[Dict[str, Any]] = []


class QueryRequest(BaseModel):
    query: str
    context: Optional[List[Dict[str, Any]]] = []


class QueryResponse(BaseModel):
    answer: str
    sql_logic: str
    derivation: Dict[str, Any]
    visualization_type: str
    chart_data: Dict[str, Any]
    row_count: int
    confidence_score: float
    grounding_info: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    company: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: Dict[str, Any]
    message: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "DataSage API",
        "version": "1.0.0"
    }


@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    User login endpoint (mock implementation)
    In production, this would verify credentials against a database
    and implement proper password hashing and JWT token generation
    """
    # Mock validation - in production, check against database
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Simulate successful login
    mock_token = f"mock_jwt_token_{request.email.replace('@', '_at_')}"
    user_data = {
        "name": request.email.split('@')[0].title(),
        "email": request.email,
        "company": "DataSage User",
        "userId": f"user_{hash(request.email) % 10000}"
    }
    
    return AuthResponse(
        token=mock_token,
        user=user_data,
        message="Login successful"
    )


@app.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    User registration endpoint (mock implementation)
    In production, this would:
    - Validate email uniqueness
    - Hash passwords with bcrypt
    - Store user in database
    - Send verification email
    """
    # Mock validation
    if not request.email or not request.password or not request.name:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    # Simulate successful signup
    mock_token = f"mock_jwt_token_{request.email.replace('@', '_at_')}"
    user_data = {
        "name": request.name,
        "email": request.email,
        "company": request.company,
        "userId": f"user_{hash(request.email) % 10000}"
    }
    
    return AuthResponse(
        token=mock_token,
        user=user_data,
        message="Registration successful"
    )


@app.post("/auth/google")
async def google_auth(google_token: Dict[str, str]):
    """
    Google OAuth authentication endpoint (mock implementation)
    In production, this would:
    - Verify Google OAuth token with Google's API
    - Extract user info from Google
    - Create or update user in database
    - Generate JWT token
    """
    # Mock Google auth - in production, verify token with Google
    email = google_token.get("email", "user@example.com")
    name = google_token.get("name", "Google User")
    
    mock_token = f"mock_jwt_token_google_{email.replace('@', '_at_')}"
    user_data = {
        "name": name,
        "email": email,
        "company": "Google Workspace",
        "userId": f"user_{hash(email) % 10000}",
        "authProvider": "google"
    }
    
    return AuthResponse(
        token=mock_token,
        user=user_data,
        message="Google authentication successful"
    )


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload and process CSV dataset
    Returns schema, row count, and preview
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read and store dataset
        content = await file.read()
        dataset_info = csv_manager.load_csv(content, file.filename)
        
        # Analyze schema
        schema = schema_analyzer.analyze(csv_manager.get_dataframe())
        
        # Generate suggested questions based on schema
        suggested_questions = schema_analyzer.generate_suggested_questions()
        
        # Clear conversation history on new upload
        global conversation_history
        conversation_history = []
        
        return {
            "success": True,
            "filename": file.filename,
            "row_count": dataset_info["row_count"],
            "column_count": dataset_info["column_count"],
            "columns": dataset_info["columns"],
            "schema": schema,
            "preview": dataset_info["preview"],
            "suggested_questions": suggested_questions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/dataset/info")
async def get_dataset_info():
    """Get current dataset information"""
    if not csv_manager.has_dataset():
        raise HTTPException(status_code=404, detail="No dataset loaded")
    
    df = csv_manager.get_dataframe()
    schema = schema_analyzer.analyze(df)
    
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "schema": schema,
        "filename": csv_manager.filename
    }


@app.post("/query")
async def query_dataset(request: QueryRequest):
    """
    Process natural language query and return structured response
    """
    try:
        if not csv_manager.has_dataset():
            raise HTTPException(status_code=404, detail="No dataset loaded. Please upload a CSV first.")
        
        df = csv_manager.get_dataframe()
        schema = schema_analyzer.analyze(df)
        
        # Parse query with context
        global conversation_history
        parsed_query = query_parser.parse(
            request.query,
            schema,
            conversation_history
        )
        
        # Check if query is valid
        if "error" in parsed_query:
            return {
                "answer": f"❌ {parsed_query['error']}",
                "sql_logic": "-- Query could not be parsed",
                "derivation": {
                    "error": parsed_query['error'],
                    "rows_analyzed": 0,
                    "columns_used": []
                },
                "visualization_type": "none",
                "chart_data": {},
                "row_count": len(df),
                "confidence_score": 0.0,
                "grounding_info": "Query parsing failed"
            }
        
        # Execute query using Pandas
        result = analytics_engine.execute(df, parsed_query)
        
        # Format response
        response = response_formatter.format(
            result,
            parsed_query,
            len(df)
        )
        
        # Add to conversation history
        conversation_history.append({
            "query": request.query,
            "parsed": parsed_query,
            "response": response
        })
        
        # Keep only last 10 conversations
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/conversation/history")
async def get_conversation_history():
    """Get conversation history"""
    return {
        "history": conversation_history,
        "count": len(conversation_history)
    }


@app.delete("/conversation/clear")
async def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return {"success": True, "message": "Conversation history cleared"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "dataset_loaded": csv_manager.has_dataset(),
        "row_count": len(csv_manager.get_dataframe()) if csv_manager.has_dataset() else 0,
        "conversation_count": len(conversation_history)
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
