from modules import data_create
from modules import details_data
from modules import ocr_data


class Pipeline:
    def __init__(self):
        self.ocr_extractor = ocr_data.MedicineOCRExtractor()
        self.details_extractor = details_data.MedicineDetailsExtractor()
        self.data_creator = data_create.MedicineDataCreator()

    def run(self, image_path):
        medicine_info = self.ocr_extractor.extract_medicine_info(image_path)
        if not medicine_info:
            return
        medicine_info=list(medicine_info[0])
        medicine_data = self.details_extractor.generate_medicine_info(medicine_info)
        if not medicine_data:
            return

        self.data_creator.import_medicine_data(medicine_data)