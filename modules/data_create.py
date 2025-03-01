from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()


NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

with GraphDatabase.driver(NEO4J_URI,auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
    driver.verify_connectivity()
    
queries = [
    # Symptoms
    'CREATE (:Symptom {name: "Headache"})',
    'CREATE (:Symptom {name: "Cold"})',
    'CREATE (:Symptom {name: "Congestion"})',
    'CREATE (:Symptom {name: "Cough"})',
    'CREATE (:Symptom {name: "Fever"})',
    'CREATE (:Symptom {name: "Sore Throat"})',

    # Ingredients
    'CREATE (:Ingredient {name: "Paracetamol", dosage: "500mg"})',
    'CREATE (:Ingredient {name: "Ibuprofen", dosage: "200mg"})',
    'CREATE (:Ingredient {name: "Caffeine", dosage: "65mg"})',
    'CREATE (:Ingredient {name: "Pseudoephedrine", dosage: "30mg"})',
    'CREATE (:Ingredient {name: "Chlorpheniramine", dosage: "4mg"})',
    'CREATE (:Ingredient {name: "Dextromethorphan", dosage: "10mg"})',

    # Medicines
    'CREATE (:Medicine {name: "Tylenol Cold & Flu", brand: "Tylenol"})',
    'CREATE (:Medicine {name: "Advil Cold & Sinus", brand: "Advil"})',
    'CREATE (:Medicine {name: "Nyquil Severe", brand: "Nyquil"})',
    'CREATE (:Medicine {name: "DayQuil", brand: "DayQuil"})',
    'CREATE (:Medicine {name: "Excedrin Migraine", brand: "Excedrin"})',
    'CREATE (:Medicine {name: "Generic Cold Medicine", brand: "PharmaCo"})',
    'CREATE (:Medicine {name: "Multi-Symptom Relief", brand: "ReliefCo"})'
]


for query in queries:
    records, summary, keys = driver.execute_query(query, database_="neo4j")

relationships = queries = [
    # Symptoms require ingredients
    'MATCH (s:Symptom {name: "Headache"}), (i:Ingredient {name: "Ibuprofen"}) CREATE (s)-[:REQUIRES]->(i)',
    'MATCH (s:Symptom {name: "Cold"}), (i:Ingredient {name: "Pseudoephedrine"}) CREATE (s)-[:REQUIRES]->(i)',
    'MATCH (s:Symptom {name: "Congestion"}), (i:Ingredient {name: "Pseudoephedrine"}) CREATE (s)-[:REQUIRES]->(i)',
    'MATCH (s:Symptom {name: "Fever"}), (i:Ingredient {name: "Paracetamol"}) CREATE (s)-[:REQUIRES]->(i)',
    'MATCH (s:Symptom {name: "Cough"}), (i:Ingredient {name: "Dextromethorphan"}) CREATE (s)-[:REQUIRES]->(i)',
    'MATCH (s:Symptom {name: "Sore Throat"}), (i:Ingredient {name: "Chlorpheniramine"}) CREATE (s)-[:REQUIRES]->(i)',

    # Medicines contain ingredients
    'MATCH (m:Medicine {name: "Tylenol Cold & Flu"}), (i:Ingredient {name: "Paracetamol"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Tylenol Cold & Flu"}), (i:Ingredient {name: "Dextromethorphan"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Advil Cold & Sinus"}), (i:Ingredient {name: "Ibuprofen"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Advil Cold & Sinus"}), (i:Ingredient {name: "Pseudoephedrine"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Nyquil Severe"}), (i:Ingredient {name: "Dextromethorphan"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Nyquil Severe"}), (i:Ingredient {name: "Chlorpheniramine"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Excedrin Migraine"}), (i:Ingredient {name: "Ibuprofen"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Excedrin Migraine"}), (i:Ingredient {name: "Caffeine"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Multi-Symptom Relief"}), (i:Ingredient {name: "Paracetamol"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Multi-Symptom Relief"}), (i:Ingredient {name: "Pseudoephedrine"}) CREATE (m)-[:CONTAINS]->(i)',
    'MATCH (m:Medicine {name: "Multi-Symptom Relief"}), (i:Ingredient {name: "Chlorpheniramine"}) CREATE (m)-[:CONTAINS]->(i)'
]

for query in relationships:
    records, summary, keys = driver.execute_query(query, database_="neo4j")
