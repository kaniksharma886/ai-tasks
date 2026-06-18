from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
import prompt_config as pconfig
from typing import List, Type
import subprocess
import config
import utils
import json
import stat
import os


class CodingResponse(BaseModel):
    task: str  = Field(description="Initial coding task")
    code: str = Field(description="Programming language code. Provide RAW code only. DO NOT wrap it in markdown block backticks like ```python.")
    status: str = Field(description="PASS or FAIL, depending on if code is working or not")
    errors: str = Field(description="All comilation errors (if any)")
    

def run_code(raw_code: str) -> str:
    
    if raw_code.startswith("```python"):
        raw_code = raw_code.replace("```python", "", 1)
    elif raw_code.startswith("```"):
        raw_code = raw_code.replace("```", "", 1)
        
    if raw_code.endswith("```"):
        raw_code = raw_code.rsplit("```", 1)[0]
        
    clean_code = raw_code.strip()
    
    file_path = "sandpit/generated_script.py"
    
    with open(file_path, "w") as f:
        f.write(clean_code)
    
    # Run the command and capture the output
    result = subprocess.run(["python3", file_path], capture_output=True, text=True)
    out = str(result.stdout)
    err = ""
    if result.stderr:
        err = str(result.stderr)

    return out, err, file_path


def create_code(user_prompt, past_errors=None):

    try:
        model = init_chat_model(config.MODEL_NAME, temperature=config.MODEL_TEMPERATURE, base_url=config.OPENAI_BASE_URL)
        model_with_structure = model.with_structured_output(CodingResponse)
        
    except Exception as e:
        utils.log(f"Error : Failed to load model {config.MODEL_NAME}': {e}")
        return None

    conversation_history = [SystemMessage(content=pconfig.SYSTEM_MESSAGE_CODE_AGENT)]
    conversation_history.append(HumanMessage(content=user_prompt))
    if past_errors is not None:
        error_prompt = f"""Previous run resulted in these errors: 
        {past_errors}"""
        conversation_history.append(HumanMessage(content=error_prompt))

    final_structured_json = ""
    try:            
        code = model.invoke(conversation_history)
        code_str = code.content
        
        utils.log(f"\nCode: {code_str}")
        format_prompt = f"Based on your response for the prompt '{user_prompt}', format the final response: {code_str}"
        print(format_prompt)
        final_structured_json = model_with_structure.invoke(format_prompt)
        
        
    except Exception as e:
        utils.log(f"Error: Response failed : {e}")
    return final_structured_json




if __name__ == "__main__":
    
    errors = ""
    max_tries = 3
    cnt = 0
    while cnt < max_tries:
        prompt = "Write code to create a simple fastapi python code for a school."

        result = create_code(user_prompt=prompt, past_errors=errors)
        output = ""
        errors = ""
        file_path = ""
        if result and result.code:
            raw_code = result.code
            output, errors, file_path = run_code(raw_code)
        if len(errors) > 0:
            cnt += 1
        else:
            break

    utils.log(f"""
Final result:

Execution output: {output}

Errors (if any) : {errors}

Code file       : {file_path}

""")
