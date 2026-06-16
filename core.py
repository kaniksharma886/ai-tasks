import config
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import utils


def start_streaming_chat():
    #Initializes a generic chat loop.
    
    try:
        model = config.MODEL_NAME
        temp = config.MODEL_TEMPRATURE
        # Dynamically load model
        model = init_chat_model(model, temperature= temp)
    except Exception as e:
        utils.log(f"Error : Failed to load model {model}': {e}")
        return

    # Initialize conversation history
    conversation_history = [
        SystemMessage(content="You are a helpful, generic AI assistant.")
    ]
    
    utils.log(f"Chat Loop Initialized. Model: {model}, temprature: {temp}")
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
        
        full_ai_response = ""
        
        try:
            
            for chunk in model.stream(conversation_history):
                token = chunk.content
                if token:
                    utils.log(token, end="", flush=True)
                    full_ai_response += token
            
            utils.log("\n")
            
            # Append complete response to history
            conversation_history.append(AIMessage(content=full_ai_response))
            
        except Exception as e:
            utils.log(f"Error: Response failed : {e}")

if __name__ == "__main__":

    start_streaming_chat()
