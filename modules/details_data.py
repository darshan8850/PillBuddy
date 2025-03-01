import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from schemas.schemas import MedicineDetailedInfo
from prompts import INFO_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MedicineInfoGenerator:
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """Initialize the LLM model and API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logging.error("OPENAI_API_KEY is missing from the environment variables.")
            raise ValueError("OPENAI_API_KEY is required.")
        
        os.environ["OPENAI_API_KEY"] = self.api_key
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def generate_medicine_info(self, medicine_data):
        """Generate detailed medicine information from structured OCR data."""
        try:
            message = HumanMessage(
                content=[
                    {"type": "text", "text": INFO_PROMPT},
                    {"type": "text", "text": f"{medicine_data}"},
                ]
            )

            llm_with_tools = self.llm.bind_tools([MedicineDetailedInfo])
            response = llm_with_tools.invoke([message])

            logging.info("Medicine detailed information generation successful.")
            return response.tool_calls

        except Exception as e:
            logging.error(f"Failed to generate medicine information: {e}")
            return None


# if __name__ == "__main__":
#     medicine_data = {
#         "name": "MedicineOCRData",
#         "args": {
#             "generic_name": "Paracetamol",
#             "brand_name": "Dolo-650",
#             "manufacturer": "Micro Labs Limited",
#             "power_mg": "650",
#             "ingredients": [{"name": "Paracetamol", "composition_mg": 650}],
#         },
#     }

#     generator = MedicineInfoGenerator()
#     result = generator.generate_medicine_info(medicine_data)

#     if result:
#         print(result)
#     else:
#         logging.error("Failed to generate detailed medicine information.")
