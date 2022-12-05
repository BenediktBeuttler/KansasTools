# meta einlesen und jede line als str in liste abspeichern
# eintrag finden und löschen
# file finden und löschen

import os
import codecs


# "D:\\Repos\\kansas\\data\\new_corpus\\texts\\hurraki"
# baseFolderPath = "D:\\Repos\\KansasTools\\FileAndMetaDeleter\\"
baseFolderPath = "D:\\Repos\\kansas\\data\\new_corpus\\texts\\"
# metaFile = "D:\\Repos\\KansasTools\\FileAndMetaDeleter\\alpha-corpus-meta_bsp.tsv"
metaFile = "D:\\Repos\\kansas\\data\\new_corpus\\alpha-corpus-meta.tsv"
deleteFiles = "D:\\Repos\\KansasTools\\FileAndMetaDeleter\\filesToDelete.txt"
logs = "FileAndMetaDeleter/logs.txt"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()

linesMeta = []
indexToDelete = []
# read file and save lines in list
with open(metaFile, 'r', encoding='UTF-8') as file1:
    for line in file1:
        # logIt(line.split('\t')[0])
        linesMeta.append(line.split('\t')[0])

# read file and save lines in list
with open(deleteFiles, 'r', encoding='UTF-8') as file2:
    linesDelete = [line.rstrip() for line in file2]
        
for lineDelete in linesDelete:
    logIt(lineDelete)
    if lineDelete in linesMeta:
        i = linesMeta.index(lineDelete)
        logIt(str(i))
        indexToDelete.append(i)

indexToDelete.sort(reverse=True)

with open(metaFile, "r+") as f:
    lines = f.readlines()
    for i in indexToDelete:
        del lines[i]  # use linenum - 1 if linenum starts from 1
    f.seek(0)
    f.truncate()
    f.writelines(lines)

for i in indexToDelete:
    os.remove(baseFolderPath + linesMeta[i])
    # print(i)