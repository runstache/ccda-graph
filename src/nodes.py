"""
Class denoting different Node Types for C-CDA Entities
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass(kw_only=True)
class BaseNode:
    """
    Base Node Class with common field structures.
    """

    doc_id: int
    doc_source_id: str
    canonical_id: str
    etl_dg_code: int
    etl_load_datetime: datetime
    etl_src_inc_datetime: datetime
    etl_src_sys_id: int


@dataclass(kw_only=True)
class IdentifierNode(BaseNode):
    """
    Node for capturing Identifier Data Type Information
    """

    root: str
    extension: str
    assign_authority: str


@dataclass(kw_only=True)
class CodeNode(BaseNode):
    """
    Node for capturing coded information.
    """

    code: str
    code_system: str
    code_system_name: str
    code_system_version: str
    display_name: str


@dataclass(kw_only=True)
class NameNode(BaseNode):
    """
    Node for capturing a Person's Name
    """

    type_code: str
    family_name: str
    given_name: str
    prefix: str
    suffix: str
    valid_start_date: datetime | None
    valid_end_date: datetime | None


@dataclass(kw_only=True)
class AddressNode(BaseNode):
    """
    Node for capturing Address Information.
    """

    use: str
    type: str
    street_address_line: str
    city: str
    state: str
    county: str
    country: str
    postal_code: str


@dataclass(kw_only=True)
class EncounterNode(BaseNode):
    """
    Node for Capturing Encounter information.
    """

    status_code: str
    encounter_start: datetime
    encounter_end: datetime


@dataclass(kw_only=True)
class GeneralEntityNode(BaseNode):
    """
    Denotes a General Entity Node like a Person, or Assigned Entity
    """

    class_code: str


@dataclass(kw_only=True)
class DiagnosisNode(BaseNode):
    """
    Denotes a Basic Diagnosis Node.
    """

    negation_indicator: bool
    status_code: str
    effective_start_datetime: datetime
    effective_end_datetime: datetime


@dataclass(kw_only=True)
class ContactNode(BaseNode):
    """
    Denotes a Node for Capturing Contact Information
    """

    use: str
    value: str
