from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import init_chat_model
import prompt_config as pconfig
import db_manager as db
import rag_manager
import config
import utils
import time



def chat_helper(user_input, use_rag=False):
    #Initializes database.
    db.init_db()
    
    try:
        retriever = rag_manager.get_retriever()
    except Exception as e:
        utils.log(f"Error: Failed to get retriever: {e}")
        return


    try:
        model = init_chat_model(config.MODEL_NAME, temperature=config.MODEL_TEMPERATURE, base_url=config.OPENAI_BASE_URL)
    except Exception as e:
        utils.log(f"Error : Failed to load model {config.MODEL_NAME}': {e}")
        return

    # Initialize conversation history
    sys_msg = pconfig.SYSTEM_MESSAGE_RAG if use_rag else pconfig.SYSTEM_MESSAGE
    conversation_history = [
        SystemMessage(content=sys_msg)
    ]
    
    past_messages = db.fetch_last_messages()
    conversation_history.extend(past_messages)

    db.save_message("user", user_input)
    if use_rag:
        try:
            retrieved_docs = retriever.invoke(user_input)
        except Exception as e:
            utils.log(f"Retrieval Error: {e}")
            retrieved_docs = []
            

            # This is for inline citation requirement 3.2 (c) i.
            context_str = ""
            for idx, doc in enumerate(retrieved_docs, start=1):
                source_file = doc.metadata.get("source", "Unknown")
                context_str += f"\n[{idx}] (Source: {source_file}):\n{doc.page_content}\n"

            rag_prompt = f"""
    Context Material:
    {context_str}

    User Query: {user_input}"""
            
            
            # Append rag_prompt instead of user prompt as we need to reve it after chat response.
            conversation_history.append(HumanMessage(content=rag_prompt))

    try:
        prompt_tokens = model.get_num_tokens_from_messages(conversation_history)
    except Exception:
        prompt_tokens = 0
    
    ai_response = ""
    
    try:
        st_time = time.perf_counter()
        retry = 3
        resp = None
        while retry > 0:
            try:
                print(">>",conversation_history,"<<")
                resp = model.invoke(conversation_history)
                retry = 0
            except:
                utils.log("Retrying...")
                retry -= 1
        
        ai_response = resp.content
        end_time = time.perf_counter()
        latency = int((end_time - st_time) * 1000)
        
        if use_rag:
            conversation_history.pop() 
        conversation_history.append(HumanMessage(content=user_input))

        # Append complete response to history
        conversation_history.append(AIMessage(content=ai_response))
        db.save_message("assistant", ai_response)
        
        # to keep in memory chat history <= 10 : 1 System + 10 User/AI 
        while len(conversation_history) > config.MESSAGE_HISTORY_LIMIT + 1:
            conversation_history.pop(1)
        
        # Calculate output token
        try:
            completion_tokens = model.get_num_tokens(ai_response)
        except Exception:
            completion_tokens = 0
            
        total_cost = (prompt_tokens * config.COST_PER_INPUT_TOKEN) + (completion_tokens * config.COST_PER_OUTPUT_TOKEN)
        
        # [stats] prompt=8 completion=23 cost=$0.000146 latency=623 ms
        # Trying to print above format after every message
        
        return ai_response, f"\n[stats] prompt={prompt_tokens} completion={completion_tokens} cost=${total_cost:.6f} latency={latency}ms"

    except Exception as e:
        return "AI Error", f"Error: Response failed : {e}"





def start_streaming_chat():
    #Initializes database.
    db.init_db()
    
    try:
        retriever = rag_manager.get_retriever()
    except Exception as e:
        utils.log(f"Error: Failed to get retriever: {e}")
        return


    try:
        model = init_chat_model(config.MODEL_NAME, temperature=config.MODEL_TEMPERATURE, base_url=config.OPENAI_BASE_URL)
    except Exception as e:
        utils.log(f"Error : Failed to load model {config.MODEL_NAME}': {e}")
        return

    # Initialize conversation history
    conversation_history = [
        SystemMessage(content=pconfig.SYSTEM_MESSAGE)
    ]
    
    past_messages = db.fetch_last_messages()
    conversation_history.extend(past_messages)
    
    
    utils.log(f"""
Chat Started.

This LLM based chat can reply to all queries that can be covered by the model's training data.

It has abount 50 MB of text from different free novels. 
Responses related to novel stories will have a high level of bias towards the information from novel.

Chat history is saved and LLM will refer to last {config.MESSAGE_HISTORY_LIMIT} messages.

Type '{config.EXIT_STRING}' to stop.""")
    
    while True:
        user_input = input("User: ")
        
        if user_input.lower() == config.EXIT_STRING:
            utils.log("Exiting...")
            break
            
        if not user_input.strip():
            continue
        
        
        # Save this new msg in database
        db.save_message("user", user_input)
        
        
        # Added RAG in same query mode
        try:
            retrieved_docs = retriever.invoke(user_input)
        except Exception as e:
            utils.log(f"Retrieval Error: {e}")
            retrieved_docs = []
        

        # This is for inline citation requirement 3.2 (c) i.
        context_str = ""
        for idx, doc in enumerate(retrieved_docs, start=1):
            source_file = doc.metadata.get("source", "Unknown")
            context_str += f"\n[{idx}] (Source: {source_file}):\n{doc.page_content}\n"

        rag_prompt = f"""
Context Material:
{context_str}

User Query: {user_input}"""
        
        
        # Append rag_prompt instead of user prompt as we need to reve it after chat response.
        conversation_history.append(HumanMessage(content=rag_prompt))

        try:
            prompt_tokens = model.get_num_tokens_from_messages(conversation_history)
        except Exception:
            prompt_tokens = 0
        
        ai_response = ""
        
        st_time = time.perf_counter()
        utils.log("LLM:")
        try:
            for chunk in model.stream(conversation_history):
                try:
                    token = chunk.content if type(chunk.content) == type("") else chunk.content[0]["text"]
                except:
                    token = ""
                if token:
                    utils.log(token, end="", flush=True)
                    ai_response += token
            
            end_time = time.perf_counter()
            latency = int((end_time - st_time) * 1000)
            
            utils.log("\n")
            
            conversation_history.pop() 
            conversation_history.append(HumanMessage(content=user_input))

            '''
           
            Here we are not saving rag prompt in db. DB is only getting final response. RAG is only in memory.
            
            '''
            
            # Append complete response to history
            conversation_history.append(AIMessage(content=ai_response))
            db.save_message("assistant", ai_response)
            
            # to keep in memory chat history <= 10 : 1 System + 10 User/AI 
            while len(conversation_history) > config.MESSAGE_HISTORY_LIMIT + 1:
                conversation_history.pop(1)
            
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

