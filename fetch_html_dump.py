import argparse
import pathlib
import re
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Dump wikipedia static html articles.")
parser.add_argument('root', type=pathlib.Path, help="article folder path")
parser.add_argument('output', type=pathlib.Path, help="output folder path")

args = parser.parse_args()
logging.basicConfig(filename='log.txt', level=logging.DEBUG)

blacklist = ('User_', 'Kép~', 'Vita~', 'Kategória~')


def check_blacklist(file: pathlib.Path) -> bool:
    for entry in blacklist:
        if entry in str(file):
            return True
    return False


def read(file: pathlib.Path):
    with open(file, 'r', encoding='UTF-8') as f:
        content = f.read()
    return BeautifulSoup(content, 'html.parser')


def save(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)


def traverse(path: pathlib.Path):
    for child in path.iterdir():
        if child.is_dir():
            yield from traverse(child)
        elif child.is_file() and child.suffix == '.html':
            blacklisted = check_blacklist(child)
            yield child.absolute() if not blacklisted else None


def find_toc_idx(content):
    for idx, entry in enumerate(content):
        entry_string = str(entry).replace('\n', '')
        e = BeautifulSoup(entry_string, 'html.parser')
        toc = e.find('table', {'id': 'toc'})
        if toc:
            return idx


def parse_section_text(section):
    obj = BeautifulSoup(''.join(str(x) for x in section), 'html.parser')
    p_list = obj.find_all('p')
    for p in p_list:
        text = p.text.replace('\n', '')
        text = text.replace(u'\xa0', u'')
        yield text


files = list(traverse(args.root))
files = [file for file in files if file]
for file in tqdm(files):
    html = read(file)
    try:
        content = html.find('div', {
            'id': 'bodyContent'
        }).contents
        toc_idx = find_toc_idx(content)
        if not toc_idx:
            continue

        introduction_section = content[:toc_idx]
        extended_section = content[toc_idx:]

        introduction_list = tuple(parse_section_text(introduction_section))
        extended_list = tuple(parse_section_text(extended_section))

        introduction = ''.join(introduction_list)
        extended = ''.join(extended_list)
        introduction = re.sub(r'\[\d\]', ' ', introduction)
        extended = re.sub(r'\[\d\]', ' ', extended)

        if len(introduction) > 0 and len(extended) > 0:
            fname = str(file).rsplit('\\', 1)[1].rsplit('.')[0]
            save(introduction, f'{args.output}//{fname}_int.txt')
            save(extended, f'{args.output}//{fname}_ext.txt')

    except AttributeError as e:
        logging.info(f'TOC not found in: {file}')
    except Exception as e:
        logging.info(e)

