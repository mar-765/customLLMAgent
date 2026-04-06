from fastapi import FastAPI,Request,Response
from pydantic import BaseModel

from loguru import logger
from helper_constants.loguru import Formats as loguruFormts

from llm import LLM,clientPresets,modelPresets

import sys



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
    if request.headers.get("Authorization") != "Bearer f202bc8e18ce0c17deeeedbcf0360e4249dddaa9f784855e5b425a1d39763b1f99504dddb20d94d001f94e6af07568253e46365bc842ddab8af96d8ef07a3fdb":
        return Response("Unauthorized", status_code=401)
    
    return await call_next(request)