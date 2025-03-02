from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()

class MedicineDataImporter:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def import_medicine_data(self, medicine_data):
        with self.driver.session() as session:
            session.execute_write(self._create_medicine_nodes, medicine_data)

    def _create_medicine_nodes(self, tx, medicine_data):
        for item in medicine_data:
            if item['name'] == 'MedicineDetailedInfo':
                args = item['args']
                
                # Create Medicine node
                query = """
                CREATE (m:Medicine {
                    generic_name: $generic_name,
                    brand_name: $brand_name,
                    manufacturer: $manufacturer,
                    power_mg: $power_mg
                })
                """
                tx.run(query, **args)

                # Create Ingredient node and relationship
                for ingredient in args['ingredients']:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (i:Ingredient {name: $name, composition_mg: $composition_mg})
                    CREATE (m)-[:CONTAINS]->(i)
                    """
                    tx.run(query, brand_name=args['brand_name'], **ingredient)

                # Create Use nodes and relationships
                for use in args['uses']:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (u:Use {name: $use})
                    CREATE (m)-[:USED_FOR]->(u)
                    """
                    tx.run(query, brand_name=args['brand_name'], use=use)

                # Create DosageGuideline node and relationship
                query = """
                MATCH (m:Medicine {brand_name: $brand_name})
                CREATE (dg:DosageGuideline {max_daily_dosage: $max_daily_dosage})
                CREATE (m)-[:HAS_DOSAGE_GUIDELINE]->(dg)
                """
                tx.run(query, brand_name=args['brand_name'], **args['dosage_guidelines'])

                # Create OverdoseEffect nodes and relationships
                for effect in args['dosage_guidelines']['overdose_effects']:
                    query = """
                    MATCH (dg:DosageGuideline)-[:HAS_DOSAGE_GUIDELINE]-(m:Medicine {brand_name: $brand_name})
                    CREATE (oe:OverdoseEffect {name: $effect})
                    CREATE (dg)-[:MAY_CAUSE]->(oe)
                    """
                    tx.run(query, brand_name=args['brand_name'], effect=effect)

                # Create AdministrationInstruction nodes and relationships
                for instruction in args['administration_instructions'].items():
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (ai:AdministrationInstruction {instruction: $instruction})
                    CREATE (m)-[:ADMINISTERED_WITH]->(ai)
                    """
                    tx.run(query, brand_name=args['brand_name'], instruction=f"{instruction[0]}: {instruction[1]}")

                # Create MechanismOfAction node and relationship
                query = """
                MATCH (m:Medicine {brand_name: $brand_name})
                CREATE (moa:MechanismOfAction {description: $description})
                CREATE (m)-[:WORKS_BY]->(moa)
                """
                tx.run(query, brand_name=args['brand_name'], **args['mechanism_of_action'])

                # Create MechanismStep nodes and relationships
                for step in args['mechanism_of_action']['detailed_steps']:
                    query = """
                    MATCH (moa:MechanismOfAction)-[:WORKS_BY]-(m:Medicine {brand_name: $brand_name})
                    CREATE (ms:MechanismStep {description: $step})
                    CREATE (moa)-[:INVOLVES]->(ms)
                    """
                    tx.run(query, brand_name=args['brand_name'], step=step)

                # Create SideEffect nodes and relationships
                for effect in args['side_effects']:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (se:SideEffect {name: $effect})
                    CREATE (m)-[:MAY_CAUSE]->(se)
                    """
                    tx.run(query, brand_name=args['brand_name'], effect=effect)

                # Create DrugInteraction nodes and relationships
                for interaction in args['drug_interactions']:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (di:DrugInteraction {
                        drug_name: $drug_name,
                        interaction_type: $interaction_type,
                        effects: $effects
                    })
                    CREATE (m)-[:INTERACTS_WITH]->(di)
                    """
                    tx.run(query, brand_name=args['brand_name'], **interaction)

                # Create StorageCondition nodes and relationships
                for condition in args['storage_and_shelf_life']['storage_conditions']:
                    query = """
                    MATCH (m:Medicine {brand_name: $brand_name})
                    CREATE (sc:StorageCondition {condition: $condition})
                    CREATE (m)-[:STORED_UNDER]->(sc)
                    """
                    tx.run(query, brand_name=args['brand_name'], condition=condition)

                # Create ShelfLife node and relationship
                query = """
                MATCH (m:Medicine {brand_name: $brand_name})
                CREATE (sl:ShelfLife {duration: $shelf_life})
                CREATE (m)-[:HAS_SHELF_LIFE]->(sl)
                """
                tx.run(query, brand_name=args['brand_name'], shelf_life=args['storage_and_shelf_life']['shelf_life'])


NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

importer = MedicineDataImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

medicine_data = [{'name': 'MedicineDetailedInfo', 'args': {'generic_name': 'Paracetamol', 'brand_name': 'Dolo-650', 'manufacturer': 'Micro Labs Limited', 'power_mg': '650', 'ingredients': [{'name': 'Paracetamol', 'composition_mg': 650}], 'uses': ['Pain relief', 'Fever reduction'], 'dosage_guidelines': {'max_daily_dosage': '4000 mg', 'overdose_effects': ['Liver damage', 'Nausea', 'Vomiting', 'Confusion']}, 'administration_instructions': {'with_what_to_take': ['Water'], 'before_or_after_food': 'After food'}, 'mechanism_of_action': {'description': 'Paracetamol works by inhibiting the production of prostaglandins in the brain, which are responsible for pain and fever.', 'detailed_steps': ['Paracetamol is absorbed from the gastrointestinal tract.', 'It is metabolized in the liver to form active metabolites.', 'These metabolites inhibit the cyclooxygenase (COX) enzymes, reducing the synthesis of prostaglandins.', 'Lower levels of prostaglandins lead to decreased pain and fever.']}, 'side_effects': ['Nausea', 'Rash', 'Liver toxicity (in overdose)'], 'drug_interactions': [{'drug_name': 'Warfarin', 'interaction_type': 'synergistic', 'effects': 'Increased risk of bleeding'}, {'drug_name': 'Alcohol', 'interaction_type': 'dangerous', 'effects': 'Increased risk of liver damage'}], 'storage_and_shelf_life': {'storage_conditions': ['Store at room temperature', 'Keep away from moisture'], 'shelf_life': '3 years'}}, 'id': 'call_SUZKDbbbQjZwPZ1SG1uMDuTW', 'type': 'tool_call'}]

importer.import_medicine_data(medicine_data)
importer.close()
