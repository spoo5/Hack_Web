# DataSage Backend

## Setup

1. Create virtual environment:

```bash
python -m venv venv
```

2. Activate virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run server:

```bash
python main.py
```

Server will run on `http://localhost:8000`

## API Endpoints

- `POST /upload` - Upload CSV dataset
- `POST /query` - Query dataset with natural language
- `GET /dataset/info` - Get current dataset information
- `GET /conversation/history` - Get conversation history
- `DELETE /conversation/clear` - Clear conversation history
- `GET /health` - Health check

## Features

✅ Dataset-agnostic CSV processing
✅ Schema auto-detection
✅ Anti-hallucination enforcement (Pandas-only computation)
✅ Natural language query parsing
✅ Deterministic analytics engine
✅ Structured 4-section responses
✅ Conversation context memory
✅ Confidence scoring
✅ Data grounding
