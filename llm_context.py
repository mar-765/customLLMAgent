from llm_messaging import *
from typing import Annotated
import toml
from glob import glob
def passprint(object):
    print(object)
    return object
filter_for_lisc = lambda x:x.load_in_system_context 
class ContextFile:
    
    heading_preset = "######### {name} ##########\n"
    def __init__(self,name,path,load_in_system_context=False,writeable=False) -> None:
        self.name = name
        self.path = path
        self.load_in_system_context = load_in_system_context
        self.writeable = writeable
        
        
    def load(self):
        print("load:",self.path)
        with open(self.path,"rb") as f:
            file = f.read()
            
        return self.heading_preset.format(name=self.name) + file.decode()
    
    def write(self,new_content):
        if self.writeable:
            with open(self.path,"w") as f:
                f.write(new_content)
                
            return True
        else: return False
        
  
class ContextManager: 
    
    def __init__(self,save_path="./config/ContextManager.toml") -> None:
        self.contextFiles:list[ContextFile] = []
        self.loaded_context = []
        self.save_path=save_path
    def addContext(self,file:ContextFile):
        self.contextFiles.append(file)
        
    def load_system_context(self):
        sys_context:list[ContextFile] = [passprint(i) for i in self.contextFiles if i.load_in_system_context]
        self.loaded_context = [ x.name
                               for x in
                               sys_context
                              ]
        
        context_str = '\n\n'.join([
            passprint(x).load()
            for x in
            sys_context
        ])
        return context_str
    
    def requires_loaded_context(self,context_name:str):
        run = context_name in self.loaded_context
        def inner(func):
            if run:
                return func
            else: 
                return lambda *x,**y:f"You need to load context '{context_name}' before using this function."
        return inner #this is the fun_obj mentioned in the above content
    
    def load_context(self,name:Annotated[str,"The name of the Markdown context (e.g. 'user.md')"]):
        """loads context in markdown format"""
        to_load = [i for i in self.contextFiles if i.name == name]
        print("load:",to_load,name)
        context_str = '\n\n'.join([
            x.load()
            for x in
            to_load
        ])
        return context_str
    
    
    def write_context(self,name:Annotated[str,"The name of the Markdown context (e.g. 'user.md')"],new_content:Annotated[str,"The new content to write to the context (replaces full old content)"]):
        """writes to markdown context. Some contexts are fixed -> can't be written."""
        to_write:ContextFile = list(filter(lambda x:x.name == name,self.contextFiles))[0]
        if to_write.write(new_content):
            return "Done!"
        else: return "This context is read only!"
        
        
    def load_context_files(self,path="./context/"):
        context_files = glob("*.md",root_dir=path)
        self.contextFiles += [ ContextFile(file,path+file,file[0] == "$" or file[0] == "%",file[0] == "%" or file[0] == "§") for file in context_files]


    # $ Load in system
    # % Load in system, writeble
    # § Writeable 
    