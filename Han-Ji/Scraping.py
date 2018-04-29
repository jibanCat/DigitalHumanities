#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:16:18 2018
@author: jibanCat
"""
import urllib
from urllib import request
from bs4 import BeautifulSoup
import bs4
import random
import time

# pandas DataFrame
import pandas as pd

# argument parser 
import argparse


def DataFrame_passage_comment(texts):
    '''
    Input texts object (bs4.element.ResultSet) and return 
    a DataFrame which seperate 
    the passages and comments (with <font size="-2"></font> tag)
    into different columns. 
    '''
    # get all elements (includes passages and comments) into a long list,
    # which means make a whole page html into a list, 
    # such that text = [passage, ..., comment, ..., passage, ...]
    text = [item for sublist in texts for item in list(sublist)]

    # filter out irrevelant elements, leave only passages and 
    # comments with font size = '-2'
    textIter = filter(lambda x : 
        isinstance(x, bs4.element.NavigableString) 
        # modification here to make sure all sizes fit in, not only size = -2
        or ('size' in x.attrs
        if isinstance(x, bs4.element.Tag) else False), 
        text)

    # the list to append (passage, comment) tuples
    List = []

    # buffer lists to store passages and tags independently
    buffer_text = []
    buffer_tag  = []

    for t in textIter:
        # This is the tricky part, takes me lots of time to figure it out. 
        # since the ordering of text and tag is like
        # ['text', ..., 'tag, ..., 'text'(next text element after a series of tags), ... ]
        # we should :
        if ( len(buffer_text) > 0 and # count at least one text element
             len(buffer_tag) > 0 and  # count at least one tag element
            # and make sure # we have already looped to
            # **the next text element after tags**
             isinstance(t, bs4.element.NavigableString) ): 

            # append tuple (text, tag), which means (passage, comment)
            List.append((''.join(buffer_text), ''.join(buffer_tag)))

            # clear buffer lists to be empty
            buffer_text.clear()
            buffer_tag.clear()

        # if t is passage (bs4.element.NavigableString):
        # force bs4.element.NavigableString to be str and append to the list    
        if isinstance(t, bs4.element.NavigableString):
            buffer_text.append(str(t)) 

        # else if t i a tag (bs4.element.Tag):
        # find all texts in tag and strip the childern tags. 
        # append all into the list        
        elif isinstance(t, bs4.element.Tag):
            buffer_tag.append(
                ''.join(t.find_all(text=True, recursive=False))
            )

    # append anything else leave in th buffer lists into List
    # and remember to exclude the spaces.
    if (not ''.join(buffer_text).isspace() and 
        not ''.join(buffer_tag).isspace()):
        List.append((''.join(buffer_text), ''.join(buffer_tag)))
    
    return pd.DataFrame(List, columns=['passage', 'comment'])


def main(args):
    
    BASE_URL = 'http://hanchi.ihp.sinica.edu.tw/ihpc/'
    
    # first page, parse from argument parser
    url = args.URL
    
    #### Loop over the pages ##################################################
    for i in range(1000):
        URL = urllib.parse.urljoin(BASE_URL, url)
        
        # use urllib.request to get the html content of the web
        req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        page = request.urlopen(req)
        
        #### Beautiful soup tag finding process ###############################
        # convert html object to BeautifulSoup object
        soup = BeautifulSoup(page, 'lxml')
        
        # <span id="fontstyle"> is the parent of head and passages
        body  = soup.find_all('span', {'id' : 'fontstyle'})[0]
        
        # extract heads <h3>
        heads = body.find_all('h3')
        
        # extract gobookmark as filename
        filename  = soup.find('a', attrs={'class', 'gobookmark'}).text.split('／')[-1]
        
        # passage in inside <div style="XXX" > tag
        # it is tricky here since style="text-indent:Xem;padding-left:Xem;">
        # indent and padding are not constants. 
        texts  = body.find_all('div', attrs={'style': True})

        # find author (it is optional, not every passages have authors),
        # author here is a string
        try:
            author = body.find('div', attrs={"align": True}).text
        except AttributeError as e:
            print('[Warning] no author in {} page, skip the author.'.format(i),
                  e)
            author = ''
        
        ##### Makeing dataframe table in the form of | passage | comment | ####
        # make a dataframe of header
        df_heads = DataFrame_passage_comment(heads)
        df_heads['author'] = author # add a column for the author name

        # make a dataframe of passages
        df_passages = DataFrame_passage_comment(texts)
        
        # saving dataframe
        df_heads.to_csv('{}_Head_{}.csv'.format(i, filename))
        df_passages.to_csv('{}_Passage_{}.csv'.format(i, filename))        
        
        #### finding the next page ############################################
        # <img src="/ihp/snext.gif"> is the children of the <a href="(URL of next page)">
        next_page = soup.find('img', {'src' : '/ihp/snext.gif'})
        if next_page != None:
            url = next_page.find_parent()['href']
        else:
            print('No further next page!')
            break
        
        # randomly sleep for 2~5 second 
        time.sleep(random.randint(2, 5))
        
if __name__ == "__main__":
    # argument parser, building flags
    parser = argparse.ArgumentParser()
    parser.add_argument('--URL', type=str, 
                        help='The start page you want to scrape in Han-Ji')
    args = parser.parse_args()                        
    
    # usage:
    # python Scraping --URL=hanji?@72^74245715^802^^^60407005000900010001@@355855896
    # but it is okay if users input --URL=http://hanchi.ihp.sinica.edu.tw/ihpc/hanji?@72^74245715^802^^^60407005000900010001@@355855896
    # because urllib.parse.urljoin will handle this situation
    main(args)