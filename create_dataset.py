import argparse
import pathlib
import logging
import pandas as pd

parser = argparse.ArgumentParser(description="Dump wikipedia static html articles.")
parser.add_argument('root', type=pathlib.Path, help="article folder path")
logging.basicConfig(filename='log.txt', level=logging.DEBUG)
args = parser.parse_args()


def get_files(folder: pathlib.Path) -> dict:
    files = dict()
    for file in folder.iterdir():
        filename = str(file).rsplit('_', 1)[0]
        files.setdefault(filename, list()).append(file)

    return files


def read(file: pathlib.Path) -> str:
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()


def traverse(txts: dict) -> dict:
    ext, int = '', ''
    for entry in txts:
        if str(entry).endswith('_ext.txt'):
            ext = read(entry)
        elif str(entry).endswith('_int.txt'):
            int = read(entry)

        if len(ext) > 0 and len(int) > 0:
            return {'ext': ext, 'int': int}
        else:
            logging.info(f'{entry}: int or ext not found, skipping...')


files = get_files(args.root)
data = [traverse(file) for key, file in files.items()]
df = pd.DataFrame(data)
df.to_csv('dataset.csv', encoding='utf-8')