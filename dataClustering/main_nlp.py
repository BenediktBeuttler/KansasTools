from HelperFunctions import *
import stanza

import sys

import pickle
import gensim.corpora as corpora

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==================================================================================================================
# ==================================================================================================================
# THIS IS THE FIRST STEP IN THE PIPELINE. IT CAN BE RUN FROM THE COMMAND LINE
# ==================================================================================================================
# ==================================================================================================================

if __name__ == '__main__':

    # General settings
    loadDataFromCommandLine = False  # change here to enable/disable hard coded settings
    be_verbose = True
    use_mallet_model = True

    pos_list = ["NOUN"]  # ["NOUN", "VERB", "ADV", "ADJ"]
    lemmaPickleFile = "resources/nlp/corpusLemmas-nouns.p"
    fileNamePickleFile = "resources/nlp/corpusFileNames-nouns.p"
    bigramPickleFile = "resources/nlp/corpusBigrams-nouns.p"
    trigramPickleFile = "resources/nlp/corpusTrigrams-nouns.p"

    id2wordPickleFile = "resources/nlp/id2word-nouns.p"
    textsPickleFile = "resources/nlp/texts-nouns.p"
    corpusPickleFile = "resources/nlp/corpus-nouns.p"

    # ==================================================================================================================
    # STEP 0: Obtain user settings
    # ==================================================================================================================
    if loadDataFromCommandLine:
        if len(sys.argv) < 5:
            print("Call:\n> python3 topic_main-depricated.py STR_INDIR STR_OUTDIR BOOL_USE_PICKLED_DATA SAVE_AS_PICKLE")
            sys.exit(0)
        in_dir = sys.argv[1]
        out_dir = sys.argv[2]
        use_pickled_data = sys.argv[3].lower() == "true"
        save_as_pickle = sys.argv[4].lower() == "true"
    else:
        if be_verbose:
            print("Using hard coded settings")
        in_dir = "/Users/zweiss/Documents/Forschung/Projekte/kansas/texts/"
        out_dir = "/Users/zweiss/Documents/Forschung/Projekte/kansas/ANSAS-TopicModeling2/"
    os.makedirs(out_dir, exist_ok=True)

    # ==================================================================================================================
    # STEP 1: Get NLP annotation of all data files and extract content lemmata
    # ==================================================================================================================
    if be_verbose:
        print("Starting NLP annotation")
    nlp = stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma')  # initialize pipeline
    all_corpus_files = rec_file_list(in_dir, file_ending=".txt")  # get all files from input dir
    # all_corpus_files = all_corpus_files[:10]  # only for testing of the pipeline

    corpus_lemmas = []
    corpus_file_names = []
    nfiles = len(all_corpus_files)
    issue = []
    for i, c_file in enumerate(all_corpus_files):
        if be_verbose:
            print("... {}/{}".format(i, nfiles))
        try:
            c_text = load_text(c_file)
        except UnicodeDecodeError:
            with open(c_file, 'r', encoding="iso-8859-1") as fr:
                with open(c_file, 'w', encoding="utf-8") as fw:
                    for line in fr:
                        fw.write(line)
            issue.append(c_file)  # sanity check, should be zero thanks to workaround

        # ignore empty files
        if len(c_text) == 0:
            continue
        doc = nlp(c_text)

        content_lemmas = extract_content_lemmas(annotated_document=doc,
                                                set_content_pos=pos_list)
        corpus_lemmas.append(content_lemmas)
        corpus_file_names.append(c_file)
    if be_verbose:
        print("NLP annotation complete: {} annotations / {} file names".format(len(corpus_lemmas),
                                                                               len(corpus_file_names)))
    # save documents
    if be_verbose:
        print("Pickling corpus data")
    pickle.dump(corpus_lemmas, open(lemmaPickleFile, "wb"))
    pickle.dump(corpus_file_names, open(fileNamePickleFile, "wb"))

    # ==================================================================================================================
    # STEP 2: Calculate bigrams and trigrams
    # ==================================================================================================================
    if be_verbose:
        print("Calculating ngrams")
    data_words_bigrams = calculate_ngram_model(txt_data=corpus_lemmas, min_count=5, threshold=100)
    data_words_trigrams = calculate_ngram_model(txt_data=data_words_bigrams, threshold=100)
    if be_verbose:
        print("Pickling ngrams")
    pickle.dump(data_words_bigrams, open(bigramPickleFile, "wb"))
    pickle.dump(data_words_trigrams, open(trigramPickleFile, "wb"))

    # ==================================================================================================================
    # STEP 3: Create the Dictionary
    # ==================================================================================================================
    id2word = corpora.Dictionary(data_words_trigrams)
    texts = data_words_trigrams  # Create Corpus
    corpus = [id2word.doc2bow(text) for text in texts]  # Term Document Frequency

    if be_verbose:
        print("Pickling dictionary data")
    pickle.dump(id2word, open(id2wordPickleFile, "wb"))
    pickle.dump(texts, open(textsPickleFile, "wb"))
    pickle.dump(corpus, open(corpusPickleFile, "wb"))

    # View
    if be_verbose:
        # For example, (0, 1) in id2word[:1] implies, word id 0 occurs once in the first document.
        # Likewise, word id 1 occurs twice and so on.
        # If you want to see what word a given id corresponds to, pass the id as a key to the dictionary.
        # Human readable format of corpus (term-frequency)
        print([[(id2word[cid], freq) for cid, freq in cp] for cp in corpus[:1]])
