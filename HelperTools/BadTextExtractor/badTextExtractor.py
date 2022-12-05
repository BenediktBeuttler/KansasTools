import os
from fnmatch import fnmatch
import codecs

# set base folder path
baseFolderPath = "D:\\Repos\\kansas\\data\\new_corpus\\texts\\hurraki"
pattern1 = "*verschiedene Bedeutung*"
pattern2 = "*verschiedenen Bedeutung*"
logs = "BadTextExtractor/logs.txt"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()

# if fnmatch(name, pattern):
            
# get all _clean filenames in all subfolder
for path, subdirs, files in os.walk(baseFolderPath):
    for name in files:                
        filePath = os.path.join(path, name)
        if os.path.isfile(filePath):
            #open text file in read mode
            text_file = open(filePath, "r", encoding="utf-8")        
            #read whole file to a string
            data = text_file.read()        
            #close file
            text_file.close()

        if fnmatch(data, pattern1):
            logIt(filePath)
            logIt(data)
            logIt("-----")
        if fnmatch(data, pattern2):
            logIt(filePath)
            logIt(data)
            logIt("-----")