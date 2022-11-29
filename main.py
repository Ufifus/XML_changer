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
            tables, title_content = redactor.select_title(title)
            subtitle = st.selectbox('Choice subtitle', redactor.get_subtitles(title_content))
            if tables:
                subtitle_content = redactor.select_subtitle(subtitle)
                save_table = st.checkbox('Save table', value=True)

                if not save_table:
                    tables = False
                    subtitle_content = subtitle_content.parent
            else:
                subtitle_content = title_content

            if tables:
                # full_table = st.checkbox('Refactor full table', value=False)
                placeholder = st.empty()
                full_table = None

                with placeholder.form(key='update table xml', clear_on_submit=True):
                    if full_table:
                        change = st.text_area('Update text', '', height=300)
                        if change == '':
                            st.form_submit_button(label='update')
                        else:
                            st.form_submit_button(label='Update', on_click=redactor.change_table(subtitle_content, change))
                    else:
                        max_height, max_width = redactor.parce_table(subtitle_content)
                        i = st.number_input('X', min_value=0, max_value=max_height + 1, value=0, step=1)
                        for j in range(max_width+1):
                            st.text_input(label=f'cell {j}', value='', key=f'{j}')
                        st.form_submit_button(label='update', on_click=redactor.change_cell(subtitle_content, i,
                                                                                                max_height, max_width))



            else:
                with st.form(key='Update text', clear_on_submit=True):
                    change = st.text_area('Update text', '', height=300)
                    if change == '':
                        st.form_submit_button(label='update')
                    else:
                        st.form_submit_button(label='Update', on_click=redactor.change_text(subtitle_content, change))


        # for i in range(max_width+1):
        #     st.session_state[f'{i}'] = ''

        redactor.reload_changes()

        new_name = st.text_input('name file without ".xml"')
        if st.button('save file'):
            new_path = redactor.save_changes(new_name)
            redactor.download_changes(new_path, new_name)
            st.write('Done!')