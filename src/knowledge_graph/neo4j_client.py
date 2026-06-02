"""
Neo4j client for managing knowledge graph database operations.
Handles connection, node creation, relationship creation, and queries.
"""

from neo4j import GraphDatabase
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import os


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection"""
    uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "password")


class Neo4jClient:
    """
    Client for interacting with Neo4j knowledge graph database.
    """
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """
        Initialize Neo4j client.
        
        Args:
            config: Neo4jConfig object with connection details
        """
        if config is None:
            config = Neo4jConfig()
        
        self.config = config
        self.driver = None
        self.session = None
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password)
            )
            self.driver.verify_connectivity()
            print("✓ Connected to Neo4j database")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            return False
    
    def disconnect(self):
        """Close connection to Neo4j database."""
        if self.driver:
            self.driver.close()
            print("✓ Disconnected from Neo4j")
    
    def _run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records
        """
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            return []
    
    def create_node(
        self,
        label: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        Create a node in the knowledge graph.
        
        Args:
            label: Node label (e.g., 'Organization', 'Person', 'Date')
            properties: Node properties (name, value, etc.)
            
        Returns:
            True if successful
        """
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"CREATE (n:{label} {{{props_str}}})"
        
        try:
            self._run_query(query, properties)
            return True
        except Exception as e:
            print(f"✗ Failed to create node: {e}")
            return False
    
    def create_relationship(
        self,
        source_label: str,
        source_property: str,
        source_value: str,
        relation_type: str,
        target_label: str,
        target_property: str,
        target_value: str,
        relation_properties: Optional[Dict] = None
    ) -> bool:
        """
        Create a relationship between two nodes.
        
        Args:
            source_label: Label of source node
            source_property: Property name to match source
            source_value: Property value of source
            relation_type: Type of relationship
            target_label: Label of target node
            target_property: Property name to match target
            target_value: Property value of target
            relation_properties: Optional properties for the relationship
            
        Returns:
            True if successful
        """
        if relation_properties is None:
            relation_properties = {}
        
        props_str = ""
        if relation_properties:
            props_str = " {" + ", ".join([f"{k}: ${k}" for k in relation_properties.keys()]) + "}"
        
        query = f"""
        MATCH (a:{source_label} {{{source_property}: $source_value}})
        MATCH (b:{target_label} {{{target_property}: $target_value}})
        CREATE (a)-[r:{relation_type}{props_str}]->(b)
        RETURN r
        """
        
        params = {
            "source_value": source_value,
            "target_value": target_value,
            **relation_properties
        }
        
        try:
            self._run_query(query, params)
            return True
        except Exception as e:
            print(f"✗ Failed to create relationship: {e}")
            return False
    
    def node_exists(self, label: str, property_name: str, property_value: str) -> bool:
        """
        Check if a node exists.
        
        Args:
            label: Node label
            property_name: Property to match
            property_value: Property value
            
        Returns:
            True if node exists
        """
        query = f"MATCH (n:{label} {{{property_name}: $value}}) RETURN COUNT(n) as count"
        
        try:
            result = self._run_query(query, {"value": property_value})
            return result[0]["count"] > 0 if result else False
        except Exception as e:
            print(f"✗ Failed to check node existence: {e}")
            return False
    
    def get_node_relationships(
        self,
        label: str,
        property_name: str,
        property_value: str
    ) -> List[Dict]:
        """
        Get all relationships for a node.
        
        Args:
            label: Node label
            property_name: Property to match
            property_value: Property value
            
        Returns:
            List of relationship information
        """
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})-[r]->(m)
        RETURN n.name as source, type(r) as relation_type, m.name as target
        """
        
        try:
            return self._run_query(query, {"value": property_value})
        except Exception as e:
            print(f"✗ Failed to get relationships: {e}")
            return []
    
    def find_paths(
        self,
        start_label: str,
        start_value: str,
        end_label: str,
        end_value: str,
        max_depth: int = 3
    ) -> List[Dict]:
        """
        Find paths between two nodes.
        
        Args:
            start_label: Starting node label
            start_value: Starting node identifier
            end_label: Ending node label
            end_value: Ending node identifier
            max_depth: Maximum relationship depth
            
        Returns:
            List of paths found
        """
        query = f"""
        MATCH (start:{start_label} {{name: $start_value}})
        MATCH (end:{end_label} {{name: $end_value}})
        MATCH p = shortestPath((start)-[*1..{max_depth}]->(end))
        RETURN p
        """
        
        try:
            return self._run_query(query, {
                "start_value": start_value,
                "end_value": end_value
            })
        except Exception as e:
            print(f"✗ Failed to find paths: {e}")
            return []
    
    def query_entities(
        self,
        entity_type: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query all entities of a specific type.
        
        Args:
            entity_type: Type of entity to query
            limit: Maximum results to return
            
        Returns:
            List of entities
        """
        query = f"MATCH (n:{entity_type}) RETURN n LIMIT {limit}"
        
        try:
            return self._run_query(query)
        except Exception as e:
            print(f"✗ Failed to query entities: {e}")
            return []
    
    def clear_database(self) -> bool:
        """
        Delete all nodes and relationships (use with caution!).
        
        Returns:
            True if successful
        """
        query = "MATCH (n) DETACH DELETE n"
        
        try:
            self._run_query(query)
            print("✓ Database cleared")
            return True
        except Exception as e:
            print(f"✗ Failed to clear database: {e}")
            return False
