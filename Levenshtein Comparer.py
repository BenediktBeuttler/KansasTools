from Levenshtein import distance as lev

bpb_file_old = 'bpb_titles_old.txt'
bpb_file_new = 'bpb_titles_new.txt'

ndr_file_old = 'ndr/ndr_titles_old.txt'
ndr_file_new = 'ndr/ndr_titles_new.txt'

oldTxts = []
newTxts = []

with open(ndr_file_old) as my_file:
    for line in my_file:
        oldTxts.append(line)

with open(ndr_file_new) as my_file:
    for line in my_file:
        newTxts.append(line)

for oldT in oldTxts:
    for newText in newTxts:
        if lev(oldT, newText) < 4:
            print(oldT + " and " + newText + " seem to match.")
