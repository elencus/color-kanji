"""This module contains the main code for the lennon_wall package."""
# imports
import json
import gensim
import numpy as np
import pandas as pd
import regex as re
import xml.etree.ElementTree as ET


def get_character_colors(characters: str = "光復香港時代革命五大訴求缺一不可") -> list:
    """Returns an array of hsl colors for the characters specified"""
    # load the hsl.csv file
    df = pd.read_csv("hsl.csv", index_col=0)

    # make an array for the hsl colors
    hsl_colors = []
    # use a loop to print the hsl colors for each of the characters specified in the characters param.
    for character in characters:
        # add the hsl color to the array.
        # The hsl color is a python array with the hue, saturation, and lightness values.
        hsl_colors.append(df.loc[character].to_list())
    return hsl_colors


def create_svg(characters: str = "光復香港時代革命五大訴求缺一不可") -> None:
    """
    Creates an svg file with squares arranged in a square grid.
    Each square is the color of one of the characters specified previously.
    """
    # Asserts that the number of characters is a square number.
    assert np.sqrt(len(characters)) % 1 == 0

    # get the hsl colors
    hsl_colors = get_character_colors(characters=characters)

    # Assign a variable as the grid width and height
    grid_size = int(np.sqrt(len(characters)))

    # create the svg file and set it up so that the squares are perfectly centered in the svg file.
    with open(f"lennon_wall.svg", "w", encoding="utf-8") as f:
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
        for i in range(grid_size):
            for j in range(grid_size):
                f.write(
                    f"""
            <rect
                width="{1000/grid_size}"
                height="{1000/grid_size}"
                x="{j * 1000/grid_size}"
                y="{i * 1000/grid_size}"
                style="fill:hsl(
                {hsl_colors[i * grid_size + j][0]},
                {hsl_colors[i * grid_size + j][1]}%,
                {hsl_colors[i * grid_size + j][2]}%);
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
def generate_word_embeddings() -> None:
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
    model = gensim.models.Word2Vec([characters], vector_size=300)

    # Save the word embeddings in a CSV file
    with open("embeddings.csv", "w", encoding="utf-8") as f:
        for character, embedding in zip(model.wv.index_to_key, model.wv.vectors):
            f.write(f"{character},{','.join(str(x) for x in embedding)}\n")


def reduce_embeddings_to_hsl() -> list:
    """
    Changes and offsets the embedding values to fit between 0-360 for hue,
    0-100 for saturation, and 0-90 for lightness.
    The first three embeddings represent the hue, saturation, and lightness values.
    The remaining embeddings are used as offsets for hue.
    """
    # Load the word embeddings from the csv file
    df = pd.read_csv("embeddings.csv", header=None, index_col=0)

    # Normalize the embeddings to fit between 0-1
    df = (df - df.min()) / (df.max() - df.min())

    # The first three embeddings represent the hue, saturation, and lightness values.
    raw_vectors = df.iloc[:, :3].to_numpy()

    # The last 297 embeddings are used as offsets for hue.
    # Beginning with the last embedding, add it to the previous embedding.
    # If the offset is greater than 1, wrap it around to 0.
    # Repeat this process until all of the 297 embeddings have been added into a single offset.
    for i in range(297):
        raw_vectors[:, 0] += df.iloc[:, -i - 1]
        raw_vectors[:, 0] = raw_vectors[:, 0] % 1

    # Add the offset to the hue values:
    raw_vectors[:, 0] += raw_vectors[:, 0].min()

    # Flip the saturation and lightness values so that they are closer to 100.
    raw_vectors[:, 1] = 1 - raw_vectors[:, 1]
    raw_vectors[:, 2] = 1 - raw_vectors[:, 2]

    # Normalize the saturation values to fit between 0-100.
    # Normalize the hue values to fit between 0-360.
    # Normalize the lightness values to fit between 30-70.
    normalized_hsl_vectors = np.array(raw_vectors)
    normalized_hsl_vectors[:, 0] = (
        (normalized_hsl_vectors[:, 0] - normalized_hsl_vectors[:, 0].min())
        / (normalized_hsl_vectors[:, 0].max() - normalized_hsl_vectors[:, 0].min())
        * 360
    )
    normalized_hsl_vectors[:, 1] = (
        (normalized_hsl_vectors[:, 1] - normalized_hsl_vectors[:, 1].min())
        / (normalized_hsl_vectors[:, 1].max() - normalized_hsl_vectors[:, 1].min())
    ) * 100
    normalized_hsl_vectors[:, 2] = (
        (normalized_hsl_vectors[:, 2] - normalized_hsl_vectors[:, 2].min())
        / (normalized_hsl_vectors[:, 2].max() - normalized_hsl_vectors[:, 2].min())
        * 90
    )

    # Create a new DataFrame with the normalized vectors and the same index
    # as the original DataFrame. Also, rename the columns to 'hue', 'saturation', and 'lightness'
    normalized_df = pd.DataFrame(
        normalized_hsl_vectors,
        index=df.index,
        columns=["hue", "saturation", "lightness"],
    )

    # Save the normalized vectors to a new csv file called hsl.csv
    normalized_df.to_csv("hsl.csv")


def decode_svg() -> list:
    """
    This function decodes the svg file back into characters using the following steps:
    1. Read the hsl colors from the svg file for each square.
    2. Apply the inverse of the transformations done in the reduce_embeddings_to_hsl function
    to get the original embeddings.
    3. Find the character with the closest embeddings to the original embeddings.
    4. Return the characters in the order they appear in the svg file.
    """
    # Load the hsl values from the csv file
    df = pd.read_csv("hsl.csv", index_col=0)

    # Use xml.etree.ElementTree to parse the svg file
    tree = ET.parse("lennon_wall.svg")
    root = tree.getroot()

    # Get the hsl values for each square in the svg file
    # by getting the style attribute for each rectangle element
    # and extracting the hsl values from the string
    # Remove any noninteger characters so that we don't get a valueerror when converting to float
    # Also, make sure we don't get a valueerror because we can't convert string to float
    hsl_values = []
    for rect in root.iter(r"{http://www.w3.org/2000/svg}rect"):
        hsl_values.append(
            [
                float(re.sub(r"[^\d.]", "", x))
                for x in rect.attrib["style"].split(";")[0].split(":")[1].split(",")
            ]
        )

    # undo the transformations done in the reduce_embeddings_to_hsl function
    # to get the original embeddings
    hsl_values = np.array(hsl_values)
    hsl_values[:, 0] = (
        hsl_values[:, 0] / 360 * (df["hue"].max() - df["hue"].min()) + df["hue"].min()
    )
    hsl_values[:, 1] = (
        hsl_values[:, 1] / 100 * (df["saturation"].max() - df["saturation"].min())
        + df["saturation"].min()
    )
    hsl_values[:, 2] = (
        hsl_values[:, 2] / 90 * (df["lightness"].max() - df["lightness"].min())
        + df["lightness"].min()
    )

    # Find the character with the closest embeddings to the original embeddings
    # and return the characters in the order they appear in the svg file
    characters = []
    for hsl in hsl_values:
        characters.append(
            df.iloc[
                np.argmin(np.linalg.norm(df.iloc[:, :3].to_numpy() - hsl, axis=1))
            ].name
        )
    return characters


def main():
    """This function runs the main code for the lennon_wall package."""
    generate_word_embeddings()
    reduce_embeddings_to_hsl()
    create_svg(characters="光復香港時代革命五大訴求缺一不可")

    # Decode the svg file back into characters
    characters = decode_svg()
    print("".join(characters))


# main
if __name__ == "__main__":
    main()
