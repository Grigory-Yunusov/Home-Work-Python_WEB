import sys
import shutil
from pathlib import Path
from normalize_for_sort import normalize
from rich.console import Console
from rich.table import Table

DICT_FOR_EXT = {'archives': ['ZIP', 'GZ', 'TAR'],
                  'video': ['AVI', 'MP4', 'MOV', 'MKV'],
                  'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
                  'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
                  'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
                  'other': []}

PATH = 0
all_files = []
suff_used_known = set ()
suff_used_unknown = set()

def filetype (suffix): 
    suffix = suffix.removeprefix ('.')
    for type, suffixes in DICT_FOR_EXT.items():
        for suff in suffixes:
            if suffix.lower() == suff.lower():
                 suff_used_known.add(suffix.upper())
                 return type
    suff_used_unknown.add(suffix.upper())
    return "other"

def work_with_directories (path_: Path, action):
    if action == 'new':
        for dir in path_.iterdir():
            if dir.is_dir():
                dir.replace (PATH / normalize (dir.name))
        for dir_ in DICT_FOR_EXT.keys():
            path_new_dir = path_ / dir_
            path_new_dir.mkdir (exist_ok = True, parents = True)
    if action == 'del':
        for dir in path_.iterdir():
            if dir.is_dir() and (dir.name not in DICT_FOR_EXT.keys()):
                try: 
                    dir.rmdir ()
                except OSError:
                    work_with_directories (dir, action = 'del')
                    print ('Велика вкладеність папок. Запусти програму ще раз')

def sorting (path_, action = False):
    for file in path_.iterdir():
        if file.is_dir():
            if action:
                sorting (file, action = True)
            else: sorting (file)
        else:
            all_files.append (filetype (file.suffix))
            if action: 
                file_name_norm = f'{normalize (file.stem)}{file.suffix}'
                file.replace (PATH / filetype (file.suffix) / file_name_norm)
                if filetype (file.suffix) == 'archives':
                    shutil.unpack_archive (PATH / 'archives' / file_name_norm, 
                                           PATH / 'archives' / file.stem)
    return all_files

def run (line):
    global PATH
    PATH = Path(line)
    sorting (PATH)
    console = Console()
    table = Table (show_header=True)
    print ('')
    print (f'Вміст папки: {PATH}')
    table.add_column ('Типи файлів')
    table.add_column ('Кількість')
    table.add_row ('Зображення', str (all_files.count('images')))
    table.add_row ('Відео', str (all_files.count('video')))
    table.add_row ('Документи', str (all_files.count('documents')))
    table.add_row ('Музика', str (all_files.count('audio')))
    table.add_row ('Архіви', str (all_files.count('archives')))
    table.add_row ('Інші типи', str (all_files.count('other')))
    table.add_row ('Разом', str (len (all_files)))
    console.print (table)
    print ('')
    print (f'Знайдено наступні відомі типи файлів: {suff_used_known}')
    print (f'Знайдено наступні невідомі типи файлів ("Інші типи"): {suff_used_unknown}')
    print ('')
    yn = input ('Продовжити виконання завдання: транслітерація імен файлів \
та їх переміщення у папки за типами (y - yes / n - no): ')
    print ('')
    while True:
        if yn not in 'yn':
            yn = input("Будь ласка, введіть 'y' або 'n': ") 
        else: break
    if yn == 'n':
        print ('Дякую за увагу!\n')
    else:
        work_with_directories (PATH, 'new')
        sorting (PATH, action = True)
        work_with_directories (PATH, 'del')
        print ('Імена файлів нормалізовані. Файли перемещені у\
 відповідні папки.\n')
        
if __name__ == '__main__':
    run()