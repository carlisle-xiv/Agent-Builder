import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    uvicorn.run(
        "src.app:app", host="0.0.0.0", port=port, reload=reload, log_level="info"
    )
