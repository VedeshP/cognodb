from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str
    
class GraphNode(BaseModel):
    id: str
    label: str
    properties: Dict[str, Any]

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    properties: Dict[str, Any]

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ChatResponse(BaseModel):
    answer: str
    cypher_query: str
    graph_data: GraphData
