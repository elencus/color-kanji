import json
import gensim

with open("corpus.json", "r", encoding="utf8") as f:
    data = json.load(f)
    strings = [d for d in data]

# Split the strings into individual Chinese characters
characters = []
for string in strings:
    characters += [c for c in string]

# Train the word2vec model
model = gensim.models.Word2Vec([characters], vector_size=100)

# Save the word embeddings in a CSV file
with open("embeddings.csv", "w", encoding="utf-8") as f:
    for character, embedding in zip(model.wv.index_to_key, model.wv.vectors):
        f.write(f"{character},{','.join(str(x) for x in embedding)}\n")
