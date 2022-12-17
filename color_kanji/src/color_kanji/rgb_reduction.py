import pandas as pd
from sklearn.decomposition import PCA

# Load the word embeddings from the csv file
df = pd.read_csv("embeddings.csv", header=None, index_col=0)

# Use PCA to reduce the dimensions of the word embeddings to 3
pca = PCA(n_components=2)
reduced_vectors = pca.fit_transform(df)

# Normalize the first value to fit between 0-360 and the second value to fit between 0-100
normalized_vectors = []
for vector in reduced_vectors:
    normalized_vectors.append(
        [
            (vector[0] - reduced_vectors[:, 0].min())
            / (reduced_vectors[:, 0].max() - reduced_vectors[:, 0].min())
            * 360,
            (vector[1] - reduced_vectors[:, 1].min())
            / (reduced_vectors[:, 1].max() - reduced_vectors[:, 1].min())
            * 100,
        ]
    )

# Create a new DataFrame with the normalized vectors and the same index as the original DataFrame. Also, rename the columns to 'hue' and 'saturation'. Add a column called 'lightness' and set it to 50.
normalized_df = pd.DataFrame(
    normalized_vectors, index=df.index, columns=["hue", "saturation"]
)
normalized_df["lightness"] = 50

# Save the normalized vectors to a new csv file called hsl.csv
normalized_df.to_csv("hsl.csv")

# Use a loop to print the hsl colors for each of the characters: 光復香港時代革命五大訴求缺一不可
for character in "光復香港時代革命五大訴求缺一不可":
    print(f"{character} {normalized_df.loc[character]}")
