import time
import config
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import utils
import db_manager as db

def start_streaming_chat():
    #Initializes a generic chat loop.
    db.init_db()
    try:
        model = config.MODEL_NAME
        temp = config.MODEL_TEMPERATURE
        base_url = config.OPENAI_BASE_URL

        model = init_chat_model(model, temperature=temp,base_url=base_url)
    except Exception as e:
        utils.log(f"Error : Failed to load model {model}': {e}")
        return

    # Initialize conversation history
    conversation_history = [
        SystemMessage(content="You are a helpful, generic AI assistant.")
    ]
    
    past_messages = db.fetch_last_messages()
    conversation_history.extend(past_messages)
    
    
    utils.log(f"Chat Started.")
    utils.log(f"Type '{config.EXIT_STRING}' to stop.")
    
    while True:
        user_input = input("User: ")
        
        if user_input.lower() == config.EXIT_STRING:
            utils.log("Exiting...")
            break
            
        if not user_input.strip():
            continue
            
        # Append user message
        conversation_history.append(HumanMessage(content=user_input))
        
        # Save this new msg in database
        db.save_message("user", user_input)

        try:
            prompt_tokens = model.get_num_tokens_from_messages(conversation_history)
        except Exception:
            prompt_tokens = 0

        
        ai_response = ""
        
        st_time = time.perf_counter()
        utils.log("LLM:")
        try:
            
            for chunk in model.stream(conversation_history):
                token = chunk.content
                if token:
                    utils.log(token, end="", flush=True)
                    ai_response += token
            
            end_time = time.perf_counter()
            latency = int((end_time - st_time) * 1000)
            
            utils.log("\n")
            
            # Append complete response to history
            conversation_history.append(AIMessage(content=ai_response))
            
            
            db.save_message("assistant", ai_response)
            
            # Calculate output token
            try:
                completion_tokens = model.get_num_tokens(ai_response)
            except Exception:
                completion_tokens = 0
                
            total_cost = (prompt_tokens * config.COST_PER_INPUT_TOKEN) + (completion_tokens * config.COST_PER_OUTPUT_TOKEN)
            
            # [stats] prompt=8 completion=23 cost=$0.000146 latency=623 ms
            # Trying to print above format after every message
            
            utils.log(f"\n[stats] prompt={prompt_tokens} completion={completion_tokens} cost=${total_cost:.6f} latency={latency}ms")

        except Exception as e:
            utils.log(f"Error: Response failed : {e}")

