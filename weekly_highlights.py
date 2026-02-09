from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from prompt import prompt, prompt_2

# llm = Ollama(base_url="http://207.180.193.215:11434", model="deepseek-r1")


def summary_genrator(a1, a2, a4, a3):
    print("start ......")
    """genrate weekly summary using llm"""
    s = f"This is my user input, give me proper or prefessional summary report based this information {a1},{a2},{a4},{a3}."
    print("s === ", s)
    # Replace with your actual API key
    API_KEY = "AIzaSyDfrbz85taSC2knc1-GHuTtsI47KSfHT0I"

    # # Initialize LLM with API key
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0, api_key=API_KEY
    )

    messages = [SystemMessage(content=prompt_2), HumanMessage(content=s)]
    response = llm.invoke(messages)

    return response.content
