"""
Module for creating Graphs from Nodes.
"""

from nodes import BaseNode
from vertices import VertexInfo


class NodeGraph:
    nodes: dict
    vertices: dict
    vertex_info: dict

    def __init__(self) -> None:
        """
        Constructor.
        """

        self.nodes = {}
        self.vertex_info = {}
        self.vertices = {}
        self.node_vertex_info = {}

    def add_node(self, node: BaseNode) -> None:
        """
        Adds or Updates a Node to the Graph.
        :param node: Node to Add
        :return: None
        """

        self.nodes[node.canonical_id] = node

    def add_vertex(self, source_node: BaseNode, destination_node: BaseNode,
                   field: str | None) -> None:
        """
        Adds a Vertex for two Nodes.
        :param source_node: Source Node
        :param destination_node: Destination Node
        :param field: Field Name associated to the Vertex.
        :return: None
        """

        if field:
            vertex_info = VertexInfo(source_node, destination_node, field)
            self.add_vertex_with_info(source_node, destination_node, vertex_info)
        else:
            self.nodes[source_node.canonical_id] = source_node
            self.nodes[destination_node.canonical_id] = destination_node

            if source_node.canonical_id not in self.vertices:
                self.vertices[source_node.canonical_id] = set()

            if destination_node.canonical_id not in self.vertices:
                self.vertices[destination_node.canonical_id] = set()

            self.vertices[source_node.canonical_id].add(destination_node.canonical_id)
            self.vertices[destination_node.canonical_id].add(source_node.canonical_id)

    def add_vertex_with_info(self, source_node: BaseNode, destination_node: BaseNode,
                             vertex_info: VertexInfo | None) -> None:
        """
        Adds a Vertex to the Graph for two Nodes with Additional Information.
        :param source_node: Source Node
        :param destination_node: Destination Node
        :param vertex_info: Info about the relationship
        :return: None
        """

        self.add_vertex(source_node, destination_node, None)

        if vertex_info:

            if source_node.canonical_id not in self.node_vertex_info:
                self.node_vertex_info[source_node.canonical_id] = set()

            if destination_node.canonical_id not in self.node_vertex_info:
                self.node_vertex_info[destination_node.canonical_id] = set()

            self.vertex_info[vertex_info.vertx_id] = vertex_info
            self.node_vertex_info[source_node.canonical_id].add(vertex_info.vertx_id)
            self.node_vertex_info[destination_node.canonical_id].add(
                vertex_info.vertx_id)

    def get_vertices(self, node: BaseNode) -> set:
        """
        Returns the Canonical IDs related to the provided Node.
        :param node: Node
        :return: Set of Canonical IDs
        """

        return self.vertices.get(node.canonical_id, set())

    def get_node_vertex_info(self, node: BaseNode) -> set:
        """
        Returns the vertex info IDs for a given Node.
        :param node: Node
        :return: Set of Vertex Info IDs
        """

        return self.node_vertex_info.get(node.canonical_id, set())

    def get_vertex_info(self, vertex_id: str) -> VertexInfo | None:
        """
        Retrieves the Vertex Info for a provided ID
        :param vertex_id: Vertex Info ID.
        :return: Vertex Info
        """

        return self.vertex_info.get(vertex_id)

    def find_vertex_info(self, source_node: BaseNode,
                         destination_node: BaseNode) -> VertexInfo | None:
        """
        Retrieves the Vertex Info for a relationship.
        :param source_node: Source Node
        :param destination_node: Destination Node
        :return: Vertex Info
        """

        source_node_vertices = self.node_vertex_info.get(source_node.canonical_id, set())
        for source_node_vertex in source_node_vertices:
            vertex_info = self.get_vertex_info(source_node_vertex)
            if vertex_info and vertex_info.destination_node == destination_node.canonical_id:
                return vertex_info

        return None
