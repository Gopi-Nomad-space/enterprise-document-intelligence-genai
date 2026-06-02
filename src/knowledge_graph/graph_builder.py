"""
Knowledge graph builder for creating and populating Neo4j graph from extracted entities and relations.
"""

from typing import Dict, List, Optional
from src.knowledge_graph.neo4j_client import Neo4jClient
from src.extraction.entity_extractor import EntityExtraction
from src.extraction.relation_extractor import RelationExtraction


class KnowledgeGraphBuilder:
    """
    Builder class for constructing knowledge graphs from extracted entities and relations.
    """
    
    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        """
        Initialize graph builder.
        
        Args:
            neo4j_client: Neo4jClient instance (creates new one if None)
        """
        self.neo4j = neo4j_client or Neo4jClient()
        self.created_nodes = set()  # Track created nodes to avoid duplicates
    
    def add_entities_to_graph(
        self,
        entity_extraction: EntityExtraction,
        document_name: str
    ) -> bool:
        """
        Add extracted entities to the knowledge graph.
        
        Args:
            entity_extraction: EntityExtraction object with extracted entities
            document_name: Name of the source document
            
        Returns:
            True if successful
        """
        try:
            # Add organizations
            for org in entity_extraction.organizations:
                node_key = f"Organization:{org}"
                if node_key not in self.created_nodes:
                    self.neo4j.create_node(
                        "Organization",
                        {"name": org, "document": document_name}
                    )
                    self.created_nodes.add(node_key)
            
            # Add persons
            for person in entity_extraction.persons:
                node_key = f"Person:{person}"
                if node_key not in self.created_nodes:
                    self.neo4j.create_node(
                        "Person",
                        {"name": person, "document": document_name}
                    )
                    self.created_nodes.add(node_key)
            
            # Add dates
            for date in entity_extraction.dates:
                node_key = f"Date:{date}"
                if node_key not in self.created_nodes:
                    self.neo4j.create_node(
                        "Date",
                        {"name": date, "document": document_name}
                    )
                    self.created_nodes.add(node_key)
            
            # Add clauses
            for clause in entity_extraction.clauses:
                node_key = f"Clause:{clause}"
                if node_key not in self.created_nodes:
                    self.neo4j.create_node(
                        "Clause",
                        {"name": clause, "document": document_name}
                    )
                    self.created_nodes.add(node_key)
            
            return True
            
        except Exception as e:
            print(f"✗ Error adding entities to graph: {e}")
            return False
    
    def add_relations_to_graph(
        self,
        relation_extraction: RelationExtraction
    ) -> bool:
        """
        Add extracted relations to the knowledge graph.
        
        Args:
            relation_extraction: RelationExtraction object with extracted relations
            
        Returns:
            True if successful
        """
        try:
            for relation in relation_extraction.relations:
                source = relation.source
                target = relation.target
                rel_type = relation.relation_type.upper()
                
                # Infer entity types and create relationships
                # This is a simplified approach - in production you'd have more sophisticated type detection
                source_label = self._infer_entity_type(source)
                target_label = self._infer_entity_type(target)
                
                if source_label and target_label:
                    self.neo4j.create_relationship(
                        source_label,
                        "name",
                        source,
                        rel_type,
                        target_label,
                        "name",
                        target
                    )
            
            return True
            
        except Exception as e:
            print(f"✗ Error adding relations to graph: {e}")
            return False
    
    def build_from_all_extractions(
        self,
        entities_by_doc: Dict[str, List[EntityExtraction]],
        relations_by_doc: Dict[str, List[RelationExtraction]]
    ) -> bool:
        """
        Build complete knowledge graph from all extracted entities and relations.
        
        Args:
            entities_by_doc: Dictionary of document names to entity extractions
            relations_by_doc: Dictionary of document names to relation extractions
            
        Returns:
            True if successful
        """
        try:
            print("\n📊 Building knowledge graph...")
            
            # Add all entities first
            print("Adding entities...")
            for doc_name, extractions in entities_by_doc.items():
                for extraction in extractions:
                    self.add_entities_to_graph(extraction, doc_name)
            
            # Then add relations
            print("Adding relationships...")
            for doc_name, extractions in relations_by_doc.items():
                for extraction in extractions:
                    self.add_relations_to_graph(extraction)
            
            print(f"✓ Knowledge graph built with {len(self.created_nodes)} entities")
            return True
            
        except Exception as e:
            print(f"✗ Error building knowledge graph: {e}")
            return False
    
    def query_graph_stats(self) -> Dict:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary with graph statistics
        """
        try:
            organizations = self.neo4j.query_entities("Organization")
            persons = self.neo4j.query_entities("Person")
            dates = self.neo4j.query_entities("Date")
            clauses = self.neo4j.query_entities("Clause")
            
            return {
                "organizations": len(organizations),
                "persons": len(persons),
                "dates": len(dates),
                "clauses": len(clauses),
                "total_entities": len(organizations) + len(persons) + len(dates) + len(clauses)
            }
        except Exception as e:
            print(f"✗ Error querying graph stats: {e}")
            return {}
    
    def find_entity_connections(self, entity_name: str) -> List[Dict]:
        """
        Find all connections for a specific entity in the graph.
        
        Args:
            entity_name: Name of entity to search for
            
        Returns:
            List of connections
        """
        connections = []
        
        for label in ["Organization", "Person", "Date", "Clause"]:
            rels = self.neo4j.get_node_relationships(label, "name", entity_name)
            connections.extend(rels)
        
        return connections
    
    @staticmethod
    def _infer_entity_type(entity: str) -> Optional[str]:
        """
        Infer entity type from string (simple heuristic).
        
        Args:
            entity: Entity string
            
        Returns:
            Inferred entity type label
        """
        # Simple heuristics - in production this would be more sophisticated
        lower_entity = entity.lower()
        
        if any(keyword in lower_entity for keyword in ["corp", "inc", "llc", "limited", "ltd", "company", "organization"]):
            return "Organization"
        elif any(keyword in lower_entity for keyword in ["clause", "section", "provision", "article", "paragraph"]):
            return "Clause"
        elif any(keyword in lower_entity for keyword in ["january", "february", "march", "april", "may", "june", 
                                                          "july", "august", "september", "october", "november", "december",
                                                          "2023", "2024", "2025", "2026"]):
            return "Date"
        else:
            # Default to Person for other entities
            return "Person"
