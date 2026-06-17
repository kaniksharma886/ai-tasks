import os

# Model configuration
OPENAI_BASE_URL = "https://aiunifier.lemonforest-8302e80c.australiaeast.azurecontainerapps.io"
MODEL_NAME = "gpt-5.4-nano" 
#os.environ["OPENAI_API_KEY"] = ""          # will add later via export to avoid accidental commit

MODEL_TEMPERATURE = 0.4

COST_PER_INPUT_TOKEN = 0.20 / 1000000       # Found on https://developers.openai.com/api/docs/pricing
COST_PER_OUTPUT_TOKEN = 1.25 / 1000000


# General configuration
EXIT_STRING = "exit"
MESSAGE_HISTORY_LIMIT = 10                  # 1 System msg and 10 chat history messages

DB_DIR = "./db"
DB_PATH = f"{DB_DIR}/chat_history.db"
RAG_DIR = "./documents"


COLLECTION_NAME = "file_collection"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5" # BAAI/bge-small-en-v1.5 is as I cannot access open ai embedding models here. This is one of the lightest built on c++

TOP_K_RESULTS = 5

