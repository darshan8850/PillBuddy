from modules import data_create
from modules import details_data
from modules import ocr_data
import os

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Pipeline:
    def __init__(self):
        self.ocr_extractor = ocr_data.MedicineOCRExtractor(api_key=OPENAI_API_KEY)
        self.details_extractor = details_data.MedicineInfoGenerator(api_key=OPENAI_API_KEY)
        self.data_creator = data_create.MedicineDataImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

    def run(self, image_path):
        medicine_info = self.ocr_extractor.extract_medicine_info(image_path)
        if not medicine_info:
            return
        medicine_info=medicine_info[0]
        medicine_data = self.details_extractor.generate_medicine_info(medicine_info)
        if not medicine_data:
            return
        print("Medicine Data: ", medicine_data)
        self.data_creator.import_medicine_data(medicine_data)
        
        return medicine_data
    
if __name__ == "__main__":
    pipeline = Pipeline()
    image_path = "test_data/dolo.jpg"
    result = pipeline.run(image_path)
    print(result)
    
    if result:
        print(result)
    else:
        print("Failed to generate detailed medicine information.")
