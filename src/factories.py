"""
Factories for Creating Items from a C-CDA Document.
"""

from lxml.etree import ElementBase
from nodes import CodeNode, NameNode, IdentifierNode, ContactNode, AddressNode
import logging
from datetime import datetime


class BaseFactory:
    """
    Base Factory Implementation
    """

    namespaces: dict
    logger: logging.Logger

    def __init__(self, namespaces: dict) -> None:
        """
        Constructor.
        :param namespaces: Document Namespaces
        """

        self.namespaces = namespaces
        self.logger = logging.getLogger(__name__)


class NodeFactory(BaseFactory):
    """
    Factory for creating Basic Nodes from C-CDA Elements.
    """

    doc_id: int
    doc_source_id: str
    etl_dg_code: int
    etl_load_datetime: datetime
    etl_src_inc_datetime: datetime
    etl_src_sys_id: int

    def __init__(self, namespaces: dict, **kwargs) -> None:
        """
        Constructor
        :param namespaces:
        :keyword: doc_id: Document Id
        :keyword: doc_source_id: Document Source Id
        :keyword: etl_dg_code: ETL Code
        :keyword: etl_load_datetime: Datetime of ETL Load
        :keyword: etl_src_inc_datetime: Source included Datetime
        :keyword: etl_src_sys_id: Etl Source Id
        """
        super().__init__(namespaces)
        self.doc_id = kwargs.get('doc_id', 0)
        self.doc_source_id = kwargs.get('doc_source_id', '')
        self.etl_dg_code = kwargs.get('etl_dg_code', 0)
        self.etl_load_datetime = kwargs.get('etl_load_datetime', datetime.now())
        self.etl_src_inc_datetime = kwargs.get('etl_src_inc_datetime', datetime.now())
        self.etl_src_sys_id = kwargs.get('etl_src_sys_id', 0)

    def build_code_node(self, code_element: ElementBase) -> CodeNode | None:
        """
        Creates a Code node from a Coded Element or Value.
        :param code_element: Code Element of Value
        :return: Code Node
        """

        return None

    def build_translation_code_node(self, translation_element: ElementBase) -> CodeNode | None:
        """
        Creates a Code Node representing a Translation Element.
        :param translation_element: Translation
        :return: Code Node
        """
        return None

    def build_contact_node(self, telecom_element: ElementBase) -> ContactNode | None:
        """
        Creates a Contact Node representing a Telecom Element.
        :param telecom_element: Telecom Element
        :return: Optional Contact Node
        """
        return None

    def build_name_node(self, name_element: ElementBase) -> NameNode | None:
        """
        Creates a Name Node representing a Name Element.
        :param name_element: Name Element
        :return: Optional Name Node
        """
        return None

    def build_address_node(self, addr_element: ElementBase) -> AddressNode | None:
        """
        Creates an Address Node an Addr Element.
        :param addr_element: Addr Element
        :return: Optional Address Node
        """
        return None

    def build_identifier_node(self, id_element: ElementBase) -> IdentifierNode | None:
        """
        Creates an Identifier Node from an id element.
        :param id_element: id element
        :return: Optional Identifier Node
        """
        return None


class ValueFactory(BaseFactory):
    """
    Extracts Basic Values from complex elements to easier to use objects.
    """

    def build_effective_time(self, element: ElementBase) -> dict | None:
        """
        Creates an object representing the Effective Date Time.
        :param element: Effective Date Time
        :return: Optional Dictionary
        """

        return None
