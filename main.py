# Представление клинического документа 'CDA-ВыписнойЭпикризЗаконченный'
# в читаемом виде
# Разработка ПО - e.fartushnyi@d-health.institute
# --------------------------------------------------------------------
import xml.etree.ElementTree as ET
import os

import streamlit as st

import xmltodict
import pprint
import json
import pandas as pd

# from io import StringIO
# from lxml.etree import XML, XSLT, parse

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
        ("Выписной эпикриз короткий", "Выписной эпикриз полный")
    )
    # st.sidebar.write(doc_type)
    # print(doc_type)
    # Глубина
    # with st.sidebar:
    #     add_radio = st.radio(
    #         "Method",
    #         ("Standard (5-15 days)", "Express (2-5 days)")
    #     )
    # st.success("Клинический документ: CD.Эпикриз-выписной.Законченный")
    col1, col2 = st.columns([1,4])
    col1.info("Структура документа по уровням")
    col2.success("Содержание. Клинический документ: CD.Эпикриз-выписной.Законченный ")
    path = os.path.abspath('data/epi_amb/')  # название папки с файлами
    # file_name = st.upload("Выберите файл для загрузки")
    # file = st.file_uploader('Загрузите файл :')
    if(doc_type == 'Выписной эпикриз короткий'):
        file_name = 'SampleCDADocumentRuAmbulatorySummury_min.xml'
    else:
        file_name = 'SampleCDADocumentRuAmbulatorySummury_max.xml'
    file_xml = os.path.join(path, file_name)
    # print(file_xml)
    tree = ET.parse(os.path.join(path, file_name))
    root = tree.getroot()
    # for child in root:
    #     print(child.tag, child.attrib)

    fileptr = open(file_xml, encoding="utf8")
    # read xml content from the file
    xml_content = fileptr.read()
    print("XML content is:")
    print(xml_content)

    xml_dict = xmltodict.parse(xml_content)
    keys = keys_by_depth(xml_dict)
    print('Ключи - '+str(keys))
    col1.write(keys)
    col2.write(xml_dict)






if __name__ == '__main__':
    main()

