"""
Tests for the Node Factory
"""

from lxml import etree
from lxml.etree import ElementBase
from assertpy import assert_that
from src.factories import NodeFactory
import pytest
from datetime import datetime

TEST_FILE = './tests/test_files/test-elements.xml'

NAMESPACES = {
    'v3': 'urn:hl7-org:v3',
    'voc': 'urn:hl7-org:v3/voc',
    'sdtc': 'urn:hl7-org:sdtc',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

BASE_PROPERTIES = {
    'doc_id': 1,
    'doc_source_id': 'test',
    'etl_dg_code': 20,
    'etl_load_datetime': datetime(2024, 1, 22, 0, 0, 0),
    'etl_src_inc_datetime': datetime(2024, 1, 22, 0, 0, 0),
    'etl_src_sys_id': 10
}


@pytest.fixture
def xml_file() -> bytes:
    """
    Loads the Bytes from the XML File.
    :return: Bytes
    """

    with open(TEST_FILE, 'rb') as input_file:
        return input_file.read()


def test_identifier_node(xml_file):
    """
    Tests creating an Identifier Node.
    """

    elements_file: ElementBase = etree.fromstring(xml_file)

    id_element = elements_file.find('./v3:id', namespaces=NAMESPACES)
    factory = NodeFactory(NAMESPACES, **BASE_PROPERTIES)

    result = factory.build_identifier_node(id_element)

    assert_that(result).is_not_none()
    assert_that(result).has_canonical_id(
        'urn:oid:2.16.840.1.113883.19.5:2fa15bc7-8866-461a-9000-f739e425860a')
    assert_that(result).has_root('2.16.840.1.113883.19.5')
    assert_that(result).has_extension('2fa15bc7-8866-461a-9000-f739e425860a')
    assert_that(result).has_assign_authority('https://github.com/synthetichealth/synthea')


def test_identifier_node_url(xml_file):
    """
    Tests creating an Identifier Node with a URL Root.
    """

    elements_file: ElementBase = etree.fromstring(xml_file)

    id_element = elements_file.find('./v3:id', namespaces=NAMESPACES)
    factory = NodeFactory(NAMESPACES, **BASE_PROPERTIES)

    result = factory.build_identifier_node(id_element)

    assert_that(result).is_not_none()
    assert_that(result).has_canonical_id(
        'https://github.com/synthetichealth/synthea/999999')
    assert_that(result).has_root('https://github.com/synthetichealth/synthea')
    assert_that(result).has_extension('999999')
    assert_that(result).has_assign_authority('https://github.com/synthetichealth/synthea')


def test_identifier_node_none(xml_file):
    """
    Tests sending an empty item to the Factory.
    """

    elements_file: ElementBase = etree.fromstring(xml_file)

    id_element = elements_file.find('./v3:chicken', namespaces=NAMESPACES)
    factory = NodeFactory(NAMESPACES, **BASE_PROPERTIES)

    result = factory.build_identifier_node(id_element)
    assert_that(result).is_none()

def test_contact_node(xml_file):
    """
    Tests creating a
    :param xml_file:
    :return:
    """