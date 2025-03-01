import os
import base64
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import chain
from schemas import Ingredient, MedicineOCRData
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
        {"type": "text", "text": "You are a medicine OCR model. Please extract the following information from the image. Don't forget to include the brand name and power of the medicine if available. Don't add any information that is not present in the image."},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data['image']}"},
        },
    ],
)

llm_with_tools = llm.bind_tools([MedicineOCRData])
response = llm_with_tools.invoke([message])
print(response.tool_calls)