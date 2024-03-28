"""
Vertex classes with specific property information between two nodes.
"""

from nodes import CodeNode, BaseNode, IdentifierNode, NameNode


class BaseVertex:
    """
    Base Vertex Class
    """

    vertx_id: str
    source_node: str
    destination_node: str
    field_name: str

    def __init__(self, vertx_id: str, source_node: str, destination_node: str,
                 field_name: str) -> None:
        """
        Constructor
        :param vertx_id: Vertex ID
        :param source_node: Source Node Canonical URL
        :param destination_node: Destination Node Canonical URL
        :param field_name: Relationship Field Name
        """

        self.vertx_id = vertx_id
        self.source_node = source_node
        self.destination_node = destination_node
        self.field_name = field_name


class CodeTranslationVertex(BaseVertex):
    """
    Vertex for establishing a Code Translation
    """

    def __init__(self, parent_code: CodeNode, translation: CodeNode) -> None:
        """
        Creates a Vertex Relationship to denote Translations to a Code.
        :param parent_code: Parent Code
        :param translation: Translation Code Value
        """

        super().__init__(f"{parent_code.canonical_id}_{translation.canonical_id}",
                         parent_code.canonical_id, translation.canonical_id, 'translation')


class CodeVertex(BaseVertex):
    """
    Vertex for establishing a relationship to a Code Node.
    """

    def __init__(self, node: BaseNode, code: CodeNode, **kwargs) -> None:
        """
        Creates a Relationship to a Code Node on a Code Field.
        :param node: Base Node
        :param code: Code Node
        :keyword field: Field Name override
        """
        super().__init__(f"{node.canonical_id}_{code.canonical_id}",
                         node.canonical_id, code.canonical_id, kwargs.get('field', 'code'))


class IdentifierVertex(BaseVertex):
    """
    Vertex to identify an Identifier Relationship.
    """

    def __init__(self, node: BaseNode, identifier: IdentifierNode, **kwargs) -> None:
        """
        Creates a Vertex for an Identifier Relationship
        :param node: Base Node
        :param identifier: Identifier Node
        :keyword field: Field Name
        """

        super().__init__(f"{node.canonical_id}_{identifier.canonical_id}",
                         node.canonical_id, identifier.canonical_id, kwargs.get('field', 'code'))


class NameVertex(BaseVertex):
    """
    Vertex to link to a Name Node
    """

    def __init__(self, node: BaseNode, name: NameNode) -> None:
        """
        Creates a Name Vertex to Link to a Name
        :param node: Source Node
        :param name: Name Node
        """

        super().__init__(f"{node.canonical_id}_{name.canonical_id}",
                         node.canonical_id, name.canonical_id, 'name')
