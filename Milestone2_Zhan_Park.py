
##################################
#Jing Zhan, Hyun Soo Park
#2016.11.9
#2016.11.11
#This project calcualtes the publications, keywords and author numbers ignoring case.
###################################
# -*- coding: utf-8 -*-

import re

def processFile(fileName):
    try:
        file1 = open(fileName, 'r')
        line = file1.readline()
        publication_count = 0
        keywords_list = []
        authors_list = []
        keywords_String = ""
        while line != '':
            if line.startswith('doi:'): #find publications
                publication_count += 1
            elif line.strip().startswith('keywords: {'): #find keywords
                keywords = ''
                while '}' not in line: #keywords end
                    keywords += line.rstrip() + ' '
                    line = file1.readline()
                keywords += line.rstrip() + ' '
                start = keywords.index('{')
                end = keywords.index('}')
                keywords = keywords[start+1: end].lower() #change all keywords to lower case
                keywords_list += keywords.split(';') #split all keywords by ;
            elif line.startswith('\n'): #find author, after this line there is author
                line = file1.readline()
                if line.startswith('"['):#exclude the first two covers
                    continue
                authors = ''
                while '"' not in line:
                    authors += line.rstrip() + ' '
                    line = file1.readline()
                authors += line.rstrip() + ' '
                end = authors.index('"')
                authors = authors[0: end-2]
                authors = authors.replace(' and ', ', ')#replace and
                authors_list += re.split(', ', authors)#plit by ,
            line = file1.readline()
        print(publication_count - 2) #first 2 are cover, not counted
        print(len(set(keywords_list)))#no duplicate count
        print(len(set(authors_list)))#no duplicate count
        file1.close()
    except IOError:
        print('Something wrong')


def main():
    processFile('1.txt') #the text file is named as 1.txt


main()