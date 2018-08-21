from collections import defaultdict, Counter
from datetime import datetime
from bs4 import BeautifulSoup
import bs4
from urllib import request
import urllib
import time
import random
import re
import os, sys
import glob
import logging
import pandas as pd
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import HtmlLexer

# logging information
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Book:
    """Han-Ji '<http://hanchi.ihp.sinica.edu.tw/ihp/hanji.htm>'_ Dataset.
    
    Attributes:
        flat_bodies (list): a list containing all htmls 
        flat_passages (list): a list containing the text of all passages (i.e., every individual piece in a book). Users should define their own methods to organize the passages.
        flat_heads (list): a list containing all the text of the heads (i.e., the metadata at the top of each individual piece, like title and author). Users should define their own methods to organize the heads.
        flat_meta (list): a list containing all metadata (dictionary) extracted from bookmarks. User should define their own methods to extract metadata.
        paths (list): a list of paths extracted from the "bookmark" provided in the database. e.g., 集／總集／文選／卷第二十七　詩戊之一／樂府上／古樂府三首／飲馬長城窟行(P.1277)
    
    Args: 
        bookname (string): the name of the book, default = ''
        date (string): the date you collected the book, default = None
        creator (string): the name of the creator who created the instance
        
    Methods:
        fetch_data(URL): fetch book bs4 obj from a start page URL of a Book in Han-Ji
        extract_paths(): extract paths from bookmark in self.flat_bodies list and append paths to self.paths
        write_htmls(path): write data into htmls on the disk in path
        load_htmls(path): load data from htmls on the disk in path
        char_word_counts(char, limits=(1,4)): count the number of occurances of the phrase attach with a certain character
        extract_rare_chars(driver_path, normalization=True): extract rare char in every passages. Note that this function would run for a long time.
        write_rare_chars(): writing self.flat_rare_chars to `{bookname}_rare_char.json`
        update_rare_chars(): replace rare char based on `{bookname}_rare_char.json`
    """
    
    def __init__(self, bookname='', date=None, creator=None):
        self.flat_bodies   = []
        self.flat_passages = []
        self.flat_heads    = []
        self.flat_meta     = []
        self.paths = []
        self.author_bag = defaultdict(list)
        self.bookname    = bookname
        try:
            self.date        = datetime.strptime(date, '%Y-%m-%d')
        except (TypeError,AttributeError,ValueError) as e:
            logging.warning("No datetime input provided!")
            self.date = ""
        self.creator     = creator
        self.description_dataframe = self._description_dataframe()
        
    def _highlight(self, html_code):
        from IPython.display import HTML
        formatter = HtmlFormatter(linenos=False, cssclass="source")
        html_highlight = highlight(html_code, HtmlLexer(), formatter)
        css_style = formatter.get_style_defs()

        html_template = """<style>
        {}
        </style>
        {}
        """.format(css_style, html_highlight)

        return HTML(html_template)

    def __getitem__(self, index):
        '''
        Args:
            index (int): Index
            
        Returns:
            bs4 html object in the flat_bodies
        '''
        
        return self._highlight(
            self._pretty_html(
                self.flat_bodies[index]
                )
            )
    
    def __len__(self):
        return len(self.flat_bodies)
    
    def _description_dataframe(self):
        types = ["meta", "path", "passages",]
        variables = ["flat_meta", "paths", "flat_passages",]
        methods = ["self.extract_meta", "self.extract_paths", "self.extract_passages"]
        current_lengths = [len(self.flat_meta), len(self.paths), len(self.flat_passages)]
        df = pd.DataFrame([types, variables, methods, current_lengths]).T 
        df.columns = ['type', 'variable', 'method', 'current_length']
        return df

    def __repr__(self):
        self.description_dataframe = self._description_dataframe()
        description = self.description_dataframe.to_string()
        return description

    def pretty_print(self, index):
        """pretty print the html source page in a Jupyter notebook cell output"""
        from IPython.display import HTML
        return HTML(self._pretty_html( self.flat_bodies[index] ))

    def _pretty_html(self, soup):
        """cut off irrelevant content, such as side columns in the webpage, from the Han-Ji HTML source page. 
        This procedure aims to save memory for the computer."""
        span_id_fontstyle = str(soup.find("span", {"id": "fontstyle"}))
        path  = str(soup.find('a', attrs={'class', 'gobookmark'}))
        HTML_string = """<html>
            <body>
                {}
            </body>
        </html>
        """.format("{}\n\t{}".format(path, span_id_fontstyle))
        return HTML_string
    
    def fetch_data(self, URL, pages_limit=10000, print_bookmark=False, html_cutoff=False,
                   BASE_URL='http://hanchi.ihp.sinica.edu.tw/ihpc/', sleep_range=(1, 3)):
        '''fetch book bs4 obj from a start page URL of a Book in Han-Ji
        
        Args:
            URL (string): the start page url from han-ji website
            page_limit (int): the limit of next pages you can scrape. default = 10000
            print_bookmark (bool): print the bookmark while fetching the data. default = False
            html_cutoff (bool): cut off the irrelavant side column and tags in Han-Ji raw html files, 
                                to save memory usage.
        '''
        for i in range(pages_limit):            
            # use urllib.request to get the html content of the website
            req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
            page = request.urlopen(req)
            soup = BeautifulSoup(page, 'lxml')

            # show information on the screen
            if print_bookmark == True:
                logging.info("Start fetching {}. {}/{} epoch.".format(
                    soup.find('a', attrs={'class', 'gobookmark'}).text, i + 1, pages_limit))            
            else:
                logging.info("Start fetching {}. {}/{} epoch.".format(URL, i + 1, pages_limit))            
            
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
                logging.warning("This page is the same as the previous one, discard previous one and store the new one.")
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
                logging.info('No further next page. Stop fetching.')
                break
                
            URL = urllib.parse.urljoin(BASE_URL, url)
            time.sleep(random.randint(sleep_range[0], sleep_range[1]))
            
    def extract_all(self):
        '''do all extractions at one time'''
        pass

    def extract_paths(self):
        '''extract paths from bookmark in self.flat_bodies list and append paths to self.paths'''
        self.paths = []
        
        for soup in self.flat_bodies:
            # extract "gobookmark" class
            path  = soup.find('a', attrs={'class', 'gobookmark'}).text
            self.paths.append(path)
    
    def extract_meta(self):
        '''extract meta data from self.paths.'''
        pass

    def extract_passages(self):
        '''extract passages from the Book. Users should defined their own methods to organize the Book.'''
        pass 

    def _sum_indent_and_padding(self, texts):
        '''returns the sum of indents and paddings in the texts.'''
        return [
            sum([int(num[0]), int(num[1])])
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]        

    def _indent_and_padding(self, texts):
        '''Return the indent and padding tuples of indents and paddings in the texts.'''
        return [
            (int(num[0]), int(num[1]))
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]                    

    def extract_rare_chars(self, driver_path, normalization=True):
        """Extract rare char in every passages. Note that this function would run for a long time.
        
        Args: 
            driver_path (str) : the path to your selenium driver
            normalization (bool) : whether or not using normalization API in academia sinica, default = True.
        
        Updated:
            self.flat_rare_bag (list) : {"(components of rare chars)" : ("(UNICODE)", "(UTF-8)"), ...}
        
        After running this funciton, run 
        >> self.write_rare_chars() 
        to write a json.
        
        Therefore, you could just run 
        >> self.update_rare_char()
        to update rare char in the next time without extracting rare char from web again.
        """
        from rare_char_converter import rare_char_converter
        
        self.flat_rare_chars = []
        for body in self.flat_bodies:
            while 1:
                try: 
                    time.sleep(random.randint(2, 5))
                    text = body.find("span", {"id":"fontstyle"}).text
                    rare_char_bag = rare_char_converter(text, driver_path, normalization=True)
                    self.flat_rare_chars.append(rare_char_bag)
                    break
                except (TimeoutError, ConnectionResetError, urllib.error.URLError) as e:
                    logging.warning("{}, wait for 10 secs.".format(e))
                    time.sleep(10)    

    def write_rare_chars(self):
        import json
        with open("{}_rare_char.json".format(self.bookname), "w", encoding="utf-8") as file:
            json.dump(self.flat_rare_chars, file)


    def update_rare_chars(self):
        """Replace rare char based on `{bookname}_rare_char.json`"""
        import json

        try:
            with open("{}_rare_char.json".format(self.bookname), "r", encoding="utf-8") as file:
                self.flat_rare_chars = json.load(file)

            flat_htmls = []
            for soup,rare_char in zip(self.flat_bodies, self.flat_rare_chars):
                html = str(soup)
                for components,(UICODE, char) in rare_char.items(): 
                    html = re.sub(components, char, html)
                flat_htmls.append(BeautifulSoup(html, "lxml"))

            self.flat_bodies = flat_htmls        

        except FileNotFoundError as e:
            logging.error("""[Error] {}_rare_char.json does not exist

            try to run these lines: 
            \t>> self.extract_rare_chars()
            \t>> self.write_rare_chars()\n""".format(self.bookname))

    def _regexf(self, char, num):
        return r"[^、。，？！：；「」〔〕『』]{" + str(num) + "}" + char

    def passage_generator(self):
        '''iterate over every passage regardless the hierarchical structure'''
        for passages in self.flat_passages:
            for p in passages:
                yield p

    def char_word_counts(self, char, limits=(1, 4)):
        '''
        Count the number of occurances of the phrase attach with a certain character
        
        Args:
            char (str): the character you want to set as the last character in the phrase.
            limits (tuple): lower and upper limit for the characters before the `char`.

        Yield:
            collections.Counter object
        '''
        return Counter(list(self._word_generator(char, limits)))

    def _word_generator(self, char, limits):
        lower, upper = limits
        for p in self.passage_generator():
            for i in range(lower, upper):
                for match in re.finditer(self._regexf(char, i), p):
                    yield match.group(0)

    def write_htmls(self, path='data/', html_cutoff=False):
        '''writing all htmls in flat_bodies to the folder data/

        Args:
            path (str) : the path to the folder you want to write htmls files
            html_cutoff (bool) : whether or not you want to cut off irrelevant contents in Han-Ji webpage 
        '''
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
                        
    def load_htmls(self, path='data/'):
        '''loading all files with filename = "bookname_*.html" in path data/
        '''
        self.flat_bodies = []
        i = 0
        while 1:
            filename = os.path.join(path, '{}_{}.html'.format(
                self.bookname, str(i).zfill(4)))
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    self.flat_bodies.append(BeautifulSoup(file.read(), 'lxml'))
            else:
                logging.info("Stop at loading {}.".format(filename))
                break
            i += 1
        logging.info("Total length of the data is {}.".format(len(self.flat_bodies)))