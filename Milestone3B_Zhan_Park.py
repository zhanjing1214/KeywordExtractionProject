# Jing Zhan & HyunSoo Park
# 2016.11.17
# 2016.11.18
# This program reads from a raw document to structure it. Once it removes all of the pre-defined noise
# and replace the substitution words, it sorts them in an ascending order (alphabetically).
# Once sorting procedure is done, the program finally writes an html file to put the bag of words connected to URLs
# that are not specified yet.

# -*- coding: utf-8 -*-
from stemming.porter2 import stem
import re
import os


# This function reads from the raw document to extract the abstract, titles, and keywords to put them
# in the inventory String.
def remove_useless_content(file_name):
    inventory = ''
    try:
        with open(file_name, 'r') as inventory_file:
            # while there is still a line to read in the raw document
            while True:
                line = inventory_file.readline()
                # if there is no line, break the loop
                if not line:
                    break
                # if the line starts with a certain substring
                if line.startswith('"[Front'): # skip first 2 covers
                    while not line.startswith("URL"):
                        line = inventory_file.readline()
                if line.startswith("\n"): # get title
                    while ', "' not in line:
                        line = inventory_file.readline()
                    if ',"' in line:
                        inventory += line[line.index(', "')+3: line.index(',"')].rstrip() + ' '
                    else:
                        inventory += line[line.index(', "')+3:].rstrip() + ' '
                        line = inventory_file.readline()
                        while ',"' not in line:
                            inventory += line.rstrip() + ' '
                            line = inventory_file.readline()
                        inventory += line[:line.index(',"')].rstrip() + ' '
                elif line.startswith("Abstract"): # get abstract and keywords{}
                    while not line.startswith("URL:"):
                        inventory += line.rstrip() + ' '
                        line = inventory_file.readline()
                else:
                    continue
        inventory = re.sub(";", '; ', inventory)
    except IOError:
        print("something wrong with remove useless content")
    finally:
        return inventory


# This function reads from the inventory String created by the above function to substitute specific ngrams (n <= 3)
# into compound words
def join_compound_words(inventory):
    # change entire String to lower case to ignore case sensitivity
    inventory = inventory.lower()
    try:
        # reads from the predefined list of compound words
        with open("compound.txt", 'r') as compound_file:
            compound_file.readline() #skip first line
            while True:
                line = compound_file.readline()
                if not line:
                    break
                # spliting the compound file list by the comma
                origin = ' ' + line.split(", ")[0]
                after = ' ' + line.split(", ")[1].rstrip()
                # replacing the words into predefined format
                inventory = re.sub(origin, after, inventory)
            compound_file.close()
    except IOError:
        print('Something wrong in compounds')
    finally:
        return inventory


# performs the same process with above, replace typos and grammatical irregularities etc.
def normalization(inventory):
    # read the inventory String and cut out all the special characters
    inventory = re.sub("[^a-zA-Z0-9-_\s'/]", ' ', inventory)
    try:
        with open("replacements.csv", 'r') as replacements_file:
            replacements_file.readline() # skip title line
            while True:
                line = replacements_file.readline()
                if not line:
                    break
                # read from the replacement.txt and split each line by comma
                origin = ' ' + line.split(",")[0]
                after = ' ' + line.split(",")[1].rstrip()
                inventory = re.sub(origin, after, inventory)
            replacements_file.close()
    except IOError:
        print('Something wrong in normalization')
    finally:
        return inventory


# We used the Porter stemming to structure the document
def stem_inventory(inventory):
    words = inventory.split(" ")
    stem_words = []
    for word in words:
        if "_" in word or '-' in word or "\\" in word: # if they are compound word, then don't stem
            stem_words.append(word)
        else: # if not stem
            stem_words.append(stem(word))
    return stem_words


# This function removes predefined noise words listed in the noise_words.txt
def remove_noise(word_list):
    try:
        with open("noise_words.txt", 'r') as noise_words_file:
            while True:
                line = noise_words_file.readline()
                if not line:
                    break
                # read from the noise word list and remove the white space to extract only the word
                noise_word = line.rstrip()
                for word in word_list:
                    # if the word is in the noise word list, blank, or starts with -, it gets removed
                    if word == noise_word or word == "" or word.startswith('-'):
                        word_list.remove(word)
            noise_words_file.close()
    except IOError:
        print('Something wrong in remove noise')
    finally:
        return word_list


# A simple function sorting the word list in an ascending order
def sort_word(word_list):
    # To remove duplicates, put the bag of words into a set first
    words_set = set()
    for word in word_list:
        words_set.add(word)
    # Sort the set in an ascending order
    sorted_words = sorted(words_set)
    return sorted_words

#
# def count_frequency(word_list):
#     dic = {}
#     for word in word_list:
#         try:
#             dic[word] += 1
#         except KeyError:
#             dic[word] = 1
#     dic_sorted = OrderedDict(sorted(dic.items(), key=lambda x: x[1], reverse = True))
#     for key in dic_sorted.keys():
#         print(key + ": " + str(dic_sorted[key]))
#     return dic


# Creating an html document function
def create_html(word_set):
    # Header String to put at the beginning of the file
    header = '''<!DOCTYPE html>
                <html>
                <head>
                <title>Basic </title>
                </head>
                <body bgcolor="#E6E6FA">
                <h1 style="color:pink;font-family:courier;text-align:center;">Key words</h1>'''
    # String values to put hyper links for the html file
    link_start = '''<p style="font-family:courier;text-align:center;"><a href="some——link">'''
    link_end = '</a></p>'

    # Make sure the file does not exist before appending anything onto it
    try:
        os.remove("index.html")
    except FileNotFoundError:
        pass

    # Create the html file, then append the header and the links for every words in the set
    try:
        html_file = open("index.html", 'w', encoding="utf8")
        html_file.write(header)
        for word in word_set:
            html_file.write(link_start + word + link_end)

        # Add the ending codes for html document
        html_file.write("</body>\
                        </html>")
        html_file.close()
    except IOError:
        print("something wrong with create html")


def main():
    contents = remove_useless_content("downloadCitations.txt")
    contents_with_compounds = join_compound_words(contents)
    normalized_contents = normalization(contents_with_compounds)
    stemmed_list = stem_inventory(normalized_contents)
    list_nonoise = remove_noise(stemmed_list)
    sorted_wordset = sort_word(list_nonoise)
    create_html(sorted_wordset)


main()

