import os
from groq import Groq
import tools_py.tools as tools
import llm_easy_tools as llmet
from pprint import pprint
import json
import colorama
from colorama import Fore
from dataclasses import dataclass
from typing import Annotated,Callable
import toml
from dotenv import load_dotenv
import datetime
from llm_context import ContextManager
import llm_messaging as llmsg

import time
import sys 



load_dotenv(".env")
colorama.init(True)


def readFile(file):
    with open(file,"r") as f:
        return f.read()


@dataclass
class clientPresets:
    groq = Groq(
        api_key=readFile("API_KEY.txt"),  # Fro anyone askinf them selves "Why should someone do this like that" or "Why dosent he use .env files", because it didnt work. And I am to lazy to find a proper fix (And it works like this)
    )

@dataclass
class modelPresets:
    groq_openai_gpt_oss_20b =  "openai/gpt-oss-20b"
    
#
    
class LLM:
    
    
    def __init__(self,  client:Groq,model:str,save_path="./config/model1.toml",auto_save_time:int=-1,print_reasoning=True,show_tool_calls=True,allowed_buildin_tools=["browser_search","code_interpreter"],additionaltools:list|None=None,send_func:Callable|None=None,) -> None:
        self.client=client
        self.print_reasoning=print_reasoning
        self.show_tool_calls=show_tool_calls
        self.allowed_buildin_tools=allowed_buildin_tools
        self.additionaltools=additionaltools
        self.model = model
        
        
        self.send_func = send_func
        self.auto_save_time = auto_save_time
        
        self.save_path = save_path
        
       
        
        self.context_mgr = ContextManager()
        self.context_mgr.load_context_files()
        
        # print("User.md:",self.context_manager.load_context("user.md"))
        
        self.chat = llmsg.Chat("__default__")
        
        self.chat.system(self.context_mgr.load_system_context())
        def load_context_tool(name:Annotated[str,"the name of the context to load"]):
            """loads context by name"""
            print("Load context tool",name)
            return self.context_mgr.load_context(name)

        def write_context_tool(name:Annotated[str,"name of the context to override"],new_contend:Annotated[str,"The text tooverride the context with."]):
            """Overrides a context with new data"""
            print("write context tool",name)
            return self.context_mgr.write_context(name,new_contend)
        context_tools = [load_context_tool,write_context_tool]
        self.tools_list = tools.tools + context_tools + (additionaltools if additionaltools else [])
        self.tools = llmet.get_tool_defs(self.tools_list)#type:ignore
        
        #pprint(llmet.get_tool_defs(tools.tools))
        
   
    def call_with_tools(self,prompt,chat_id=0):
        
        
        self.chat.user(prompt)
        
        while True:
            #pprint(messages)
            assistentMessage = self.complete_chat(self.chat)
            if self.print_reasoning and assistentMessage.reasoning: print(Fore.YELLOW+f"Reasoning: {assistentMessage.reasoning}")#type:ignore
            if assistentMessage.tool_calls:
                
                
                for tool_call in assistentMessage.tool_calls:
                    
                    if self.show_tool_calls: print(f"Tool call! Tool:{tool_call.function.name}") 
                    
                    tool_res = llmet.process_tool_call(tool_call,self.tools_list)
                    
                    #Create Tool return massage and send it in the chat 
                    msg = llmsg.ToolMessage(content=json.dumps(tool_res.output),
                                            tool_call_id=tool_res.tool_call_id,
                                            name=tool_res.name)
                    self.chat.send(msg)
            else: break
              
        print(self.send_func)  
        if self.send_func:
            self.send_func(assistentMessage.content)
            print("DEBUG:",assistentMessage.content)
            return "No output. Used sendfunc!"
        else:
            
            return assistentMessage.content
    
    def complete_chat(self,chat:llmsg.Chat):
        print(chat.dict[-1])
        chat_completion = self.client.chat.completions.create(
                    messages=chat.dict,#type:ignore
                    model=self.model,
                    tools=self.tools,#type:ignore
                    tool_choice="auto",
                    compound_custom={"tools":{"enabled_tools":self.allowed_buildin_tools}}
                )
    
        msg = llmsg.AssistantMessage(content=chat_completion.choices[0].message.content,
                                             tool_calls=chat_completion.choices[0].message.tool_calls,
                                             reasoning=chat_completion.choices[0].message.reasoning,)
        chat.send(msg)
        return msg

    
    def write_to_context(self,name,new_content):
        self.context_mgr.write_context(name,new_content)
        
    def clear_chat(self):
        del self.chat
        self.chat=llmsg.Chat("__default__")


if __name__ == "__main__":
    ai = LLM(clientPresets.groq,modelPresets.groq_openai_gpt_oss_20b)
    while True:
        prompt = input(">>")
        print(ai.call_with_tools(prompt))
    