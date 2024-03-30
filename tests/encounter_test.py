"""
Test usage for mapping an encounter.
"""
import urllib.parse
import uuid

from lxml.etree import ElementBase
from lxml import etree
import os

from src.graphs import NodeGraph
from src.nodes import NameNode, DiagnosisNode, BaseNode, IdentifierNode, CodeNode, AddressNode, \
    EncounterNode, GeneralEntityNode, ContactNode
from src.vertices import VertexInfo
import pytest
from datetime import datetime
import json

TEST_FILE = './tests/test_files/test-ccda.xml'

DATEFORMAT = '%Y%m%d'

NAMESPACES = {
    'v3': 'urn:hl7-org:v3',
    'voc': 'urn:hl7-org:v3/voc',
    'sdtc': 'urn:hl7-org:sdtc',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


@pytest.fixture
def xml_file() -> bytes:
    """
    Returns the XML File Bytes.
    :return: Bytes
    """

    with open(TEST_FILE, 'rb') as input_file:
        return input_file.read()


def get_section(ccda: ElementBase, template_id: str) -> ElementBase | None:
    """
    Retrieves the Section for a Given Template ID
    :param ccda: CCDA File
    :param template_id: Template ID Oid
    :return: Section
    """

    components = ccda.findall('./v3:component/v3:structuredBody/v3:component',
                              namespaces=NAMESPACES)

    for component in components:
        templates = component.findall('./v3:section/v3:templateId', namespaces=NAMESPACES)
        if len([x for x in templates if x.get('root') == template_id]) > 0:
            return component.find('./v3:section', namespaces=NAMESPACES)
    return None


def test_graph_encounter(xml_file) -> None:
    """
    Test Graphing an Encounter.
    :param xml_file: XML File Bytes
    :return: None
    """

    ccda_file: ElementBase = etree.fromstring(xml_file)
    ccda_graph = NodeGraph()

    document_id = 1
    source_id = 5

    document_id_element: ElementBase = ccda_file.find('./v3:id', namespaces=NAMESPACES)

    document_id_node = IdentifierNode(
        doc_id=document_id,
        doc_source_id=str(source_id),
        canonical_id=f"{document_id_element.get('root', '')}:{document_id_element.get('extension', '')}",
        etl_dg_code=0, etl_load_datetime=datetime.now(), etl_src_inc_datetime=datetime.now(),
        etl_src_sys_id=source_id, root=document_id_element.get('root', ''),
        extension=document_id_element.get('extension', ''),
        assign_authority=document_id_element.get('assigningAuthorityName', ''))

    ccda_graph.add_node(document_id_node)

    encounter_section = get_section(ccda_file, '2.16.840.1.113883.10.20.22.2.22')

    if encounter_section is None:
        raise SyntaxError('No Encounter Section Found')

    encounter_entries: list[ElementBase] = encounter_section.findall('./v3:entry',
                                                                     namespaces=NAMESPACES)
    for encounter_entry in encounter_entries:
        encounter_element: ElementBase = encounter_entry.find('./v3:encounter',
                                                              namespaces=NAMESPACES)

        encounter_ids: list[ElementBase] = encounter_element.findall('./v3:id',
                                                                     namespaces=NAMESPACES)

        status_code_element: ElementBase = encounter_element.find('./v3:statusCode',
                                                                  namespaces=NAMESPACES)
        type_code_element: ElementBase = encounter_element.find('./v3:code', namespaces=NAMESPACES)

        effective_time_start_element: ElementBase = encounter_element.find(
            './v3:effectiveTime/v3:low', namespaces=NAMESPACES)
        effective_time_end_element: ElementBase = encounter_element.find(
            './v3:effectiveTime/v3:high', namespaces=NAMESPACES)

        encounter_start = ''
        encounter_end = ''
        if effective_time_start_element is not None:
            encounter_start = effective_time_start_element.get('value', '')
        if effective_time_end_element is not None:
            encounter_end = effective_time_end_element.get('value', '')

        encounter_node = EncounterNode(
            doc_id=document_id,
            doc_source_id=str(source_id),
            etl_dg_code=0, etl_load_datetime=datetime.now(),
            etl_src_inc_datetime=datetime.now(),
            etl_src_sys_id=source_id,
            canonical_id=f"http://upmc.com/encounter/{uuid.uuid4()}",
            status_code=status_code_element.get('code', ''),
            encounter_start=datetime.strptime(encounter_start[:8], DATEFORMAT),
            encounter_end=datetime.strptime(encounter_end[:8], DATEFORMAT)
        )

        ccda_graph.add_node(encounter_node)

        type_code_node = CodeNode(
            doc_id=document_id,
            doc_source_id=str(source_id),
            etl_dg_code=0, etl_load_datetime=datetime.now(),
            etl_src_inc_datetime=datetime.now(),
            etl_src_sys_id=source_id,
            canonical_id=f"{type_code_element.get('codeSystem', '')}:{type_code_element.get('code', '')}",
            code_system=type_code_element.get('code_system', ''),
            code=type_code_element.get('code', ''),
            code_system_name=type_code_element.get('codeSystemName', ''),
            code_system_version=type_code_element.get('codeSystemVersion', ''),
            display_name=type_code_element.get('displayName', '')
        )
        ccda_graph.add_node(type_code_node)
        code_translations: list[ElementBase] = type_code_element.findall('./v3:translation',
                                                                         namespaces=NAMESPACES)

        for code_translation in code_translations:
            translation_code_node = CodeNode(doc_id=document_id,
                                             doc_source_id=str(source_id),
                                             etl_dg_code=0, etl_load_datetime=datetime.now(),
                                             etl_src_inc_datetime=datetime.now(),
                                             etl_src_sys_id=source_id,
                                             canonical_id=f"{code_translation.get('codeSystem', '')}:{code_translation.get('code', '')}",
                                             code_system=code_translation.get('code_system', ''),
                                             code=code_translation.get('code', ''),
                                             code_system_name=code_translation.get('codeSystemName',
                                                                                   ''),
                                             code_system_version=code_translation.get(
                                                 'codeSystemVersion', ''),
                                             display_name=code_translation.get('displayName', ''))

            ccda_graph.add_node(translation_code_node)
            ccda_graph.add_vertex(type_code_node, translation_code_node, 'translation')

        ccda_graph.add_vertex(encounter_node, type_code_node, 'code')

        for encounter_id in encounter_ids:
            encounter_id_node = IdentifierNode(
                doc_id=document_id,
                doc_source_id=str(source_id),
                canonical_id=f"{encounter_id.get('root', '')}:{encounter_id.get('extension', '')}",
                etl_dg_code=0, etl_load_datetime=datetime.now(),
                etl_src_inc_datetime=datetime.now(),
                etl_src_sys_id=source_id, root=encounter_id.get('root', ''),
                extension=encounter_id.get('extension', ''),
                assign_authority=encounter_id.get('assigningAuthorityName', '')
            )
            ccda_graph.add_node(encounter_id_node)
            ccda_graph.add_vertex(encounter_node, encounter_id_node, 'id')

        # Performers
        performer_elements: list[ElementBase] = encounter_element.findall('./v3:performer',
                                                                          namespaces=NAMESPACES)
        for performer_element in performer_elements:
            function_code_element: ElementBase = performer_element.find('./v3:functionCode',
                                                                        namespaces=NAMESPACES)
            function_code_node = CodeNode(
                doc_id=document_id,
                doc_source_id=str(source_id),
                etl_dg_code=0, etl_load_datetime=datetime.now(),
                etl_src_inc_datetime=datetime.now(),
                etl_src_sys_id=source_id,
                canonical_id=f"{function_code_element.get('codeSystemName', '')}:{function_code_element.get('code', '')}",
                code=function_code_element.get('code', ''),
                code_system=function_code_element.get('codeSystem', ''),
                code_system_name=function_code_element.get('codeSystemName', ''),
                code_system_version=function_code_element.get('codeSystemVersion', ''),
                display_name=function_code_element.get('displayName', '')
            )
            ccda_graph.add_node(function_code_node)
            function_code_translation_elements: list[ElementBase] = function_code_element.findall(
                './translation', namespaces=NAMESPACES)
            for function_code_translation_element in function_code_translation_elements:
                translation_code_node = CodeNode(
                    doc_id=document_id,
                    doc_source_id=str(source_id),
                    etl_dg_code=0, etl_load_datetime=datetime.now(),
                    etl_src_inc_datetime=datetime.now(),
                    etl_src_sys_id=source_id,
                    canonical_id=f"{function_code_translation_element.get('codeSystemName', '')}:{function_code_translation_element.get('code', '')}",
                    code=function_code_translation_element.get('code', ''),
                    code_system=function_code_translation_element.get('codeSystem', ''),
                    code_system_name=function_code_translation_element.get('codeSystemName', ''),
                    code_system_version=function_code_translation_element.get('codeSystemVersion',
                                                                              ''),
                    display_name=function_code_translation_element.get('displayName', '')
                )
                ccda_graph.add_node(translation_code_node)
                ccda_graph.add_vertex(function_code_node, translation_code_node, 'translation')

            assigned_entity_element: ElementBase = performer_element.find('./v3:assignedEntity',
                                                                          namespaces=NAMESPACES)
            performer_entity_node = GeneralEntityNode(
                doc_id=document_id,
                doc_source_id=str(source_id),
                etl_dg_code=0, etl_load_datetime=datetime.now(),
                etl_src_inc_datetime=datetime.now(),
                etl_src_sys_id=source_id,
                canonical_id=f"urn:uuid:{uuid.uuid4()}",
                class_code='ASSIGNED')

            ccda_graph.add_node(performer_entity_node)
            ccda_graph.add_vertex(encounter_node, performer_entity_node, 'performer')

            performer_id_elements = assigned_entity_element.findall('./v3:id',
                                                                    namespaces=NAMESPACES)
            for performer_id_element in performer_id_elements:
                id_node = IdentifierNode(
                    doc_id=document_id,
                    doc_source_id=str(source_id),
                    etl_dg_code=0, etl_load_datetime=datetime.now(),
                    etl_src_inc_datetime=datetime.now(),
                    etl_src_sys_id=source_id,
                    canonical_id=f"{performer_id_element.get('root', '')}:{performer_id_element.get('extension', '')}",
                    root=performer_id_element.get('root', ''),
                    extension=performer_id_element.get('extension', ''),
                    assign_authority=performer_id_element.get('assigningAuthorityName', '')
                )
                ccda_graph.add_node(id_node)
                ccda_graph.add_vertex(performer_entity_node, id_node, 'id')

            performer_code_element = assigned_entity_element.find('./v3:code',
                                                                  namespaces=NAMESPACES)
            performer_code_node = CodeNode(
                doc_id=document_id,
                doc_source_id=str(source_id),
                etl_dg_code=0, etl_load_datetime=datetime.now(),
                etl_src_inc_datetime=datetime.now(),
                etl_src_sys_id=source_id,
                canonical_id=f"{performer_code_element.get('codeSystemName', '')}:{performer_code_element.get('code', '')}",
                code=performer_code_element.get('code', ''),
                code_system=performer_code_element.get('codeSystem', ''),
                code_system_name=performer_code_element.get('codeSystemName', ''),
                code_system_version=performer_code_element.get('codeSystemVersion', ''),
                display_name=performer_code_element.get('displayName', '')
            )
            ccda_graph.add_node(performer_code_node)
            ccda_graph.add_vertex(performer_entity_node, performer_code_node, 'code')
            performer_code_translation_elements = performer_code_element.findall('./v3:translation',
                                                                                 namespaces=NAMESPACES)
            for performer_code_translation_element in performer_code_translation_elements:
                translation_code_node = CodeNode(
                    doc_id=document_id,
                    doc_source_id=str(source_id),
                    etl_dg_code=0, etl_load_datetime=datetime.now(),
                    etl_src_inc_datetime=datetime.now(),
                    etl_src_sys_id=source_id,
                    canonical_id=f"{performer_code_translation_element.get('codeSystemName', '')}:{performer_code_translation_element.get('code', '')}",
                    code=performer_code_translation_element.get('code', ''),
                    code_system=performer_code_translation_element.get('codeSystem', ''),
                    code_system_name=performer_code_translation_element.get('codeSystemName', ''),
                    code_system_version=performer_code_translation_element.get('codeSystemVersion',
                                                                               ''),
                    display_name=performer_code_translation_element.get('displayName', '')
                )
                ccda_graph.add_node(translation_code_node)
                ccda_graph.add_vertex(performer_code_node, translation_code_node, 'translation')

            performer_address_elements: list[ElementBase] = assigned_entity_element.findall(
                './v3:addr', namespaces=NAMESPACES)
            for performer_address_element in performer_address_elements:
                address_lines = '\n'.join([x.text for x in performer_address_element.findall(
                    './v3:streetAddressLine', namespaces=NAMESPACES)])
                city_element = performer_address_element.find('./v3:city', namespaces=NAMESPACES)
                state_element = performer_address_element.find('./v3:state', namespaces=NAMESPACES)
                zip_code_element = performer_address_element.find('./v3:postalCode',
                                                                  namespaces=NAMESPACES)

                address_node = AddressNode(
                    doc_id=document_id,
                    doc_source_id=str(source_id),
                    etl_dg_code=0, etl_load_datetime=datetime.now(),
                    etl_src_inc_datetime=datetime.now(),
                    etl_src_sys_id=source_id,
                    canonical_id=f"urn:uuid:{uuid.uuid4()}",
                    street_address_line=address_lines,
                    country='US',
                    city=city_element.text if city_element is not None else '',
                    state=state_element.text if state_element is not None else '',
                    postal_code=zip_code_element.text if zip_code_element is not None else '',
                    county='',
                    type=performer_address_element.get('type', ''),
                    use=performer_address_element.get('use', '')
                )
                ccda_graph.add_node(address_node)
                ccda_graph.add_vertex(performer_entity_node, address_node, 'addr')

            performer_phone_elements = assigned_entity_element.findall('./v3:tel',
                                                                       namespaces=NAMESPACES)
            for performer_phone_element in performer_phone_elements:
                contact_node = ContactNode(doc_id=document_id,
                                           doc_source_id=str(source_id),
                                           etl_dg_code=0, etl_load_datetime=datetime.now(),
                                           etl_src_inc_datetime=datetime.now(),
                                           etl_src_sys_id=source_id,
                                           canonical_id=f"http://upmc.com/contact/value/{performer_phone_element.get('value', '')}",
                                           use=performer_phone_element.get('use', ''),
                                           value=performer_phone_element.get('value', ''))
                ccda_graph.add_node(contact_node)
                ccda_graph.add_vertex(performer_entity_node, contact_node, 'telecom')
            person_name_elements: list[ElementBase] = assigned_entity_element.find(
                './v3:assignedPerson/v3:name', namespaces=NAMESPACES)

            performer_person_node = BaseNode(
                doc_id=document_id,
                doc_source_id=str(source_id),
                etl_dg_code=0, etl_load_datetime=datetime.now(),
                etl_src_inc_datetime=datetime.now(),
                etl_src_sys_id=source_id,
                canonical_id=f"urn:uuid:{uuid.uuid4()}"
            )
            ccda_graph.add_node(performer_person_node)
            ccda_graph.add_vertex(performer_entity_node, performer_person_node, 'assignedPerson')

            for person_name_element in person_name_elements:
                given_name_string = ' '.join([x.text for x in
                                              person_name_element.findall('./v3:given',
                                                                          namespaces=NAMESPACES) if
                                              x is not None])
                family_name_element = person_name_element.find('./v3:family', namespaces=NAMESPACES)
                suffix_element = person_name_element.find('./v3:suffix', namespaces=NAMESPACES)

                name_node = NameNode(
                    doc_id=document_id,
                    doc_source_id=str(source_id),
                    etl_dg_code=0, etl_load_datetime=datetime.now(),
                    etl_src_inc_datetime=datetime.now(),
                    etl_src_sys_id=source_id,
                    family_name=family_name_element.text if family_name_element is not None else '',
                    given_name=given_name_string,
                    canonical_id=f"http://upmc.com/performers/names/{urllib.parse.quote_plus(given_name_string)}_{urllib.parse.quote_plus(family_name_element.text)}_{urllib.parse.quote_plus(suffix_element.text)}",
                    suffix=suffix_element.text if suffix_element is not None else '',
                    type_code=person_name_element.get('use', ''),
                    prefix='',
                    valid_start_date=None,
                    valid_end_date=None
                )
                ccda_graph.add_node(name_node)
                ccda_graph.add_vertex(performer_person_node, name_node, 'name')



        # Locations

        # Diagnoses
