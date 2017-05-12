from gensim.models import Word2Vec

model=Word2Vec.load('wiki_word2vec')

model.most_similar(positive=['祖国','人民']，negative=['反面'])
