from Book import Book 
from collections import defaultdict
from bs4 import BeautifulSoup
import bs4
from urllib import request
import urllib
import time
import random
import re
import os
import glob

class SongShu(Book):
    """SongShu Dataset
    
    Attributes:
        flat_meta : a list of bookmarks in SonShu extracted from Han-Ji
        flat_passages : a list of ``passages`` in SongShu. 
            Each ``passages`` contain a list of passage in a piece of work.
            i.e., flat_passages = [passages1(list, passages2(list), ...]
                  passages1 = [passage1(str), passage2(str), ...]    
                  
    Args: same as Book class
    
    Methods:
        extract_meta(): Extract meta data from self.paths. Index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title. The method would check the author name using author_bag automatically.    
        extract_passages(): Extract passages based on indent==2 & padding==0. 
                            If there's no passage in this page, merge all texts into one string.
    """
    
    def __init__(self, date, creator, description=''):
        Book.__init__(self, 'SongShu', date, creator, description)

    def extract_meta(self):
        self.flat_meta = []
        for path in self.paths:
            meta = {}
            bookmark_split = path.split('／')

            # Navie implementation
            category = bookmark_split[3].split('\u3000')[0] # 本紀、志、列傳
            scroll   = bookmark_split[4].split('\u3000')[0] # 卷 N 
            categrory_number   = bookmark_split[4].split('\u3000')[1] # 本紀第 N 
            title = '/'.join(bookmark_split[5:]).replace('..[底本：宋元明三朝遞修本]', '')
            meta['category'] = category
            meta['category_number'] = categrory_number
            meta['scroll'] = scroll
            meta['title']  = title
            self.flat_meta.append(meta)

    def extract_passages(self):
        '''Extract passages from SongShu, which divided by the ( indent == 2 & padding == 0 )'''
        self.flat_passages = []

        for body,path in zip(self.flat_bodies, self.paths):
            texts  = body.find_all('div', attrs={'style': True})
            try:
                self.flat_passages.append(
                    self._passage2paragraphs(texts)
                )
            except IndexError as e:
                print("[Warning] Not the right indent.", path)
                self.flat_passages.append(
                    ''.join([text.text for text in texts])
                )


    def _passage2paragraphs(self, texts):
        '''Organize a passage with its paragraph, which is defined using ( indent == 2& padding == 0 )
        '''
        # concatenent the paragraphs with indents not equal to 2 to the previous paragraph
        new_texts = []
        
        # get the pairs of indents and paddings 
        indent_padding_list = self._indent_and_padding(texts)
        
        for text, (indent, padding) in zip(texts, indent_padding_list):
            if indent == 2 and padding == 0:
                # only save the text, without tags
                new_texts.append(
                    ''.join([s for s in text if isinstance(s, bs4.NavigableString)])
                )
            else:
                new_texts[-1] += ''.join([s for s in text if isinstance(s, bs4.NavigableString)])
            
        return new_texts   