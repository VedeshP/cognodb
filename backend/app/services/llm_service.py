import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LLMService:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            # Use gemini-1.5-pro for better code/cypher generation
            self.model = genai.GenerativeModel('gemini-3.6-flash')
        else:
            print("Warning: GEMINI_API_KEY not found. LLM features will be mocked.")
            self.model = None
            
    def generate_cypher(self, user_prompt: str, schema_context: str) -> str:
        if not self.model:
            return "MATCH (c:Company)-[:OPERATES_IN]->(m:Market) RETURN c, m LIMIT 10" # Mock query
            
        prompt = f"""
        You are an expert Graph Database Cypher query generator for Neo4j.
        Based on the following graph schema, generate a Cypher query to answer the user's question.
        
        Graph Schema:
        {schema_context}
        
        Rules:
        1. ONLY output the raw Cypher query. No markdown, no explanations, no backticks.
        2. Always use LIMIT 50 to prevent massive payloads.
        3. Ensure you return the nodes and relationships needed to answer the question, e.g., RETURN n, r, m.
        4. Use case-insensitive matching where appropriate (e.g., toLower(c.name) CONTAINS toLower('value')).
        
        User Question: {user_prompt}
        Cypher Query:
        """
        
        response = self.model.generate_content(prompt)
        cypher = response.text.strip().replace("```cypher", "").replace("```", "").strip()
        return cypher

    def generate_answer(self, user_prompt: str, graph_data_json: str) -> str:
        if not self.model:
            return "This is a mocked answer because no API key was provided. The query was executed successfully."
            
        prompt = f"""
        You are a helpful AI assistant exploring a Tech & Startup Ecosystem Knowledge Graph.
        A user asked a question, and we retrieved the following JSON data from our Graph Database to help answer it.
        
        Graph Data Context:
        {graph_data_json}
        
        User Question: {user_prompt}
        
        Please provide a conversational, natural language answer to the user based ONLY on the provided Graph Data Context. 
        If the data is empty or doesn't answer the question, say so politely. Do not hallucinate external information.
        Format your response cleanly.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

llm_service = LLMService()
