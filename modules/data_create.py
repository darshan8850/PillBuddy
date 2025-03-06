import logging
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class MedicineDataImporter:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("MedicineDataImporter initialized")

    def close(self):
        self.driver.close()
        logger.info("Neo4j connection closed")

    def import_medicine_data(self, medicine_data):
        logger.info("Starting medicine data import")
        with self.driver.session() as session:
            session.execute_write(self._create_medicine_nodes, medicine_data)
        logger.info("Medicine data import completed")
        
    def get_none_fields(self, data, parent_key=""):
        none_fields = []

        if isinstance(data, dict): 
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key  
                if value in (None, "", [], {}):  
                    none_fields.append(full_key)
                else:
                    none_fields.extend(self.get_none_fields(value, full_key))  

        elif isinstance(data, list): 
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                none_fields.extend(self.get_none_fields(item, full_key))  

        return none_fields
    
    def filter_none_values(self, data):
        return {k: v for k, v in data.items() if v not in (None, "", [], {})}
    
    def _create_medicine_nodes(self, tx, medicine_data):
        for item in medicine_data:
            if item['name'] == 'MedicineDetailedInfo':
                args = item['args']
                none_fields = self.get_none_fields(item['args'])
                logger.info(f"None fields: {none_fields}")
                logger.info(f"Processing medicine: {args['brand_name']}")
                
                # Create Medicine node
                query = """
                MERGE (m:Medicine {
                    generic_name: $generic_name,
                    brand_name: $brand_name,
                    manufacturer: $manufacturer,
                    power_mg: $power_mg
                })
                """
                tx.run(query, **args)
                logger.debug(f"Created or merged Medicine node for {args['brand_name']}")

                # Create Ingredient nodes and relationships
                if 'ingredients' in args and 'ingredients' not in none_fields:
                    for ingredient in args['ingredients']:
                        query = """
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (i:Ingredient {name: $name})
                        ON CREATE SET i.composition_mg = $composition_mg
                        MERGE (m)-[:CONTAINS]->(i)
                        """
                        tx.run(query, brand_name=args['brand_name'], **ingredient)
                
                # Create Use nodes and relationships
                if 'uses' in args and 'uses' not in none_fields:
                    for use in args['uses']:
                        query = """
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (u:Use {name: $use})
                        MERGE (m)-[:USED_FOR]->(u)
                        """
                        tx.run(query, brand_name=args['brand_name'], use=use)
                
                # Create DosageGuideline node and relationship
                if 'dosage_guidelines' in args and 'dosage_guidelines' not in none_fields:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    MERGE (dg:DosageGuideline {max_daily_dosage: $max_daily_dosage})
                    MERGE (m)-[:HAS_DOSAGE_GUIDELINE]->(dg)
                    """
                    tx.run(query, brand_name=args['brand_name'], **args['dosage_guidelines'])

                # Create OverdoseEffect nodes and relationships
                if 'overdose_effects' in args['dosage_guidelines'] and 'dosage_guidelines.overdose_effects' not in none_fields:
                    for effect in args['dosage_guidelines']['overdose_effects']:
                        query = """
                        MATCH (dg:DosageGuideline)-[:HAS_DOSAGE_GUIDELINE]-(m:Medicine {brand_name: $brand_name})
                        MERGE (oe:OverdoseEffect {name: $effect})
                        MERGE (dg)-[:MAY_CAUSE]->(oe)
                        """
                        tx.run(query, brand_name=args['brand_name'], effect=effect)
                
                # Create AdministrationInstruction nodes and relationships
                if 'administration_instructions' in args and 'administration_instructions' not in none_fields:
                    for key, instruction in args['administration_instructions'].items():
                        query = """
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (ai:AdministrationInstruction {instruction_type: $key, instruction: $instruction})
                        MERGE (m)-[:ADMINISTERED_WITH]->(ai)
                        """
                        tx.run(query, brand_name=args['brand_name'], key=key, instruction=instruction)
                
                # Create Separate Nodes for with_what_to_take and before_or_after_food
                if 'with_what_to_take' in args['administration_instructions'] and 'administration_instructions.with_what_to_take' not in none_fields:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    MERGE (wwt:WithWhatToTake {instruction: $instruction})
                    MERGE (m)-[:TAKEN_WITH]->(wwt)
                    """
                    tx.run(query, brand_name=args['brand_name'], instruction=args['administration_instructions']['with_what_to_take'])

                if 'before_or_after_food' in args['administration_instructions'] and 'administration_instructions.before_or_after_food' not in none_fields:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    MERGE (baf:BeforeOrAfterFood {instruction: $instruction})
                    MERGE (m)-[:TAKEN_BEFORE_OR_AFTER_FOOD]->(baf)
                    """
                    tx.run(query, brand_name=args['brand_name'], instruction=args['administration_instructions']['before_or_after_food'])
                
                # Create MechanismOfAction node and relationships
                if 'mechanism_of_action' in args and 'mechanism_of_action' not in none_fields:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    MERGE (moa:MechanismOfAction {description: $description})
                    MERGE (m)-[:WORKS_BY]->(moa)
                    """
                    tx.run(query, brand_name=args['brand_name'], **args['mechanism_of_action'])
                
                # Create MechanismStep nodes and relationships
                if 'detailed_steps' in args['mechanism_of_action'] and 'mechanism_of_action.detailed_steps' not in none_fields:
                    for step in args['mechanism_of_action']['detailed_steps']:
                        query = """
                        MATCH (moa:MechanismOfAction)-[:WORKS_BY]-(m:Medicine {brand_name: $brand_name})
                        MERGE (ms:MechanismStep {description: $step})
                        MERGE (moa)-[:INVOLVES]->(ms)
                        """
                        tx.run(query, brand_name=args['brand_name'], step=step)
                
                logger.info(f"Finished processing medicine: {args['brand_name']}")

                
                # Create SideEffect nodes and relationships
                if 'side_effects' in args and 'side_effects' not in none_fields:
                    for effect in args['side_effects']:
                        query = """
                        MERGE (se:SideEffect {name: $effect})
                        WITH se
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (m)-[:MAY_CAUSE]->(se)
                        """
                        tx.run(query, brand_name=args['brand_name'], effect=effect)
                
                # Create DrugInteraction nodes and relationships
                if 'drug_interactions' in args and 'drug_interactions' not in none_fields:
                    for interaction in args['drug_interactions']:
                        query = """
                        MERGE (di:DrugInteraction {drug_name: $drug_name})
                        ON CREATE SET di.interaction_type = $interaction_type, di.effects = $effects
                        WITH di
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (m)-[:INTERACTS_WITH]->(di)
                        """
                        tx.run(query, brand_name=args['brand_name'], **interaction)
                
                # Create StorageCondition nodes and relationships
                if 'storage_conditions' in args['storage_and_shelf_life'] and 'storage_and_shelf_life.storage_conditions' not in none_fields:
                    for condition in args['storage_and_shelf_life']['storage_conditions']:
                        query = """
                        MERGE (sc:StorageCondition {condition: $condition})
                        WITH sc
                        MATCH (m:Medicine {brand_name: $brand_name})
                        MERGE (m)-[:STORED_UNDER]->(sc)
                        """
                        tx.run(query, brand_name=args['brand_name'], condition=condition)
                
                # Create ShelfLife node and relationship
                if 'shelf_life' in args['storage_and_shelf_life'] and 'storage_and_shelf_life.shelf_life' not in none_fields:
                    query = """
                    MERGE (sl:ShelfLife {duration: $shelf_life})
                    WITH sl
                    MATCH (m:Medicine {brand_name: $brand_name})
                    MERGE (m)-[:HAS_SHELF_LIFE]->(sl)
                    """
                    tx.run(query, brand_name=args['brand_name'], shelf_life=args['storage_and_shelf_life']['shelf_life'])
                
                logger.info(f"Finished processing medicine: {args['brand_name']}")
