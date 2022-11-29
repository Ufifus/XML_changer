from bs4 import BeautifulSoup as bs
import os
import lxml
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO


def viewer(file):

    output = BytesIO(file)

    xsl_file_name = 'DischSum.xsl'
    try:
        xslt = lxml.etree.parse(os.path.join('data/epi_stac/', xsl_file_name))
    except ValueError:
        st.error(ValueError)
    dom = lxml.etree.parse(output)
    transform = lxml.etree.XSLT(xslt)
    newdom = transform(dom)
    html = lxml.etree.tostring(newdom, pretty_print=True)
    st.components.v1.html(html, width=None, height=960, scrolling=True)

    output.close()

class Redactor:
    def __init__(self, _file):
        """"""
        self.name = _file.name
        self.file = _file
        self.content = None
        self.titles = None
        self.subtitles = None
        self.store_dir = os.path.abspath('store/saved_files')
        self.saved_dir = os.path.abspath('store/epicrises')
        if not os.path.exists(self.saved_dir):
            os.mkdir(self.saved_dir)
        if not os.path.exists(self.store_dir):
            os.mkdir(self.store_dir)

        self.items = None

    def loader(self):
        """Check format file (only xml files)
        open file and parce this as bs object"""

        if self.name.split('.')[-1] != 'xml':
            self.get_state(False, 'Not "XML" format file!')

        save_file = os.path.join(self.store_dir, self.name)
        if os.path.exists(save_file):
            content = open(save_file, encoding='utf-8').read()
        else:
            bytes_data = self.file.getvalue()
            string = StringIO(bytes_data.decode('utf-8'))

            content = string.readlines()
            content = ''.join(content)

        bs_content = bs(content, 'xml')
        self.content = bs_content

    def get_titles(self):
        """Parse content and search titles"""
        title_contents = self.content.find_all('title')
        labels = [str(title.contents[0]) for title in title_contents]
        self.titles = {k: v for k, v in zip(labels, title_contents)}
        return labels

    def select_title(self, label):
        """Parse each content of title and select current table or text for user"""
        title = self.titles[label]
        # st.write(title.parent.contents)
        # try:
        #     # st.write(''.join([str(line) for line in title.parent.find('text').contents]))
        #     st.write(title.parent.find('text').string)
        #     st.write('string')
        # except:
        #     st.write(title.parent.find('text'))
        # return False, title, False
        # st.write(title.parent.contents)
        content = title.parent.find('text').find_all('table')
        if len(content) == 0:
            print('None tables only text')
            content = self.parse_text(title.parent.find('text'))
            return False, content
        return True, content

    def get_subtitles(self, title_content):
        """Choice one of exist tables and get these content,
        print table on page as pandas dataframe
        пока под вопросом может и обьединиииим в общую ф-ю!!!!
        """
        label = [i + 1 for i in range(len(title_content))]
        self.subtitles = {k: v for k, v in zip(label, title_content)}
        return label

    def select_subtitle(self, label):
        """select current subtitle which contains needed table"""
        subtitle = self.subtitles[label]
        return subtitle

    def get_items(self, subtitle):
        items = subtitle.find_all('item')
        if len(items) == 0:
            return False
        labels = [label.text for label in items]
        self.items = {k: v for k, v in zip(labels, items)}
        return labels

    def parse_text(self, subtitle):
        # lists = subtitle.find_all('list')
        # paragraphs = subtitle.find_all('paragraph')
        # if len(lists) == 0 and len(paragraphs) == 0:
        #     have_lp = False
        #     return subtitle, have_lp
        # else:
        #     labeltotext = {k: v for k, v in
        #                    zip([t.find('caption').contents[0].replace('\n', '') for t in lists], lists)}
        #     for p in paragraphs:
        #         labeltotext[p.find('caption').contents[0].replace('\n', '')] = p
        #     print('------')
        #     print([[label, val] for label, val in labeltotext.items()])
        #     have_lp = True
        #     return labeltotext, have_lp
        return subtitle

    def parce_table(self, subtitle):
        """parce table and turn on in pandas dataframe"""
        datatable = []
        max_width = 0

        for row in subtitle.find_all('tr'):
            datatable_row = []
            num_cells = row.find_all('td')
            if len(num_cells) == 0:
                num_cells = row.find_all('th')
            for cell in num_cells:
                cell = cell.text.replace('\n', '')
                datatable_row.append(cell)
            if len(datatable_row) > max_width:
                max_width = len(datatable_row)
            datatable.append(datatable_row)

        max_height = len(datatable)
        df = pd.DataFrame(datatable)

        st.dataframe(df)
        return max_height - 1, max_width - 1

    def change_cell(self, current_table, i, max_height, max_width):
        """Change exist cell in current table"""

        changes = [st.session_state[f'{i}'] for i in range(max_width+1)]
        empty_changes = True
        for change in changes:
            if change != '':
                empty_changes = False
        if empty_changes:
            return None
        if len(current_table.find('tbody').find_all('tr')[0].find_all('td')) != 0:
            tag = 'td'
        else:
            tag = 'th'
        if i <= max_height:
            row = current_table.find('tbody').find_all('tr')[i]
            row.clear()
        else:
            row = self.content.new_tag('tr')
            current_table.find('tbody').append(row)
        for cell in changes:
            new_cell = self.content.new_tag(tag)
            new_cell.string = cell
            row.append(new_cell)

    def change_table(self, current_table, change):
        split_simbol = ':'
        if len(current_table.find('tbody').find_all('tr')[0].find_all('td')) != 0:
            tag = 'td'
        else:
            tag = 'th'
        print(change.split('\n')[0].split(' '))
        pos_cells = [int(c) for c in change.split('\n')[0].split(' ') if c != '']
        max_pos = max(pos_cells)
        for elem in range(max_pos+1):
            if elem not in pos_cells:
                # st.write(elem)
                pass
        rows = []
        for row in change.split('\n')[1:]:
            new_row = ['-' for i in range(max_pos+1)]
            for current_pos, exist_pos in enumerate(pos_cells):
                new_row[exist_pos] = row.split(split_simbol)[current_pos]
            rows.append(new_row)
        # st.write(rows)
        current_table.find('tbody').clear()
        for row in rows:
            new_row = self.content.new_tag('tr')
            for cell in row:
                new_cell = self.content.new_tag(tag)
                new_cell.string = cell
                new_row.append(new_cell)
            current_table.find('tbody').append(new_row)
        # st.write(change)

    def change_text(self, subtitle, change):
        new_text = self.content.new_tag('text')
        new_text.string = change
        if change != '':
            subtitle.parent.find('text').replace_with(new_text)
            # subtitle.parent.string = change

    def reload_changes(self):
        """save cahnges in new file"""

        name = os.path.join(self.store_dir, self.name)
        with open(name, 'w', encoding='utf-8') as xml_file:
            xml_file.write(str(self.content.prettify()))


    def save_changes(self, new_name):
        """save file like new xml epicrise"""
        new_name = f'{new_name}.xml'
        name = os.path.join(self.store_dir, self.name)
        new_name = os.path.join(self.saved_dir, new_name)
        os.rename(name, new_name)
        return new_name

    def download_changes(self, new_path, new_name):
        new_file = open(new_path, encoding='utf-8').read()
        st.download_button(
            label='Download file',
            data=new_file,
            file_name=f'{new_name}.xml',
        )

    def get_state(self, state: bool, text):
        """request state(bool, True = success, False = error)
        text(string if False, other if True)"""
        if not state:
            st.error(text)

    def get_content(self):
        return self.content.prettify()

