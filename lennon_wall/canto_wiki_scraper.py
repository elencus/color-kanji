"""
This module scrapes random articles from the Cantonese Wikipedia,
and saves the summaries of the articles into a json.
"""
import json
import os
import random
import threading
import time
import requests
import regex as re

STOP_WORDS = r"一啲|一定|不如|不過|之後|乜|乜嘢|人哋|但係|你|你哋|佢|佢哋|係|個|其他|冇|再|到|即|即係|原來|去|又|可以|可能|同|同埋|吖|呀|呢|咁|咗|咩|咪|哦|哩|哩個|哩啲|哩度|哩樣|唔|唔使|唔係|啊|啲|喎|喺|喺度|嗯|嗰|嗰個|嗰啲|嗰度|嘅|嘢|噉|噉樣|因為|多|太|好|如果|就|已經|幾|幾多|得|想|應該|成日|我|我哋|或者|所以|最|會|有|有冇|有啲|未|梗係|然之後|由|真係|睇|知|而|而家|自己|要|覺得|話|諗|講|譬如|跟住|返|過|邊個|都|點|點樣|點解|"

# Cleans a string of cantonese text to only include Canonical Chinese characters.
def clean_data(content: str) -> str:
    """
    This function cleans the data from a string of Cantonese text.
    It should return only Canonical Chinese characters.
    Also removes the strings "光復香港", "時代革命" "五大訴求" "缺一不可" from the text.
    This ensures that the colors of the squares are not too similar.
    """
    regexes = [r"[^\p{Han}]", r"光復|香港|時代|革命|五大訴求|訴求|缺一不可", STOP_WORDS]
    # Clean the data using all the regexes:
    for regex in regexes:
        content = re.sub(regex, "", content)
    return content


def get_random_wikipedia_articles(rnlimit: int = 25, json_file: str = "canto_wiki"):
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
        # except a keyerror if the article is missing the extract
        except KeyError:
            pass

    with open(
        f"{json_file}{random.randint(0, 1000000)}.json", "w", encoding="utf-8"
    ) as file:
        json.dump(
            extracts,
            file,
            indent=2,
            ensure_ascii=False,
            separators=(",", ": "),
            sort_keys=True,
        )


# function to join together the data from the json files
def join_json_files():
    """
    This function joins together the data from the json files.
    """
    duplicate_count = 0
    extract_count = 0
    # get a list of all the json files in the directory that have the name canto_wiki
    json_files = [
        file
        for file in os.listdir()  # iterate over the files in the directory
        if file.startswith(
            "canto_wiki"
        )  # only include files that start with canto_wiki
    ]
    # check if corpus.json already exists in os.listdir. If it does, extract the data and save it as a list named extracts.
    if "corpus.json" in os.listdir():
        with open("corpus.json", "r", encoding="utf-8") as file:
            extracts = json.load(file)
    else:
        # make a list to store the extracts in. Don't include a title for the columns.
        extracts = []
    # iterate over the json files
    for json_file in json_files:
        # open the json file and load the data
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        # concat the new data to the old data only if the new data is not already in the old data
        for extract in data:
            extract_count += 1
            if extract not in extracts:
                extracts.append(extract)
            else:
                duplicate_count += 1
    # delete the old json files based on a regex pattern that matches the name of the json files
    # this regex only contains the name of the json files that have at least one digit in the name
    for file in os.listdir():
        if re.match(r"canto_wiki\d+.json", file):
            os.remove(file)
    # save the new data to the json file
    with open("corpus.json", "w", encoding="utf-8") as file:
        json.dump(
            extracts,
            file,
            indent=2,
            ensure_ascii=False,
            separators=(",", ": "),
            sort_keys=True,
        )
    return (duplicate_count / extract_count) * 100


def main():
    """
    This function runs the main program.
    """
    duplicate_percent = 0
    iterations = 0
    # iterate thru as long as less than 30% of results are duplicates
    while duplicate_percent < 30:
        iterations += 1
        # use threading to run the function in parallel
        threading.Thread(target=get_random_wikipedia_articles).start()
        # log the number of threads currently running
        time.sleep(0.2)
        # Check if there are any valid json files in os.listdir
        if any(
            file.startswith("canto_wiki") for file in os.listdir()
        ):  # only include files that start with canto_wiki
            current_duplicate_percent = join_json_files()
            # Adjust the duplicate percent so that it reflects
            # the average duplicate percent across all iterations
            duplicate_percent = (
                (duplicate_percent * (iterations - 1)) + current_duplicate_percent
            ) / iterations
            print(
                f"Duplicate percent: {duplicate_percent},"
                f"threads running: {threading.active_count()}"
            )
    time.sleep(10)
    join_json_files()


# if name is main
if __name__ == "__main__":
    main()
