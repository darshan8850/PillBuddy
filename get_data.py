import os
import base64
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain
from schemas import MedicineDetailedInfo
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def load_image(image_path):

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}

image_data = load_image("dolo.jpg")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)
message = HumanMessage(
    content=[
        {"type": "text", "text": "You are a medical AI assistant specializing in pharmacology and clinical medicine. Based on the given structured data about a medicine, extract and provide detailed information in the specified format."},
        {
            "type": "text",
            "text": "{'name': 'MedicineOCRData', 'args': {'generic_name': 'Paracetamol', 'brand_name': 'Dolo-650', 'manufacturer': 'Micro Labs Limited', 'power_mg': '650', 'ingredients': [{'name': 'Paracetamol', 'composition_mg': 650}]}",
        },
    ],
)




llm_with_tools = llm.bind_tools([MedicineDetailedInfo])
response = llm_with_tools.invoke([message])
print(response.tool_calls)