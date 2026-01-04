#!/usr/bin/env python3
"""Run script for the application."""
import uvicorn
from backend.config import config

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )




