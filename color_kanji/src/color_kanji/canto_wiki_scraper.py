"""
This module scrapes random articles from the Cantonese Wikipedia,
and saves the summaries of the articles into a json.
"""
import json
import os
import requests
import regex as re


# Cleans a string of cantonese text to only include Canonical Chinese characters.
def clean_data(content: str) -> str:
    """
    This function cleans the data from a string of Cantonese text.
    It should return only Canonical Chinese characters.
    Also removes the strings "光復香港", "時代革命" "五大訴求" "缺一不可" from the text.
    This ensures that the colors of the squares are not too similar.
    """
    # Clean the data using a regex
    content = re.sub(r"[^\p{Han}]", "", content)
    # Clean the data using a regex to remove the strings to be used in the artwork.
    # This ensures that the colors of the squares are not too similar.
    content = re.sub(r"光復香港|時代革命|五大訴求|缺一不可", "", content)
    return content


def get_random_wikipedia_articles(rnlimit: int, json_file: str = "canto_wiki.json"):
    """
    This function gets rnlimit random articles from wikipedia,
    and saves the summaries of the articles into a json.
    """
    # Set the base URL for the MediaWiki API
    base_url = "https://yue.wikipedia.org/w/api.php"

    # Set the parameters for the request
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "grnnamespace": 0,  # Only include articles from the main namespace
        "grnlimit": rnlimit,  # Retrieve rnlimit random articles
        "prop": "extracts",  # Include the article text in the response
        "exintro": "",  # Only include the intro text of the article
        "explaintext": "",  # Return the text in plain text format
        "utf8": 1,  # Encode the response in UTF-8
        "formatversion": 2,  # Use the newer format for the response
    }

    # Send the request and store the response
    response = requests.get(base_url, params=params, timeout=10)

    # Get the list of articles from the response
    articles = response.json()["query"]["pages"]

    # make a list to store the extracts in. Don't include a title for the columns.
    extracts = []

    # Iterate over the articles and concat the extracts to the dataframe
    for article in articles:
        try:
            extracts.append(clean_data(article["extract"]))
            print(extracts[-1])
        # except a keyerror if the article is missing the extract
        except KeyError:
            pass

    # Check if a json file already exists at the path specified by json_file. use os.path
    if not os.path.exists(json_file):
        # save the list to a json file, displaying the chinese characters correctly by setting ensure_ascii to False.
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(
                extracts,
                file,
                indent=2,
                ensure_ascii=False,
                separators=(",", ": "),
                sort_keys=True,
            )
    else:
        # open the json file and load the data
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        # concat the new data to the old data only if the new data is not already in the old data
        for extract in extracts:
            if extract not in data:
                data.append(extract)
        # save the new data to the json file
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                separators=(",", ": "),
                sort_keys=True,
            )


# if name is main
if __name__ == "__main__":
    for i in range(500):
        get_random_wikipedia_articles(25)
