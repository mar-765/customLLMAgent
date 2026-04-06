from dataclasses import dataclass
from typing import Optional, Dict, Any
import groq
from groq.types.chat import ChatCompletionMessageToolCall
from uuid import uuid4 as gen_uuid
import json 


@dataclass
class Message:
    content:str
    role:str
    
    
    
    @property
    def dict(self):
        return {
            k: v
            for k, v in vars(self).items()
            if v is not None
        }
    
    @classmethod
    def system(cls, text,name = None):
        return SystemMessage(content=text,name=name)
    
    @classmethod
    def user(cls, text,name = None):
        return UserMessage(content=text,name=name)
    
    @classmethod
    def from_dict(cls, data):
        role = data.get("role")

        if role == "system":
            return SystemMessage(
                content=data.get("content")
            )

        elif role == "user":
            return UserMessage(
                content=data.get("content")
            )

        elif role == "assistant":
            return AssistantMessage(
                content=data.get("content"),
                tool_calls=data.get("tool_calls")
            )

        elif role == "tool":
            return ToolMessage(
                content=data.get("content"),
                tool_call_id=data.get("tool_call_id")
            )

        else:
            raise ValueError(f"Unknown message role: {role}")
        
            

@dataclass
class SystemMessage(Message):
    name:Optional[str]=None
    role:str="system"
@dataclass
class UserMessage(Message):
    name:Optional[str]=None
    role:str="user"

@dataclass
class AssistantMessage(Message):
    content:Optional[str] = None#type:ignore
    tool_calls: list[ChatCompletionMessageToolCall]|None = None
    role:str="assistant"
    name:Optional[str] = None
    reasoning:Optional[str] = None
    
@dataclass
class ToolMessage(Message):
    tool_call_id:str = ""
    role:str="tool"
    name:str =""
    

class Chat:
    
    def __init__(self,name:str|None=None,save_path:str="./chat_history.json",length_before_cleanup:int=6*750*8) -> None:
        self.messages:list[Message] = []
        self.name = name if name else gen_uuid()
        self.save_path=save_path
        self.length_before_cleanup = length_before_cleanup
        
    def send(self,message:Message):
        if len(str(self.messages)) >  self.length_before_cleanup:
            self.clean_up()
        self.messages.append(message)
       
    def clean_up(self):
        for i in self.messages:
            if isinstance(i,ToolMessage):
                del self.messages[self.messages.index(i)]
                
    @property
    def dict(self) -> list[dict[str,Any]]:
        return [i.dict 
                for i in
                self.messages if isinstance(i.dict,dict)]
            

    def user(self,content:str,name=None):
        self.send(UserMessage(content=content,name=name))
        
    def system(self,content,name=None):
        self.send(SystemMessage(content=content,name=name))
        
    
            
class ChatManager:
    def __init__(self,maxChats:int=100,save_path:str="./chat_history.json") -> None:
        self.maxChats = maxChats
        self.chats:dict[int,Chat] = {}
        self.save_path = save_path
        
    def createChat(self,sysprompt,sysprompt_name,name:str="New Chat"):
        for i in range(len(self.chats.keys())+1):
            if i not in self.chats.keys():
                self.chats[i] = (Chat(name,self.save_path))
                self.chats[i].system(sysprompt,sysprompt_name)
                break
        
    def changeChatName(self,chat_id:int,name:str):
        self.chats[chat_id].name = name
        
    def deleteChat(self,chat_id:int):
        del self.chats[chat_id]
        
    def getChat(self,chat_id:int):
        return self.chats[chat_id]
    
 