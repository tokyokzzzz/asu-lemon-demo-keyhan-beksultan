import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.analysis import router as analysis_router

# Load and validate environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

app = FastAPI(title="TZ Analyzer API", version="1.0.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory as static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    print(f"[{timestamp}] ✓ Uploads directory ready")

    # Validate GEMINI_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    # Test Gemini API connection
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Reply with OK")
        if response and response.text:
            print(f"[{timestamp}] ✓ Gemini API connection successful")
        else:
            print(f"[{timestamp}] ⚠ Gemini API response empty")
    except Exception as e:
        print(f"[{timestamp}] ❌ Gemini API connection failed: {str(e)}")
        

    print(f"[{timestamp}] ✓ TZ Analyzer API ready")


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


# Include analysis router
app.include_router(analysis_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
