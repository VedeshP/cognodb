import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")
COGNODB_USER = "cognodb"

class Database:
    def __init__(self):
        self.driver = None

    def connect(self):
        if not COGNODB_URI or not COGNODB_PASSWORD:
            print("Warning: COGNODB_URI or COGNODB_PASSWORD environment variables not set.")
            return

        try:
            self.driver = GraphDatabase.driver(COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD))
            self.driver.verify_connectivity()
            print("Successfully connected to CognoDB.")
        except Exception as e:
            print(f"Failed to connect to CognoDB: {e}")
            self.driver = None

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def get_session(self):
        if self.driver is None:
            self.connect()
            
        if self.driver is None:
            raise Exception("Database driver is not initialized. Please check your COGNODB credentials.")
            
        return self.driver.session()

# Singleton instance
db = Database()
