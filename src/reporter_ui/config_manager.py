import logging
from os.path import join

import lxml.etree as l_etree

from common.constants import RESOURCES, ROOT
from common.models.errors import RGUIError
from common.models.utilities import RGConfig, RGMeasureEntry
from common.text import *
from common.utility_base import RGUtilityBase
from common.utils import get_dir_path


class RGConfigManager(RGUtilityBase):
    XML_OUT_DIR = 'out_dir'
    XML_TEMPLATE_DIR = 'template_dir'
    XML_ORCA_PATH = 'orca_path'
    XML_MEASURES = 'measures'
    XML_MEASURE = 'measure'
    XML_ATTR_ID = 'id'
    XML_ATTR_REF_NO = 'ref_no'
    XML_ATTR_TITLE = 'title'
    XML_CONFIGURATION = 'configuration'
    XML_FISCAL_YEAR_BAND = 'fiscal_year_band'
    XML_DEBUG_MODE = 'debug_mode'

    @staticmethod
    def read_config():
        try:
            with open(join(get_dir_path(ROOT), 'config.xml'), 'r') as ff:
                s_xml = ''.join(ff.readlines())

            tree = RGConfigManager.__get_valid_config_tree(s_xml)
            config = RGConfigManager.__parse_config_from_xml(tree)

        except RGUIError as ex:
            raise ex
        except Exception as ex:
            logging.getLogger(__name__).error('Configuration manager could not read reporter configuration file [{}]'.format(str(ex)))
            raise RGUIError(REPORTER_COULD_NOT_READ_THE_CONFIGURATION_FILE)
        return config

    @staticmethod
    def save_config(config):
        if not isinstance(config, RGConfig):
            raise RGUIError(CONFIGURATION_COULD_NOT_BE_SAVED)
        try:
            tree = RGConfigManager.__parse_config_to_xml(config=config)
            s_config = l_etree.tostring(tree, encoding='UTF-8', pretty_print=True, xml_declaration=True) \
                .decode(encoding='UTF-8')

            # validate config before saving
            RGConfigManager.__get_valid_config_tree(s_config)

            with open(join(get_dir_path(ROOT), 'config.xml'), 'w') as ff:
                ff.write(s_config)

        except Exception as ex:
            logging.getLogger(__name__).error('Configuration manager could not save reporter configuration file [{}]'.format(str(ex)))
            raise RGUIError(CONFIGURATION_COULD_NOT_BE_SAVED)

    @staticmethod
    def __get_valid_config_tree(s_xml):
        try:
            with open(join(get_dir_path(RESOURCES), 'config_schema.xsd'), 'r') as ff:
                s_schema = ''.join(ff.readlines())

            if s_schema is None:
                raise RGUIError('Reporter could not find a valid configuration file')

            schema_root = l_etree.XML(s_schema.encode(encoding='UTF-8'))
            schema = l_etree.XMLSchema(schema_root)
            parser = l_etree.XMLParser(schema=schema)

            tree = l_etree.fromstring(s_xml.encode(encoding='UTF-8'), parser)

        except l_etree.XMLSyntaxError as ex:
            logging.getLogger(__name__).error('Configuration contains invalid tags/data [{}]'.format(str(ex)))
            raise RGUIError(CONFIGURATION_FILE_CONTAINS_INVALID_XML_TAGS_OR_DATA)
        except Exception as ex:
            logging.getLogger(__name__).error('Reporter could not validate configuration file [{}]'.format(str(ex)))
            raise RGUIError(REPORTER_COULD_NOT_VALIDATE_CONFIGURATION_FILE)
        return tree

    @staticmethod
    def __parse_config_from_xml(tree=None):
        config = None
        if tree is not None:
            config = RGConfig()
            for node in tree:
                if node.tag == RGConfigManager.XML_OUT_DIR:
                    config.out_dir = node.text
                elif node.tag == RGConfigManager.XML_TEMPLATE_DIR:
                    config.template_dir = node.text
                elif node.tag == RGConfigManager.XML_ORCA_PATH:
                    config.orca_path = node.text
                elif node.tag == RGConfigManager.XML_FISCAL_YEAR_BAND:
                    config.fy_band = int(node.text)
                elif node.tag == RGConfigManager.XML_DEBUG_MODE:
                    config.debug_mode = bool(node.text.title())
                elif node.tag == RGConfigManager.XML_MEASURES:
                    measures = list()
                    for c_node in node:
                        measures.append(
                            RGMeasureEntry(
                                m_id=c_node.get(RGConfigManager.XML_ATTR_ID),
                                m_ref_no=c_node.get(RGConfigManager.XML_ATTR_REF_NO),
                                m_title=c_node.get(RGConfigManager.XML_ATTR_TITLE)
                            )
                        )
                    config.measure_entries = measures
        del tree, node, c_node
        return config

    @staticmethod
    def __parse_config_to_xml(config):
        tree = None
        if config is not None:
            tree = l_etree.Element(RGConfigManager.XML_CONFIGURATION)

            out_dir = l_etree.Element(RGConfigManager.XML_OUT_DIR)
            out_dir.text = config.out_dir
            tree.append(out_dir)

            template_dir = l_etree.Element(RGConfigManager.XML_TEMPLATE_DIR)
            template_dir.text = config.template_dir
            tree.append(template_dir)

            orca_path = l_etree.Element(RGConfigManager.XML_ORCA_PATH)
            orca_path.text = config.orca_path
            tree.append(orca_path)

            fy_band = l_etree.Element(RGConfigManager.XML_FISCAL_YEAR_BAND)
            fy_band.text = str(config.fy_band)
            tree.append(fy_band)

            debug_mode = l_etree.Element(RGConfigManager.XML_DEBUG_MODE)
            debug_mode.text = str(config.debug_mode).lower()
            tree.append(debug_mode)

            measures = l_etree.Element(RGConfigManager.XML_MEASURES)
            for m_entry in config.measure_entries:
                m_node = l_etree.Element(RGConfigManager.XML_MEASURE)
                m_node.attrib[RGConfigManager.XML_ATTR_ID] = m_entry.m_id
                m_node.attrib[RGConfigManager.XML_ATTR_REF_NO] = m_entry.m_ref_no
                m_node.attrib[RGConfigManager.XML_ATTR_TITLE] = m_entry.m_title
                measures.append(m_node)

            tree.append(measures)
        return tree
