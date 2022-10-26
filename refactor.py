import streamlit as st
import lxml
from lxml import etree
import os
from bs4 import BeautifulSoup as bs
import pandas as pd


def init_state(upload_file):
    if 'store' not in st.session_state:
        store = os.path.abspath('store')
        if not os.path.exists(store):
            os.mkdir(store)
        st.session_state.store = store
    if 'parse_xml' not in st.session_state:
        st.session_state.parse_xml = upload_file
        st.session_state.parse_xml_update = 0
        st.session_state.parse_xml_string = None

    print(st.session_state)


def update_state(update_parse):
    xml_name = st.session_state.parse_xml.split('/')[-1]
    print(xml_name)
    xml_name, xml_type = xml_name.split('.')
    print(xml_name, xml_type)
    if os.path.exists(st.session_state.parse_xml):
        st.session_state.parse_xml_update += 1
        if st.session_state.parse_xml_update == 0:
            new_xml = os.path.join(st.session_state.store, f'{xml_name}_1')
        else:
            xml_name = st.session_state.parse_xml.replace(f'_{st.session_state.parse_xml_update-1}', f'_{st.session_state.parse_xml_update}')
            new_xml = os.path.join(st.session_state.store, f'{xml_name}')
        st.session_state.parse_xml = new_xml
        print(st.session_state.parse_xml)
        with open(st.session_state.parse_xml, 'w') as xml_file:
            xml_file.write(str(update_parse))

    print(st.session_state)

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    st.header('Trying test refactor xml file')

    upload_file = st.file_uploader('Загрузите произвольный xml')

    if upload_file:
        """Upload xml file and parse him with bs4 and lxml"""
    else:
        """If None file was upload use one of saved files"""
        file_name = 'CDADocumentRuDischargeSummury_max.xml'
        store_dir = os.path.abspath('data/epi_stac/')
        upload_file = os.path.join(store_dir, file_name)

    init_state(upload_file)
    print(upload_file, os.path.exists(upload_file))
    view, structure = st.columns(2)

    with view:

        xsl_file_name = 'DischSum.xsl'

        try:
            xslt = lxml.etree.parse(os.path.join(store_dir, xsl_file_name))
        except ValueError:
            st.error(ValueError)
        dom = lxml.etree.parse(st.session_state.parse_xml)
        transform = lxml.etree.XSLT(xslt)
        newdom = transform(dom)
        html = lxml.etree.tostring(newdom, pretty_print=True)
        st.components.v1.html(html, width=None, height=960, scrolling=True)


    with structure:
        st.header('How this arranged')

        with open(st.session_state.parse_xml, "r") as file:
            content = file.readlines()
            content = "".join(content)
            bs_content = bs(content, "xml")

        file.close()

        contents = bs_content.find_all('title')
        labels = [str(content.contents[0]) for content in contents]
        labeltocontent = {k: v for k, v in zip(labels, contents)}
        param = st.selectbox('Choise label', labels)

        all_data = labeltocontent[param]
        data = all_data.parent.find('text').find('table')


        st.write(data.contents)
        datatable = []

        for row in data.find_all('tr'):
            datatable_row = []
            for cell in row.find_all('td'):
                cell = cell.text.replace('\n', '')
                datatable_row.append(cell)
            datatable.append(datatable_row)

        st.write(data.prettify())

        df = pd.DataFrame(datatable)
        st.dataframe(df)

        with st.form(key='update_xml_file'):
            i = st.number_input('X', min_value=0, max_value=2, value=0, step=1)
            j = st.number_input('Y', min_value=0, max_value=2, value=0, step=1)
            change = st.text_input('Input num row num col and val')
            if change != '':
                st.write('table[{0},{1}] changed on {2}'.format(i, j, change))
                cell = data.find('tr').find('td')
                st.write(cell.__dict__)
                cell.string = change
            submit = st.form_submit_button(label='Update', on_click=update_state(bs_content.prettify()))
