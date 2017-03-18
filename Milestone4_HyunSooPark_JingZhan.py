# Author Name:			HyunSoo Park, Jing Zhan		
# Original Creation Date:	12/07/2016
# Last Modification Date:	12/07/2016
# Description:                  This program builds on top of all of the past
#                               milestone programs which reads from a text file
#                               to structure the text file to extract keywords.
#                               The program then separates the original text
#                               into individual articles, then structure them,
#                               then link the article's author & title with
#                               the given title.
#                               As a final touch, each link will be correctly
#                               led to the article's webpage.

import re
import os
from stemming.porter2 import stem

# This function reads from the raw document to extract the abstract, titles, 
# and keywords to put them in the inventory String.
def remove_useless_content(file_name):
    inventory = ''
    try:
        with open(file_name, 'r', encoding='UTF-8') as inventory_file:
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
                    line = inventory_file.readline()
                    if not line:
                        break
                    #if the line does not contain the beginning index for title
                    while ', "' not in line:
                        line = inventory_file.readline()
                    #if the line contains the title
                    if ',"' in line:
                        inventory += line[line.index(', "')+3: line.index(',"')].rstrip() + ' '
                    else:
                        inventory += line[line.index(', "')+3:].rstrip() + ' '
                        line = inventory_file.readline()
                        if not line:
                            break
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
        inventory_file.close()
        return inventory


# This function reads from the inventory String created by the above function to substitute specific ngrams (n <= 3)
# into compound words
def join_compound_words(inventory):
    # change entire String to lower case to ignore case sensitivity
    inventory = inventory.lower()
    try:
        # reads from the predefined list of compound words
        with open("Milestone4_Compound_HyunSooPark_JingZhan.txt", 'r', encoding='UTF-8') as compound_file:
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
        with open("Milestone4_Sub_HyunSooPark_JingZhan.csv", 'r', encoding='UTF-8') as replacements_file:
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
        with open("Milestone4_Del_HyunSooPark_JingZhan.txt", 'r', encoding='UTF-8') as noise_words_file:
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
    link_start = '''<p style="font-family:courier;text-align:center;"><a href='''
    link_middle = '.html>'
    link_end ='</a></p>'

    # Make sure the file does not exist before appending anything onto it
    try:
        os.remove("index.html")
    except FileNotFoundError:
        pass

    # Create the html file, then append the header and the links for every words in the set
    try:
        html_file = open("index.html", 'a', encoding='UTF-8')
        html_file.write(header)
        for word in word_set:
            html_file.write(link_start + "keywords/" + word.replace('/', '_') + link_middle + word + link_end)

        # Add the ending codes for html document
        html_file.write("</body>\
                        </html>")
        html_file.close()
    except IOError:
        print("something wrong with create html")


# This function reads from the given file name to extract the author, title, abstract, and the
# keywords from the document
def get_paper(file_name):
    #declaring three lists to put extracted data
    author_title_list = []
    abstract_list = []
    keyword_list = []
    try:
        with open(file_name, 'r', encoding='UTF-8') as inventory_file:
            # while there is still a line to read in the raw document
            while True:
                line = inventory_file.readline()
                if not line:
                    break
                #use the nextline regex to find an article to read
                if line.startswith('\n'):
                    line = inventory_file.readline()
                    if not line:
                        break
                    if line.startswith('"[Front'):  # ignore the first two covers
                        continue
                    author_title = ''
                    while ',"' not in line:  # get titles and authors
                        author_title += line.rstrip() + ' '
                        line = inventory_file.readline()
                    index = line.index(',"')
                    author_title += line[: index] + '"'
                    author_title_list.append(author_title)
                elif line.startswith('Abstract:'):  # get abstracts
                    abstract = ''
                    while '.\n' not in line:
                        abstract += line.rstrip() + ' '
                        line = inventory_file.readline()
                    abstract += line.rstrip()
                    abstract_list.append(abstract)
                elif line.startswith(' keywords:'):  # get keywords
                    keywords = ''
                    while '},' not in line:
                        keywords += line.rstrip() + ' '
                        line = inventory_file.readline()
                    keywords += line.rstrip()
                    keyword_list.append(keywords)
                else:
                    pass
        del abstract_list[0:2]  # remove the first two abstracts from cover as they are not articles
    except IOError:
        print("something wrong with remove useless content")
    finally:
        inventory_file.close()
        return author_title_list, abstract_list, keyword_list


# this method generates the html for each paper
def generate_html(author_title_list, abstract_list, keyword_list):
    if not os.path.exists("articles"):
        os.makedirs("articles")
    for i in range(len(author_title_list)):
        # Header String to put at the beginning of the file
        header = '''<!DOCTYPE html>
                    <html>
                    <head>
                    <title>Basic</title>
                    </head>
                    <body bgcolor="#E6E6FA"><br><br><br>'''

        # Make sure the file does not exist before appending anything onto it
        try:
            os.remove("articles/article_number_" + str(i) + ".html")
        except FileNotFoundError:
            pass

        # Create the html file, then append the header and the links for every words in the set
        try:
            html_file = open("articles/article_number_" + str(i) + ".html", 'a', encoding="UTF-8")
            html_file.write(header)
            html_file.write('<h3 style="color:black;font-family:courier;">' +
                            author_title_list[i] + "</h3>")
            html_file.write('<p style="color:grey;font-family:courier;">' + abstract_list[i] + "</p>")            
            # Add the ending codes for html document
            html_file.write("</body>\
                            </html>")
            html_file.close()
        except IOError:
            print("something went wrong while creating html for articles")


#This function re-combine the separately extracted author, title, abstract,
#and the keywords so the new list contains individual article
def combine(author_title_list, abstract_list, keyword_list):
    paper = []
    for i in range(len(author_title_list)):
        paper.append(author_title_list[i] + " " + abstract_list[i] + " " + keyword_list[i])
    #returning the list of individual articles
    return paper


#This funtion structure each article the same way the entire document was structured
def cleanPaper(paper):
    str_paper = []
    for i in range(len(paper)):
        contents = str(paper[i])
        # Joining compound concepts
        contents_with_compounds = join_compound_words(contents)
        # Perform normalization
        normalized_contents = normalization(contents_with_compounds)
        # Perform stemming
        stemmed_list = stem_inventory(normalized_contents)
        # Noise / stop words removal
        list_nonoise = remove_noise(stemmed_list)
        str_paper.append(list_nonoise)
    return str_paper


#This funtion structures the entire document to extract keywords
def get_keywords():
    # read from inventory
    contents = remove_useless_content("downloadCitations.txt")
    # Joining compound concepts
    contents_with_compounds = join_compound_words(contents)
    # Perform normalization
    normalized_contents = normalization(contents_with_compounds)
    # Perform stemming
    stemmed_list = stem_inventory(normalized_contents)
    # Noise / stop words removal
    list_nonoise = remove_noise(stemmed_list)
    # sorted the keyword in ascending
    sorted_wordset = sort_word(list_nonoise)
    # Make an html page of the keywrods
    create_html(sorted_wordset)
    return sorted_wordset


#This function links the extracted keywords to each article
def link_keyword_all_paper(sorted_wordset, paper, author_title_list):
    #for every keyword in from the entire document
    for keyword in sorted_wordset:
        index_list = []
        #going through the keywords in individual article
        for i in range(len(paper)):
            #if the keyword is found in the article
            if link_keywords_single_paper(keyword, paper[i], i):
                #add the index of the article to the index_list
                index_list.append(i)
        #make an html page with all the articles in the list for the keyword
        write_html(keyword, index_list, author_title_list)


#This function checks if the keyword is contained in the single article's keywords list
def link_keywords_single_paper(keyword, single_paper, index):
    #for every keyword for a single paper
    for word in single_paper:
        #if the document's keyword is contained in the individual article's 
        #keyword list, return true
        if keyword.lower() == word.lower():
            return True
    return False


#This funtion makes an html page of a single keyword for all the articles that 
#contain the keyword
def write_html(keyword, index_list, author_title_list):
    if not os.path.exists("keywords"):
        os.makedirs("keywords")
    #html header to be put at the top of the html page
    header = '''<!DOCTYPE html>
                    <html>
                    <head>
                    <title>Basic</title>
                    </head>
                    <body bgcolor="#E6E6FA"><br>
                    <h4 style="color:pink;font-family:courier;text-align:left;"> Articles Including Keyword: '''
    
    # String values to put hyper links for the html file
    try:
        #if the keyword html already exists, delete it
        os.remove("keywords/" + keyword + ".html")
    except FileNotFoundError:
        pass
    # Create the html file, then append the header and the links for every words in the set
    try:
        #make an keyword html file. Since file name cannot contain '/', replaces 
        #it with '_' if the key word contains the slash
        html_file = open("keywords/" + keyword.replace('/', '_')+'.html', 'w', encoding='UTF-8')
        #writes the header first
        html_file.write(header)
        html_file.write(keyword + '</h4>')
        #adding all of the author and title in the index_list in the body of the html
        for index in index_list:
            html_file.write('<h5 style="color:black;font-family:courier;"><a href="../articles/article_number_' + str(index) + '.html">' + author_title_list[index] + "</a></h5>")
            # Add the ending codes for html document
            html_file.write("</body>\
                            </html>")
        #close the file
        html_file.close()
    except IOError:
        print(keyword + ' wrong')


#main funciton that wraps everything up.
def main():
    author_title_list, abstract_list, keyword_list = get_paper('downloadCitations.txt')
    generate_html(author_title_list, abstract_list, keyword_list)
    paper = combine(author_title_list, abstract_list, keyword_list)
    str_paper = cleanPaper(paper)
    sorted_wordset = get_keywords()
    link_keyword_all_paper(sorted_wordset, str_paper, author_title_list)

main()


