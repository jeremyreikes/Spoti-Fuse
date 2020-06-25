import spacy
nlp = spacy.load('en')

def lemmatize(text, return_lang=False):
    doc = nlp(text)
    lemmas = list()
    for token in doc:
        if token.is_stop or not token.is_alpha:
            continue
        lemma = token.lemma_.strip().lower()
        if lemma and lemma not in lemmas:
            lemmas.append(lemma)
    if return_lang:
        return lemmas, doc.lang_
    return lemmas
