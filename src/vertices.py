"""
Vertex classes with specific property information between two nodes.
"""

from nodes import BaseNode


class VertexInfo:
    """
    Base Vertex Class
    """

    vertx_id: str
    source_node: str
    destination_node: str
    field_name: str
    meta: dict | str | None

    def __init__(self, source_node: BaseNode, destination_node: BaseNode,
                 field_name: str, **kwargs) -> None:
        """
        Constructor to capture information about the relationship
        :param source_node: Source Node Canonical URL
        :param destination_node: Destination Node Canonical URL
        :param field_name: Relationship Field Name
        :keyword meta: Dictionary or String to add additional information about the relationship.
        """

        self.vertx_id = f"{source_node.canonical_id}_{destination_node.canonical_id}"
        self.source_node = source_node.canonical_id
        self.destination_node = destination_node.canonical_id
        self.field_name = field_name
        self.meta = kwargs.get('meta')
