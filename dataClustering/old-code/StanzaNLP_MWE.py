import stanza


if __name__ == '__main__':

    # Minimally Working Example from https://stanfordnlp.github.io/stanza/index.html
    # applied to German

    # stanza.download('de')  # download model # only needed once
    nlp = stanza.Pipeline('de')  # initialize English neural pipeline
    doc = nlp("Ich sitze im Schaukelstuhl und schlafe. Hast du damit ein Problem?")  # run annotation over a sentence

    for sentence in doc.sentences:
        for word in sentence.words:
            print(word.text, word.lemma, word.pos)

    print(*[f'word: {word.text+" "}\tlemma: {word.lemma}\tpos: {word.pos}' for sent in doc.sentences for word in sent.words], sep='\n')