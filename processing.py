import csv
import os
import chardet
import re
from collections import defaultdict
import pandas as pd

# i'll figure out how to make this nicer eventually
unwanted_char = [r'\b-', r'-\b', r'\[\b', r'\(\b', r'\b\]', r'\b\)']


# Searches for desired files in all directorys
def filefinder(root, naming, isprefix=False, ext='.csv'):
    foundfiles = []
    fileslist = []

    for path, _, files in os.walk(root):
        for file in files:
            if file.endswith(ext):
                if isprefix:
                    if file.startswith(naming):
                        foundfiles.append(os.path.join(path, file).replace('\\', '/'))
                        fileslist.append(os.path.splitext(file)[0])
                else:
                    if file.endswith(naming+ext):
                        foundfiles.append(os.path.join(path, file).replace('\\', '/'))
                        fileslist.append(os.path.splitext(file)[0])

    # Document which were already done
    mastertxt = os.path.join(root, "list_foundfiles.txt").replace('\\', '/')
    with open(mastertxt, 'w+') as f:
        for file in fileslist:
            f.write(str(file + '\n'))

    return foundfiles


# prevent overwriting
def checkexisting(root, filename, ext='.csv'):
    base = os.path.join(root, filename).replace('\\', '/')
    file = base + ext
    i = 1
    while True:
        if os.path.exists(file):
            file = base + '_' + str(i) + ext
            i += 1
        else:
            return file


# handles opening each transcript/words file and processes the unique wordcounts
# returns dict(wordcount)
def wordcounting(processfile):
    wordcount = defaultdict(lambda: 0)
    encode = 'utf-8-sig'

    while True:
        try:
            with open(processfile, "r", encoding=encode) as f:
                reader = csv.reader(f)

                for row in reader:
                    if not row:
                        continue
                    words = []
                    # find first cell in row w/o numbers
                    for i in range(len(row)):
                        if not row[i].isdigit():
                            words = row[i].split(" ")
                            break
                    # now filter
                    for word in words:
                        clean_word = fix_punctuation(word)
                        wordcount[clean_word] += 1
            break
        except UnicodeDecodeError:
            # 'utf-8-sig' is to prevent weird symbols showing up
            # but sometimes it causes unicodedecodeerror and requires 'utf-8'
            # this is a catch-all route
            encode = fix_encoding(processfile)

    return wordcount


def fix_punctuation(word):
    newword = word.lower()
    for unwanted in unwanted_char:
        newword = re.sub(unwanted, '', newword)
    return newword


# Solves UnicodeDecodeError
# credit to Ritz on StackOverflow (https://stackoverflow.com/a/54134734)
def fix_encoding(file):
    rawdata = open(file, 'r').read().encode()
    result = chardet.detect(rawdata)
    return result['encoding']


# merges list of dataframes, where col[0] is all the unique words
def join_dfs(dfs_list, dfs_savename, save_root, returndfs=False):
    # processing dataframes
    df_master = dfs_list[0].join(dfs_list[1:], how='outer', sort=True)
    df_master.fillna(0, inplace=True)

    df_file = checkexisting(save_root, dfs_savename)
    df_master.to_csv(df_file, encoding='utf-8-sig')
    # return os.path.exists(df_file)
    if returndfs:
        return df_master


def record_wordsets(words_set, words_filename, save_root):
    wordsfile = checkexisting(save_root, words_filename)
    wordslist = list(words_set)

    with open(wordsfile, "w+", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        for w in wordslist:
            writer.writerow([w])
