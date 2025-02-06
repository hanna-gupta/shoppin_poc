import gradio as gr
from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.tools import Tool
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from tools import tools
from agent import prompt
# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")


# Initialize search and LLM
llm = ChatGroq(model="llama-3.3-70b-specdec", api_key=groq_api_key, temperature=0, max_retries=3)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)



# Initialize Agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, handle_parsing_errors=True)

# Define Gradio chatbot function
def chatbot(input_text):
    memory.chat_memory.add_message(HumanMessage(content=input_text))
    response = agent_executor.invoke({"input": input_text})
    memory.chat_memory.add_message(AIMessage(content=response["output"]))
    return response["output"]

# Launch Gradio UI
gr.Interface(fn=chatbot, inputs="text", outputs="text", title="Shopping Assistant Chatbot").launch()
