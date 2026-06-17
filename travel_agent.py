from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent   #Langchain has chnaged to langchain_classic for these functions
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import prompt_config as pconfig
from typing import List, Type
import config
import utils
import json
import os


class Activity(BaseModel):
    time_of_day: str = Field(description="Morning, Afternoon, Evening")
    description: str = Field(description="Details of what to do and where")
    cost: float = Field(description="Cost of the activity")


class DayItinerary(BaseModel):
    day_number: int = Field(description="Day 1, Day 2...")
    activities: List[Activity]


class TripItinerary(BaseModel):
    destination: str
    total_cost: float
    itinerary: List[DayItinerary]
    

@tool
def get_weather(location: str) -> str:
    """Use this tool to find weather information of a given location"""
    return f"Weather in {location} is sunny. Average temprature is 18°C."
    
    
@tool
def search_attractions(location: str, budget: float) -> str:
    """Use this tools to search for popular attractions, ticket price and activities within a given budget."""
    # Mocking database lookup
    attractions = [
        {"name": "Cycling", "cost": 40, "type": "Outdoor"},
        {"name": "Art Gallery", "cost": 0, "type": "Indoor"},
        {"name": "Auckland cruise trip", "cost": 200, "type": "Indoor"},
        {"name": "Horse riding", "cost": 60, "type": "Outdoor"}
    ]
    
    affordable = [a for a in attractions if a["cost"] <= budget]
    return json.dumps({"location": location, "place": affordable})


def run_trip_planner_agent(user_prompt: str):
    tools = [get_weather, search_attractions]

    try:
        model = init_chat_model(config.MODEL_NAME, temperature=config.MODEL_TEMPERATURE, base_url=config.OPENAI_BASE_URL)
    except Exception as e:
        utils.log(f"Error : Failed to load model {config.MODEL_NAME}': {e}")
        return

    
    model_with_structure = model.with_structured_output(TripItinerary)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", pconfig.SYSTEM_MESSAGE_TRAVEL_AGENT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    
    travel_agent = create_tool_calling_agent(model, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=travel_agent, 
        tools=tools, 
        verbose=True, # To make scratch-pad visible in logs
        handle_parsing_errors=True)
        
    agent_step_output = agent_executor.invoke({"input": user_prompt})

    int_resp = agent_step_output['output']
    utils.log("LLM Resp : ",json.dumps(int_resp, indent=4))
    
    # Re-invoking to ensure output format is aligned with JSON
    final_structured_json = model_with_structure.invoke(
        f"Based on your research for the prompt '{user_prompt}', format the final itinerary: {agent_step_output['output']}"
    )    
    return final_structured_json


if __name__ == "__main__":
    prompt = "Plan a 2-day trip to Auckland for under NZ$500"
    result = run_trip_planner_agent(prompt)
    
    utils.log("Final Resp : ",json.dumps(result.model_dump(), indent=4))