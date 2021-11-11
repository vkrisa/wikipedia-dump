import requests
import re
from bs4 import BeautifulSoup


def parse_section_text(section):
    obj = BeautifulSoup(''.join(str(x) for x in section), 'html.parser')
    p_list = obj.find_all('p')
    for p in p_list:
        text = p.text.replace('\n', '')
        text = text.replace(u'\xa0', u'')
        yield text


def save(data, path):
    with open(path, 'w') as f:
        f.write(data)


url = 'https://hu.wikipedia.org/wiki/K%C3%A1v%C3%A9'

data = requests.get(url)

html = BeautifulSoup(data.text, 'html.parser')
content = html.find('div', {
    'class': 'mw-parser-output'
}).contents

for idx, entry in enumerate(content):
    entry_string = str(entry).replace('\n', '')
    e = BeautifulSoup(entry_string, 'html.parser')
    toc = e.find('div', {'class': 'toc'})
    if toc:
        breakp = idx
        break

assert breakp, 'No TOC find in document, unable to determine sections.'

introduction_section = content[:breakp]
extended_section = content[breakp:]

introduction_list = tuple(parse_section_text(introduction_section))
extended_list = tuple(parse_section_text(extended_section))

introduction = ''.join(introduction_list)
extended = ''.join(extended_list)
introduction = re.sub(r'\[\d\]', '', introduction)
extended = re.sub(r'\[\d\]', '', extended)

save(introduction, '../data/wikidata/0_int.txt')
save(extended, '../data/wikidata/0_ext.txt')
