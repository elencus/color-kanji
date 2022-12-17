import pandas as pd
from sklearn.decomposition import PCA

# Load the word embeddings from the csv file
df = pd.read_csv("embeddings.csv", header=None, index_col=0)

# check to see if df contains any NaN values
print(df.isnull().values.any())

# Use PCA to reduce the dimensions of the word embeddings to 3
pca = PCA(n_components=3)
reduced_vectors = pca.fit_transform(df)

# Normalize the reduced vectors to the range 0-255
min_value = reduced_vectors.min()
max_value = reduced_vectors.max()
normalized_vectors = (reduced_vectors - min_value) / (max_value - min_value) * 255

# Create a new DataFrame with the normalized vectors and the same index as the original DataFrame
normalized_df = pd.DataFrame(normalized_vectors, index=df.index)

# Save the normalized vectors to a new csv file called 'rgb.csv'
normalized_df.to_csv("rgb.csv")
