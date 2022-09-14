# Представление клинического документа 'CDA-ВыписнойЭпикризЗаконченный'
# в читаемом виде
# Разработка ПО - e.fartushnyi@d-health.institute
# --------------------------------------------------------------------
import xml.etree.ElementTree as ET
import os
from lxml import etree
import streamlit as st

import xmltodict
import pprint
import json
import pandas as pd

# from io import StringIO
# from lxml.etree import XML, XSLT, parse

import lxml.etree as ETT


def keys_by_depth(dict_, depth=0, output=None):
    if output is None:
        output = {}
    if not depth in output:
        output[depth] = set()
    for key in dict_:
        output[depth].add(key)
        if isinstance(dict_[key], dict):
            keys_by_depth(dict_[key], depth+1, output)
    return output


def main():

    st.set_page_config(layout = 'wide',)
    doc_type = st.sidebar.selectbox(
        "Выбор документа",
        ("Выписной эпикриз короткий", "Выписной эпикриз полный", "Приложение_Д", "Приложение_Е")
    )

    path = os.path.abspath('data/epi_amb/')  # название папки с файлами
    if(doc_type == 'Выписной эпикриз короткий'):
        file_name = 'CDADocumentRuAmbulatorySummury_min.xml'
    elif(doc_type == 'Приложение_Д'):
        file_name = 'pril_D.xml'
    elif(doc_type == 'Приложение_Е'):
        file_name = 'pril_E.xml'
    else:
        file_name = 'CDADocumentRuAmbulatorySummury_max.xml'

    file_xml = os.path.join(path, file_name)
    # tree = ET.parse(os.path.join(path, file_name))

    # Проверка xsd
    with st.expander("Валидация схем по .xsd"):
        xsd_file_name = 'CDA.xsd'
        try:
            schema_root = etree.parse(os.path.join(path, xsd_file_name))
        except ValueError:
            st.error(ValueError)
        # st.write(schema_root)
        schema = etree.XMLSchema(schema_root)
        # st.write(schema)
        xml = etree.parse(file_xml)
        if not schema.validate(xml):
            try:
                st.error("xml-файл содержит ошибки и не соответсвует xsd-схеме. Протокол ошибок ниже :" )
                st.error(schema.error_log)
            except ValueError:
                st.error(ValueError)
        else:
            st.success("xml-файл не содержит ошибок")

    with st.expander("XSL - ПРЕОБРАЗОВАНИЕ"):
        xsl_file_name = 'AmbSum.xsl'
        try:
            xslt = ETT.parse(os.path.join(path, xsl_file_name))
        except ValueError:
            st.error(ValueError)
        dom = ETT.parse(file_xml)
        # xslt = ET.parse(file_xsl)
        transform = ETT.XSLT(xslt)
        newdom = transform(dom)

        html = ETT.tostring(newdom, pretty_print=True)
        st.components.v1.html(html, width=None, height=960, scrolling=True)

        # st.write(ETT.tostring(newdom, pretty_print=True))


    # col1, col2 = st.columns([1, 3])
    st.sidebar.info("Структура документа по уровням")
    st.success("Содержание. Клинический документ: CD.Эпикриз-выписной.Законченный ")

    fileptr = open(file_xml, encoding="utf8")
    # read xml content from the file
    xml_content = fileptr.read()
    # print("XML content is:")
    # print(xml_content)

    xml_dict = xmltodict.parse(xml_content)
    keys = keys_by_depth(xml_dict)
    # print('Ключи - '+str(keys))
    st.sidebar.write(keys)
    st.write(xml_dict)

if __name__ == '__main__':
    main()

