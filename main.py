from fastapi import FastAPI

# Initialize the SEO Automation Engine API
app = FastAPI(
    title="SEO Automation Engine",
    description="Backend API for AI Content Generation and Publishing Pipeline",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "SEO Automation Engine is running.",
        "next_steps": "Database integration pending."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "components": ["api"]}