import logging
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
import os

class Neo4jQueryHandler:
    def __init__(self, neo4j_url, neo4j_username, neo4j_password, openai_api_key):

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.logger.info("Initializing Neo4jGraph connection")
        self.enhanced_graph = Neo4jGraph(
            url=neo4j_url,
            username=neo4j_username,
            password=neo4j_password,
            enhanced_schema=True,
        )
        
        self.logger.info("Neo4jGraph connection established")
        self.logger.debug(f"Graph schema: {self.enhanced_graph.schema}")
        
        self.logger.info("Refreshing graph schema")
        self.enhanced_graph.refresh_schema()
        
        self.logger.info("Initializing GraphCypherQAChain")
        self.chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0),
            graph=self.enhanced_graph,
            verbose=True,
            allow_dangerous_requests=True
        )
        self.logger.info("GraphCypherQAChain initialized")

    def query(self, question):
        self.logger.info(f"Processing query: {question}")
        try:
            result = self.chain.invoke({"query": question})
            self.logger.info("Query processed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

# if __name__ == "__main__":
#     handler = Neo4jQueryHandler(
#         neo4j_url="bolt://localhost:7687",
#         neo4j_username="neo4j",
#         neo4j_password="","
#         openai_api_key=""
#     )
    
#     result = handler.query("In what cases should I take Dolo-650?")
#     print(result)
