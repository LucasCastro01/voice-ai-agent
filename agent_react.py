from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

def init_llm():
    return ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-120b"
    )

@tool
def consultar_saldo():
    """Retorna o saldo de horas do funcionário"""
    return "Seu saldo de horas é 120 horas positivas."

agent = create_agent(
    model=init_llm(),
    tools=[consultar_saldo],
    checkpointer=InMemorySaver()
)

def perguntar_ia(texto):
    response = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": texto}
            ]
        },
        {
            "configurable": {"thread_id": "thread-1"}
        }
    )

    return response["messages"][-1].content