"""This module contains the main code for the lennon_wall package."""
# imports
import json
import gensim
import pandas as pd
from sklearn.decomposition import PCA


def get_character_colors():
    """Returns an array of hsl colors for the characters 光復香港時代革命五大訴求缺一不可"""
    # load the hsl.csv file
    df = pd.read_csv("hsl.csv", index_col=0)

    # make an array for the hsl colors
    hsl_colors = []
    # use a loop to print the hsl colors for each of the characters: 光復香港時代革命五大訴求缺一不可
    for character in "光復香港時代革命五大訴求缺一不可":
        # add the hsl color to the array.
        # The hsl color is a python array with the hue, saturation, and lightness values.
        hsl_colors.append(df.loc[character].to_list())
    return hsl_colors


def create_svg(i: int = 0) -> None:
    """
    Creates an svg file with squares arranged in a 4x4 grid.
    Each square is the color of one of the characters 光復香港時代革命五大訴求缺一不可
    """
    # get the hsl colors
    hsl_colors = get_character_colors()

    # create the svg file and set it up so that the squares are perfectly centered in the svg file.
    with open(f"lennon_wall{i}.svg", "w", encoding="utf-8") as f:
        f.write(
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="1000"
   height="1000"
   viewBox="0 0 1000 1000"
   version="1.1"
   id="svg37"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/">
  <defs
     id="defs4" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     id="layer1">"""
        )

        # write the squares. Make sure the squares are in a 4x4 grid
        # with 0px spacing between them and 0px padding around the grid.
        # The squares should be 250px wide and 250px tall.
        # The squares should be the color of the characters 光復香港時代革命五大訴求缺一不可
        # The squares should be in the order 光復香港時代革命五大訴求缺一不可
        # The grid should be perfectly centered in the svg file.
        for i in range(4):
            for j in range(4):
                f.write(
                    f"""
            <rect
                width="250"
                height="250"
                x="{j * 250}"
                y="{i * 250}"
                style="fill:hsl(
                {hsl_colors[i * 4 + j][0]},
                {hsl_colors[i * 4 + j][1]}%,
                {hsl_colors[i * 4 + j][2]}%);
                stroke-width:0;stroke:rgb(0,0,0)" />
"""
                )

        # write the svg footer
        f.write(
            """
    </g>
</svg>
"""
        )


# functions
def generate_word_embeddings():
    """
    This function generates word embeddings for the Chinese characters in the corpus.
    """
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


def reduce_embeddings_to_hsl():
    """
    Reduces the word embeddings to 3 dimensions using PCA
    and normalizes the values to fit between 0-360 for hue,
    50-100 for saturation, and 50-100 for lightness.
    """
    # Load the word embeddings from the csv file
    df = pd.read_csv("embeddings.csv", header=None, index_col=0)

    # Use PCA to reduce the dimensions of the word embeddings to 3
    pca = PCA(n_components=3)
    reduced_vectors = pca.fit_transform(df)

    # Normalize the first value to fit between 0-360. Normalize the second two values to fit between 50-100
    normalized_vectors = []
    for vector in reduced_vectors:
        normalized_vector = [
            (vector[0] - reduced_vectors[:, 0].min())
            / (reduced_vectors[:, 0].max() - reduced_vectors[:, 0].min())
            * 360,
            (vector[1] - reduced_vectors[:, 1].min())
            / (reduced_vectors[:, 1].max() - reduced_vectors[:, 1].min())
            * 50
            + 50,
            (vector[2] - reduced_vectors[:, 1].min())
            / (reduced_vectors[:, 1].max() - reduced_vectors[:, 1].min())
            * 50
            + 50,
        ]
        normalized_vectors.append(normalized_vector)

    # Create a new DataFrame with the normalized vectors and the same index as the original DataFrame. Also, rename the columns to 'hue', 'saturation', and 'lightness'
    normalized_df = pd.DataFrame(
        normalized_vectors, index=df.index, columns=["hue", "saturation", "lightness"]
    )

    # Save the normalized vectors to a new csv file called hsl.csv
    normalized_df.to_csv("hsl.csv")


def main():
    """This function runs the main code for the lennon_wall package."""
    for i in range(10):
        generate_word_embeddings()
        reduce_embeddings_to_hsl()
        create_svg(i)


# main
if __name__ == "__main__":
    main()
