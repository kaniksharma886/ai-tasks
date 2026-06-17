from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
import prompt_config as pconfig
from typing import List, Type
import config
import utils
import json


class CodingResponse(BaseModel):
    task: str  = Field(description="Initial coding task")
    code: str = Field(description="Programming language code")
    status: str = Field(description="PASS or FAIL, depending on if code is working or not")
    errors: str = Field(description="All comilation errors (if any)")
    

def run_code(code: str) -> str:
    pass
    

def create_code(user_prompt, past_errors=None):
    
    try:
        retriever = rag_manager.get_retriever()
    except Exception as e:
        utils.log(f"Error: Failed to get retriever: {e}")
        return


    try:
        model = init_chat_model(config.MODEL_NAME, temperature=config.MODEL_TEMPERATURE, base_url=config.OPENAI_BASE_URL)
        model_with_structure = model.with_structured_output(CodingResponse)
        
    except Exception as e:
        utils.log(f"Error : Failed to load model {config.MODEL_NAME}': {e}")
        return

    conversation_history = [SystemMessage(content=pconfig.SYSTEM_MESSAGE)]
    conversation_history.append(HumanMessage(content=user_prompt))
    if past_errors is not None:
        error_prompt = f"""Previous run resulted in these errors: 
        {past_errors}"""
        conversation_history.append(HumanMessage(content=error_prompt))
    
    try:            
        code = model.invoke(conversation_history)
        utils.log(f"\nCode: {code}")
        final_structured_json = model_with_structure.invoke(f"Based on your response for the prompt '{user_prompt}', format the final response: {code['output']}") 
    except Exception as e:
        utils.log(f"Error: Response failed : {e}")
    

if __name__ == "__main__":
    prompt = "Write code to add 4 numbers in python"
    result = create_code(user_prompt=prompt)
    utils.log("Final Resp : ", result)
