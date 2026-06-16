import os

# Model configuration
OPENAI_BASE_URL = "https://aiunifier.lemonforest-8302e80c.australiaeast.azurecontainerapps.io"

MODEL_NAME = "gpt-5.4-nano" 

os.environ["OPENAI_API_KEY"] = ""       # will add later

MODEL_TEMPRATURE = 0.4



# General configuration
EXIT_STRING = "exit"