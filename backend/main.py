import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .groq_client import generate_proposal_stream, DEFAULT_MODEL

app = FastAPI(
    title="GigPitch AI",
    description="Freelance proposal generator powered by open-weight AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "app": "GigPitch AI",
        "model": DEFAULT_MODEL,
        "engine": "Groq LPU / Open-Weight",
    }


@app.post("/api/generate")
async def generate(request: Request):
    """
    Stream-generates a proposal based on job description, skills, and tone.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON payload."}, status_code=400)

    job_desc = body.get("job_description", "").strip()
    skills = body.get("skills", "").strip()
    tone = body.get("tone", "professional").strip().lower()

    if not job_desc:
        return JSONResponse({"error": "Job description cannot be empty."}, status_code=400)
    if not skills:
        return JSONResponse({"error": "Freelancer skills cannot be empty."}, status_code=400)
    if tone not in ("professional", "friendly", "bold"):
        tone = "professional"

    return StreamingResponse(
        generate_proposal_stream(job_desc, skills, tone),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Mount frontend static directory
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
