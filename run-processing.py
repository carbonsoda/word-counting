import os
from collections import defaultdict
import pandas as pd
from sorting import filefinder, wordcounting, join_dfs, record_wordsets

rootA = ""
rootZ = ""


def process(root, naming, isprefix):
    all_words = set()
    all_dfs = []
    issues = defaultdict(lambda: [])

    name_idx = 0
    if isprefix:
        name_idx = 1

    for subjectfile in filefinder(root, naming, isprefix):
        wordcount = wordcounting(subjectfile)
        if type(wordcount) is str:
            issues['PermissionError'].append(subjectfile)

        all_words.update(wordcount.keys())

        # creating df and appending to master list of dfs
        filename = os.path.splitext(os.path.split(subjectfile)[1])[0]
        colname = filename.split(naming)[name_idx]
        df = pd.DataFrame.from_dict(dict(wordcount), orient='index', columns=[colname])
        all_dfs.append(df)

    return all_words, all_dfs


# inital process through all desired files
# returns list of dataframes
def inital(initalroot, naming, isprefix, saveprefix, savedirectory):
    wordscount_filename = str(saveprefix) + '_words_count'
    wordsunique_filename = str(saveprefix) + '_words_unique'

    words, all_dfs = process(initalroot, naming, isprefix=isprefix)
    join_dfs(all_dfs, wordscount_filename, savedirectory)
    record_wordsets(words, wordsunique_filename, savedirectory)

    return all_dfs


# Processing through PB (Picture Book) files:
desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop').replace('\\', '/')

# Processing through desired files in rootA
A_dfs = inital(rootA, naming='rawtext_', isprefix=True, saveprefix='abc', savedirectory=desktop)
# Processing through desired files in rootZ
Z_dfs = inital(rootZ, naming='_final', isprefix=False, saveprefix='xyz', savedirectory=desktop)

print('abc + xyz ready!\nStarting master merge...\n')
# this is going to be a nightmare
master_savename = 'master_count_inx+pb'
master_dfs = join_dfs(pb_dfs + inx_dfs, master_savename, desktop, returndfs=True)
