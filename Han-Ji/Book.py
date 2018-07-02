from collections import defaultdict
### WHY "defaultdict", INSTEAD OF THE REGULAR "dict" FUNCTION?
from bs4 import BeautifulSoup
import bs4
from urllib import request
import urllib
import time
import random
import re
import os
import glob


class Book:
    """Han-Ji '<http://hanchi.ihp.sinica.edu.tw/ihp/hanji.htm>'_ Dataset.
    
    Attributes:
        flat_bodies (list): a list containing all htmls 
        flat_passages (list): a list containing the text of all passages (i.e., every individual piece in a book). Users should define their own methods to organize the passages.
        flat_heads (list): a list containing all the text of the heads (i.e., the metadata at the top of each individual piece, like title and author). Users should define their own methods to organize the heads.
        flat_meta (list): a list containing all metadata (dictionary). User sould define their own methods to extract metadata.
        ### I AM CONFUSED ABOUT THIS ONE -- IS IT METADATA FROM THE BOOKMARKS?
        paths (list): a list of paths extracted from the "bookmark" provided in the database. e.g., 集／總集／文選／卷第二十七　詩戊之一／樂府上／古樂府三首／飲馬長城窟行(P.1277)
        author_bag (dict): a dictionary stores all authors name and their comments. The structure is like this: 
            '丘希範': [(88,
               <font size="-2">梁史曰：丘遲，字希範，吳興人。八歲能屬文，及長，辟徐州從事。高祖踐祚，拜中書郎，遷司徒</font>),
              (88, <font size="-2">從事中郎。卒。集題曰：兼中書侍郎丘遲上。</font>),
              (239, ''),
              (490, '')], ...
              numbers stands for the index in flat arrays.
              author_bag is a template that allow you to use for further applications such as extrac metadata, but it is not working well for every books. 
        ### IS THIS SPECIFIC TO WEN XUAN 文選?
        ### Yeah... it seems to be sepecific to wenshuan.        
    
    Args: 
        bookname (string): the name of the book, default = ''
        date (string): the date you collected the book, default = None
        creator (string): the name of the creator who created the instance
        ### DOES "CREATOR" MEAN THE PERSON RUNNING THE PROGRAM?
        description (string): optional description for the instance
        
    Methods:
        fetch_data(URL): fetch book bs4 obj from a start page URL of a Book in Han-Ji
        extract_paths(): extract paths from bookmark in self.flat_bodies list and append paths to self.paths
        get_author_bag(): extract paths from bookmark in self.flat_bodies list and append paths to self.paths
        ### SAME DESCRIPTION FOR "get_author_bag" AND  “extract_paths" 
        write_htmls(path): write data into htmls on the disk in path
        load_htmls(path): load data from htmls on the disk in path
        ### THESE TWO ARE ALSO A LITTLE UNCLEAR TO ME...
    """
    
    def __init__(self, bookname='', date=None, creator=None, description=''):
        self.flat_bodies   = []
        self.flat_passages = []
        self.flat_heads    = []
        self.flat_meta     = []
        self.paths = []
        self.author_bag = defaultdict(list)
        self.bookname    = bookname
        self.date        = date
        self.creator     = creator
        self.description = description
        ### ?
        
    def __getitem__(self, index):
        '''
        Args:
            index (int): Index
            
        Returns:
            bs4 html object in the flat_bodies
        '''
        return self.flat_bodies[index]
    
    def __len__(self):
        return len(self.flat_bodies)
    
    def __repr__(self):
        fmt_str = "Dataset {} ".format(self.bookname)
        fmt_str += "created by {} at {}.\n".format(self.creator, self.date)
        fmt_str += "{} data points. ".format(self.__len__()) 
        if len(self.author_bag) > 2:
            fmt_str += "\n{} authors and commentars.\n".format(len(self.author_bag))
        fmt_str += self.description
        return fmt_str

    def _pretty_html(self, soup):
        """cut off irrelevant content from the Han-Ji HTML source page"""
        head = soup.find("head")
        span_id_fontstyle = str(soup.find("span", {"id": "fontstyle"}))
        path  = str(soup.find('a', attrs={'class', 'gobookmark'}))
        HTML_string = """<html>
                {}
            <body>
                {}
            </body>
        </html>
        """.format(str(head), "{}\n\t{}".format(path, span_id_fontstyle))
        return HTML_string
    
    def fetch_data(self, URL, pages_limit=1000, print_bookmark=False, html_cutoff=False,
                   BASE_URL='http://hanchi.ihp.sinica.edu.tw/ihpc/'):
        '''fetch book bs4 obj from a start page URL of a Book in Han-Ji
        
        Args:
            URL (string): the start page url from han-ji website
            page_limit (int): the limit of next pages you can scrape. default = 1000
            ### IS THIS DEFAULT TOO LOW?
            print_bookmark (bool): print the bookmark while fetching the data. default = False
        '''
        for i in range(pages_limit):            
            # use urllib.request to get the html content of the website
            req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
            page = request.urlopen(req)
            soup = BeautifulSoup(page, 'lxml')

            # show information on the screen
            if print_bookmark == True:
                print("[Info] Start fetching {}. {}/{} epoch.".format(
                    soup.find('a', attrs={'class', 'gobookmark'}).text, i + 1, pages_limit))            
            else:
                print("[Info] Start fetching {}. {}/{} epoch.".format(URL, i + 1, pages_limit))            
            
            # check if the content is the same as previous page
            ### ? -> Response: this line is an ad-hoc solution for dealing with the first page while scraping. There must be a better way to do it.
            if i > 0:
                buffer = self.flat_bodies[-1].find_all('div', attrs={'style': True})
            else:
                # use a dummy list for the buffer for the first page
                buffer = ['dummy']
            
            # if the first and last elements in the buffer are the same as current page
            # delete page and save the current page.
            ### GOOD SOLUTION, BUT ARE WE SURE THERE ARE NO HIDDEN TRAPS IN USING THIS RULE?  COULD TWO CONSECUTIVE BUT DIFFERENT POEMS HAVE THE SAME START AND END WORD?
            ### Response: the comparison here is for end and start sentences of a poem. 
            ### It's quite unlikely two poems have the same start and end senetences, right?
            if (buffer[-1] == 
                soup.find_all('div', attrs={'style': True})[-1]) and (
                buffer[0] == 
                soup.find_all('div', attrs={'style': True})[0]):
                print("[Warning] This page is the same as the previous one, discard previous one and store the new one.")
                if html_cutoff == True:
                    self.flat_bodies[-1] = BeautifulSoup( self._pretty_html(soup), 'lxml' )
                else:    
                    self.flat_bodies[-1] = soup
            else:
                # append to flat bodies
                if html_cutoff==True:
                    self.flat_bodies.append( BeautifulSoup( self._pretty_html(soup), 'lxml'))
                else:
                    self.flat_bodies.append(soup)
               
            
            # find the next page
            next_page = soup.find('img', {'src' : '/ihp/snext.gif'})
            if next_page != None:
                url = next_page.find_parent()['href']
            else:
                print('[Info] No further next page. Stop fetching.')
                break
                
            URL = urllib.parse.urljoin(BASE_URL, url)
            time.sleep(random.randint(1, 3))
            ### GIVE IT 5 SECS, TO LOOK MORE HUMAN? ### Maybe I can set it to an argument of this function
            
    def extract_paths(self):
        '''extract paths from bookmark in self.flat_bodies list and append paths to self.paths'''
        self.paths = []
        
        for soup in self.flat_bodies:
            # extract "gobookmark" class
            path  = soup.find('a', attrs={'class', 'gobookmark'}).text
            self.paths.append(path)
    
    def _sum_indent_and_padding(self, texts):
        '''returns the sum of indents and paddings in the texts.'''
        return [
            sum([int(num[0]), int(num[1])])
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]        
                                        
    def write_htmls(self, path='data/', html_cutoff=False):
        try:
            os.makedirs(path)
        except OSError:
            pass
            
        for i,soup in enumerate(self.flat_bodies):
            filename = os.path.join(path, '{}_{}.html'.format(
                self.bookname, str(i).zfill(4)))
            with open(filename, 'w', encoding='utf-8') as file:
                if html_cutoff==True:
                    file.write( self._pretty_html(soup) )
                else:
                    file.write(str(soup))
                
        # update the description
        self.description += 'Writing data to {}.\n'.format(os.path.join(path, self.bookname + '*'))
        
    def load_htmls(self, path='data/'):
        self.flat_bodies = []
        i = 0
        while 1:
            filename = os.path.join(path, '{}_{}.html'.format(
                self.bookname, str(i).zfill(4)))
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    self.flat_bodies.append(BeautifulSoup(file.read(), 'lxml'))
            else:
                print("[Info] Stop at loading {}.".format(filename))
                break
            i += 1
        print("[Info] Total length of the data is {}.".format(len(self.flat_bodies)))
        
        # update the description
        self.description += 'Loading data from {}.\n'.format(path.format(os.path.join(path, self.bookname + '*')))
