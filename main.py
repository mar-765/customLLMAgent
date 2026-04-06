from fastapi import FastAPI,Request,Response
from pydantic import BaseModel

from loguru import logger
from helper_constants.loguru import Formats as loguruFormts

from llm import LLM,clientPresets,modelPresets

import sys,os

import dotenv

dotenv.load_dotenv(".env")



logger.remove()
logger.add(sys.stderr,format=loguruFormts.defualt_extra)

llm = LLM(client=clientPresets.groq,
          model=modelPresets.groq_openai_gpt_oss_20b,
          )


class LLMQuestion(BaseModel):
    text:str
    
app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello, World!"}


@app.post("/ask")
def query(q:LLMQuestion):
    answer = llm.call_with_tools(q.text)
    return {"reply":answer}

@app.get("/chat/clear")
def chat_clear():
    llm.clear_chat()
    return {"status":"done"}


@app.middleware("http")
async def auth(request:Request,call_next):
    if request.headers.get("Authorization") != f"Bearer {os.environ.get("API_KEY")}":
        return Response("Unauthorized", status_code=401)
    
    return await call_next(request)