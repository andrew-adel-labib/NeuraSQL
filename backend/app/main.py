from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.app.api.ask import (
    router as ask_router
)

from backend.app.api.realtime import (
    router as realtime_router
)


app = FastAPI(
    title="QBS SQL AI API",

    description="""
    Enterprise conversational SQL AI platform
    with realtime voice transcription,
    ERP analytics, and multi-model AI support.
    """,

    version="1.0.0"
)



app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)



app.include_router(
    ask_router
)

app.include_router(
    realtime_router,
    prefix="/realtime",
    tags=["Realtime Voice"]
)



@app.get("/")
async def root():

    return {

        "status": "running",

        "service": "QBS SQL AI API",

        "features": [

            "SQL AI Analytics",

            "Realtime Voice Transcription",

            "Claude Support",

            "OpenAI Support",

            "Groq Support",

            "Enterprise ERP Intelligence"
        ]
    }



@app.get("/health")
async def health():

    return {

        "status": "healthy"
    }