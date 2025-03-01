import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import base64
import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from schemas.schemas import MedicineOCRData
from prompts import OCR_PROMPT


load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MedicineOCRExtractor:
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """Initialize the LLM model and API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logging.error("OPENAI_API_KEY is missing from the environment variables.")
            raise ValueError("OPENAI_API_KEY is required.")
        
        os.environ["OPENAI_API_KEY"] = self.api_key
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    @staticmethod
    def encode_image(image_path):
        """Convert an image file to a base64-encoded string."""
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            logging.info(f"Image {image_path} encoded successfully.")
            return encoded_image
        except Exception as e:
            logging.error(f"Error encoding image: {e}")
            raise

    def extract_medicine_info(self, image_path):
        """Extract medicine information from an image using the LLM model."""
        try:
            image_base64 = self.encode_image(image_path)

            message = HumanMessage(
                content=[
                    {"type": "text", "text": OCR_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ]
            )

            llm_with_tools = self.llm.bind_tools([MedicineOCRData])
            response = llm_with_tools.invoke([message])

            logging.info("Medicine information extraction successful.")
            return response.tool_calls

        except Exception as e:
            logging.error(f"Failed to extract medicine information: {e}")
            return None

# if __name__ == "__main__":
#     extractor = MedicineOCRExtractor()
#     image_path = "dolo.jpg"
#     result = extractor.extract_medicine_info(image_path)
    
#     if result:
#         print(result)
#     else:
#         logging.error("Failed to extract data from the image.")