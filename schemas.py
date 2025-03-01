from typing import List, Optional
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str = Field(..., description="Name of the ingredient")
    composition_mg: float = Field(..., description="Composition of the ingredient in mg")

class DosageGuideline(BaseModel):
    max_daily_dosage: Optional[str] = Field(None, description="Maximum allowed dosage per day")
    overdose_effects: Optional[List[str]] = Field(None, description="Effects and consequences of an overdose")

class AdministrationInstructions(BaseModel):
    with_what_to_take: Optional[List[str]] = Field(None, description="List of liquids or foods with which the medicine should be taken (e.g., water, milk)")
    before_or_after_food: Optional[str] = Field(None, description="Whether to take before or after food")

class MechanismOfAction(BaseModel):
    description: str = Field(..., description="How the medicine works in the body")
    detailed_steps: List[str] = Field(..., description="Step-by-step mechanism of action")

class DrugInteraction(BaseModel):
    drug_name: str = Field(..., description="Name of the drug that interacts")
    interaction_type: str = Field(..., description="Type of interaction (e.g., synergistic, antagonistic, dangerous)")
    effects: str = Field(..., description="Effects of the interaction")

class StorageAndShelfLife(BaseModel):
    storage_conditions: Optional[List[str]] = Field(None, description="Recommended storage conditions (e.g., room temperature, refrigeration)")
    shelf_life: Optional[str] = Field(None, description="Shelf life of the medicine")

class MedicineOCRData(BaseModel):
    generic_name: str = Field(..., description="Generic name of the medicine")
    brand_name: Optional[str] = Field(None, description="Brand name of the medicine")
    manufacturer: Optional[str] = Field(None, description="Name of the manufacturer of the medicine")
    power_mg: Optional[str] = Field(None, description="Power or dosage of the medicine in mg")
    ingredients: List[Ingredient] = Field(..., description="List of all active ingredients with their composition in mg")
    storage_and_shelf_life: StorageAndShelfLife = Field(..., description="Storage recommendations and shelf life of the medicine")

class MedicineDetailedInfo(BaseModel):
    generic_name: str = Field(..., description="Generic name of the medicine")
    brand_name: Optional[str] = Field(None, description="Brand name of the medicine")
    manufacturer: Optional[str] = Field(None, description="Name of the manufacturer of the medicine")
    power_mg: Optional[str] = Field(None, description="Power or dosage of the medicine in mg")
    ingredients: List[Ingredient] = Field(..., description="List of all active ingredients with their composition in mg")
    uses: List[str] = Field(..., description="List of medical conditions or symptoms this medicine is used for")
    dosage_guidelines: DosageGuideline = Field(..., description="Dosage information including maximum daily dose and overdose effects")
    administration_instructions: AdministrationInstructions = Field(..., description="Guidelines on how to take the medicine")
    
    mechanism_of_action: MechanismOfAction = Field(..., description="Detailed mechanism of action of the medicine")
    side_effects: List[str] = Field(..., description="List of possible side effects from taking the medicine")
    drug_interactions: List[DrugInteraction] = Field(..., description="List of known drug interactions with other medicines")
    
    storage_and_shelf_life: StorageAndShelfLife = Field(..., description="Storage recommendations and shelf life of the medicine")

