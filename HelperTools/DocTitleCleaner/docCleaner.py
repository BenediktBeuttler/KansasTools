import os
from fnmatch import fnmatch
import codecs

#### if there are duplicated files, delete the one with no "-clean" in it

# set base folder path
baseFolderPath = "D:\\Repos\\kansas\\data\\new_corpus\\texts"
pattern = "*-clean.txt"
logs = "DocTitleCleaner/logs.txt"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()


# get all _clean filenames in all subfolder
for path, subdirs, files in os.walk(baseFolderPath):
    for name in files:
        if fnmatch(name, pattern):
            # print(os.path.join(path, name))
            sanitizedName = name.replace("-clean","")
            filePath = os.path.join(path, sanitizedName)
            # remove _clean from it and search for those files and remove them
            if os.path.exists(filePath):
                os.remove(filePath)
                logIt(sanitizedName + ": The file has been deleted successfully")
                # print(sanitizedName)
            else:
                logIt(filePath + ": The file does not exist. Keep 'clean' version!")