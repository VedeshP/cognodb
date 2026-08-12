import json
from .db_service import db
from .llm_service import llm_service
from app.schemas.chat_schema import ChatResponse, GraphData, GraphNode, GraphEdge
from neo4j.graph import Node, Relationship

SCHEMA_CONTEXT = """
Nodes:
- Company (properties: name, category, status, founded_year)
- Investor (properties: name)
- Market (properties: name)
- Region (properties: name, country_code)

Relationships:
- (Investor)-[:INVESTED_IN {funding_round_type, amount_usd, year}]->(Company)
- (Company)-[:OPERATES_IN]->(Market)
- (Company)-[:LOCATED_IN]->(Region)
"""

def parse_neo4j_record(record, nodes_dict, edges_dict):
    """Recursively parse neo4j records to extract nodes and edges for the frontend."""
    for value in record.values():
        if isinstance(value, Node):
            node_id = str(value.element_id)
            if node_id not in nodes_dict:
                nodes_dict[node_id] = GraphNode(
                    id=node_id,
                    label=list(value.labels)[0] if value.labels else "Unknown",
                    properties=dict(value)
                )
        elif isinstance(value, Relationship):
            edge_id = str(value.element_id)
            if edge_id not in edges_dict:
                edges_dict[edge_id] = GraphEdge(
                    source=str(value.start_node.element_id),
                    target=str(value.end_node.element_id),
                    type=value.type,
                    properties=dict(value)
                )
        elif isinstance(value, list):
            # Handle paths or lists of nodes/relationships
            for item in value:
                if isinstance(item, (Node, Relationship)):
                    parse_neo4j_record({"dummy": item}, nodes_dict, edges_dict)

async def process_chat_query(user_prompt: str) -> ChatResponse:
    # 1. Generate Cypher query via LLM
    cypher_query = llm_service.generate_cypher(user_prompt, SCHEMA_CONTEXT)
    
    nodes_dict = {}
    edges_dict = {}
    
    # 2. Execute Cypher
    session = db.get_session()
    if session:
        try:
            result = session.run(cypher_query)
            for record in result:
                parse_neo4j_record(record, nodes_dict, edges_dict)
        except Exception as e:
            print(f"Cypher execution error: {e}")
            # Even if it fails, we return the Cypher so the user can debug
    
    # 3. Format Graph Data
    graph_data = GraphData(
        nodes=list(nodes_dict.values()),
        edges=list(edges_dict.values())
    )
    
    # 4. Generate Natural Language Answer
    graph_json = json.dumps(graph_data.model_dump(), default=str)
    answer = llm_service.generate_answer(user_prompt, graph_json)
    
    return ChatResponse(
        answer=answer,
        cypher_query=cypher_query,
        graph_data=graph_data
    )
