import streamlit as st
from bs4 import BeautifulSoup as bs

from tools import Redactor, viewer


st.set_page_config(layout='wide')


if __name__ == '__main__':
    st.title('XML redactor')
    st.write('')

    xml_file = st.file_uploader('Choise file', accept_multiple_files=False)

    if xml_file:
        redactor = Redactor(xml_file)
        redactor.loader()

        view, change = st.columns(2)

        with view:
            st.header('Viewer')
            viewer(redactor.get_content().encode('utf-8'))

        with change:
            st.header('Redactor')
            title = st.selectbox('Choice title', redactor.get_titles())


            # tables, subtitle_content, lists = redactor.select_title(title)
            tables, title_content= redactor.select_title(title)
            subtitle = st.selectbox('Choice subtitle', redactor.get_subtitles(title_content))
            if tables:
                subtitle_content = redactor.select_subtitle(subtitle)
                save_table = st.checkbox('Save table', value=True)
                st.write(subtitle_content.parent.parent.contents)
                if not save_table:
                    tables = False
                    subtitle_content = subtitle_content.parent
            else:
                subtitle_content = title_content

            if tables:
                max_height, max_width = redactor.parce_table(subtitle_content)
                with st.form(key='update table xml'):
                    i = st.number_input('X', min_value=0, max_value=max_height + 1, value=0, step=1)
                    j = st.number_input('Y', min_value=0, max_value=max_width + 1, value=0, step=1)
                    change = st.text_input('Input text in cell table')
                    st.form_submit_button(label='update', on_click=redactor.change_cell(subtitle_content, i, j,
                                                                                        max_height, max_width, change))
            # elif lists:
            #     items = redactor.get_items(subtitle_content)
            #     if not items:
            #         """Пока оставим т.к не знаю как делать может через регулярные выражения"""
            #     else:
            #         item = st.selectbox('Choice line', items+['append'])
            #         with st.form(key='update list xml'):
            #             change = st.text_input('Input text in item')
            #             if change == '':
            #                 st.form_submit_button(label='update')
            #             else:
            #                 st.form_submit_button(label='update', on_click=redactor.change_list(subtitle_content, item, change))
            else:
                with st.form(key='Update text'):
                    change = st.text_area('Update text', '')
                    if change == '':
                        st.form_submit_button(label='update')
                    else:
                        st.form_submit_button(label='Update', on_click=redactor.change_text(subtitle_content, change))


        redactor.reload_changes()

        new_name = st.text_input('name file without ".xml"')
        if st.button('save file'):
            redactor.save_changes(new_name)
            st.write('Done!')