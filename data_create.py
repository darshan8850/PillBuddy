from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()


NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

print(NEO4J_PASSWORD)


with GraphDatabase.driver(NEO4J_URI,auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
    driver.verify_connectivity()