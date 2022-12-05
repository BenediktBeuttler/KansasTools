# metainfos are read and a category is assigned to every entry according to a file (topic_classification-8)

import pandas as pd
import codecs


file = "CategorySelector/topic_classification-8_utf8.csv"
catMappingFile = "CategorySelector/cat_mapping.csv"
sourcesToSkip = ["bpb", "CurVe II", "Stiftung Lesen", "AOK", "GIZ", "evideo", "knotenpunkte", "alphagrund", "dgb mento"]

filenameConst = 'File_Name'
percConst = 'Perc_Contribution'
substr = "/Users/zweiss/Documents/Forschung/Projekte/kansas/texts/"


def addToFile(line):
    # append entry to meta collection    
    with codecs.open(catMappingFile, 'a', "utf-8") as f:
            f.write(f'\n{line}')
            f.close()

df = pd.read_csv(file, encoding='utf8', on_bad_lines='skip', usecols = [i for i in range(5)], sep='\t', dtype={"index": int, "Dominant_Topic": int, "Perc_Contribution": float, "File_Name": "string"})
df = df.reset_index()
processedFiles = []
# print(pd.options.display.max_rows) 

for index, row in df.iterrows():
    filename = row[filenameConst]
    skip = False    
    if filename not in processedFiles:        
        # skip if source is manually categorized
        for source in sourcesToSkip:
            if source.lower() in str(filename).replace(substr, "").lower():
                skip = True
                break
        if skip:
            continue
        currFn = df[filenameConst]== filename
        currDf = df[currFn]
        maxVal = currDf[percConst].max()
        if maxVal < 0.1:
            print(filename + " has a low matching value with: " + str(maxVal))
        maxEntry = currDf[currDf[percConst] == maxVal]
        line = str(filename).replace(substr, "") + "\t" + str(maxEntry['Dominant_Topic'].iloc[0]) + "\t" + str(maxEntry['Perc_Contribution'].iloc[0])      
        processedFiles.append(filename)
        addToFile(line)






# with open(file, encoding="utf8") as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')
#     line_count = 0
#     for row in csv_reader:
#         if line_count == 0:
#             rowStr = ", ".join(row)
#             # print(rowStr)
#             strArray = rowStr.split(",")
#             for str in strArray:
#                 print(str)
#             line_count += 1
#         else:
#             # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
#             # print(line_count)
#             exit
#             line_count += 1
#     print(f'Processed {line_count} lines.')