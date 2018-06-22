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
import pandas as pd

class WenShuan(Book):
    """WenShuan Dataset
    
    Attributes:
        head_bag (dict): A dictionary store all heads in the WenShuan as keys and comments as values.
    
    Args: same as Book class
    
    Methods:
        extract_meta(): Extract meta data from self.paths. Index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title. The method would check the author name using author_bag automatically.
        passages2tuples(): Call _passages2TextCommentPairs to transform self.flat_bodies, to text comment pairs and store in self.flat_passages
        heads2tuples(): Convert heads in <h3> tags to (header, [comment, commnent, ...]) pairs.
        extract_commentators(): Insert commentators into metadata from author_bag
    
    """
    
    def __init__(self, date, creator, description=''):
        Book.__init__(self, 'wenshuan', date, creator, description)
        self.sound_glosses_bag = []
        
    def _path_author_name_yield(self, fifth_path_item):
        '''yield the author name in the path via checking if it is in the author_bag'''
        # get the min and max length of author_bag
        author_bag_len = [len(key) for key in self.author_bag.keys()]
        for i in range(min(author_bag_len), max(author_bag_len) + 1):
            if fifth_path_item[:i] in self.author_bag:
                yield (i, fifth_path_item[:i])

    def extract_meta(self):
        '''Extract meta data from self.paths.
        Note: index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title.
        '''
        for path in self.paths:            
            # initialize the meta data
            meta = defaultdict(str)
            path_split = path.split('／')

            # check if the length of the path is longer than 5
            if len(path_split) >= 5:
                scroll = path_split[3].split()[0]
                poem   = path_split[3].split()[1]
                category = path_split[4]
                try:
                    idx, author = next(iter(self._path_author_name_yield(path_split[5])))
                except StopIteration:
                    print('[Warning] No author name in the path, {}.'.format(path))
                    author = ''
                    idx = 0

                # grab the title, which is the text behind the author name    
                title = '/'.join([x if i > 0 else x[idx:] for i,x in enumerate(path_split[5:])])

            else:
                author   = ''
                category = ''
                poem     = ''
                scroll   = ''
                title    = path_split[3]
                print('[Warning] Path is too short, {}. Only use title for metadata.'.format(path))
                

            # add values for keys
            meta['scroll'] = scroll
            meta['category']   = poem
            meta['genre'] = category
            meta['author'] = author
            meta['title']  = title
            self.flat_meta.append(meta)       
        
        # update description
        self.description += "Grabbed meta data with {} unique author names from paths.\n".format(len(set(meta['author'] for meta in self.flat_meta)))


    def passages2tuples(self, indent=4):
        '''Call _passages2TextCommentPairs to transform self.flat_bodies, 
        to text comment pairs and store in self.flat_passages'''
        self.flat_passages = []
        
        for body in self.flat_bodies:
            texts  = body.find_all('div', attrs={'style': True})

            # get the indent of the text
            sum_indent_padding = self._sum_indent_and_padding(texts)

            # setting threshold: sum_indent_padding > indent for authors
            texts = [texts[i] for i,s in enumerate(sum_indent_padding) if s <= indent]
            
            tcpairs = self._passages2TextCommentPairs(texts)
            self.flat_passages.append(tcpairs)
            
        # update description
        mean_num_pairs = sum(
            [len(tcpairs) for tcpairs in self.flat_passages]
        ) / len(self.flat_passages)
        self.description += "Got text comment pairs for WenShuan with mean of the pairs for each passage is {}.\n".format(mean_num_pairs)

    def _passages2TextCommentPairs(self, texts, comment_attr='size'):
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
            or (comment_attr in x.attrs
            if isinstance(x, bs4.element.Tag) else False), 
            text)

        # the list to append (passage, comment) tuples
        tcpairs = []

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
                tcpairs.append((''.join(buffer_text), ''.join(buffer_tag)))

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
            tcpairs.append((''.join(buffer_text), ''.join(buffer_tag)))

        return tcpairs

    def heads2tuples(self):
        '''Convert heads in <h3> tags to (header, [comment, commnent, ...]) pairs.'''
        self.flat_heads = []
        self.head_bag   = defaultdict(list)

        for body in self.flat_bodies:
            # extract heads <h3>
            heads = body.find_all('h3')
            
            flat_head = []
            for head in heads:
                # exclude the blank string in the head
                pair = [h for h in head if h != ' ']

                # assume the first element of <h3> is the header
                header_name, comments = pair[0], pair[1:]

                # preserve the comments into a shared dict in the class.
                # Plan to match the comments here with self.flat_meta 
                self.head_bag[header_name.replace('\u3000', '').replace('文選', '')] = comments
                
                # append a pair of text and comment 
                flat_head.append((header_name, comments))
                
            # append header with the following content
            self.flat_heads.append(flat_head)

        # update desciption
        mean_len_comment = sum([len(c) for head in self.flat_heads for _,c in head]) / len(self.flat_heads)
        self.description += "Grabbed tuple pairs from heads, the mean number of elements follow by the header is {}.".format(mean_len_comment)  
        
    def extract_commentators(self):
        '''Insert commentators into metadata from author_bag'''
        for author,comment_list in self.author_bag.items():
            if '注' in author:
                for comment in comment_list:
                    index, _ = comment
                    self.flat_meta[index]["commentator"] = author

    def _punctuation_count(self, phrase, pun_bag = {"、","。", "，", "？", "：", "；", "「", "」"}):
        '''Count num punctuactions in phrase based on a given pun_bag'''
        return sum(phrase.count(p) for p in pun_bag)

    def _backward_char_search(self, phrase, exclude = {" ", "、","。", "，", "？", "：", "；", "「", "」"}):
        '''Return the frist char which is not in exclude.'''
        for char in phrase[::-1]:
            if char not in exclude:
                return char
            else: continue       

    """
    Figure out a way to do in Bayesian way, to give a prob of sound glosses correctness
    """                
    def _sound_glosses_check(self, text, comment):
        '''Check the comment is a sound glosses or not.
        If it is a sound glosses, return (character reffered to, sound) as a tuple.'''
        if  (self._punctuation_count(comment) < 2 and 
            len(re.sub(r"[、。，？：；「」]", "", comment.replace(" ", ""))) < 4 and 
            comment != ""):
            return self._backward_char_search(text), re.sub(r"[、。，？：；「」]", "", comment)
            
        elif (self._punctuation_count(comment.split("。")[0]) == 0 and 
            0 < len(comment.split("。")[0]) < 4):
            return self._backward_char_search(text), comment.split("。")[0]
        
        else: return None
        
    def extract_sound_glosses(self, remove_sound_glosses=True):
        self.sound_glosses_bag = []
        new_flat_passages  = []

        for i,passage in enumerate(self.flat_passages):
            # A place to save sound glosses    
            new_passage = []
            p_preivous_buffer = ''

            for j,(p,c) in enumerate(passage):
                # check if c is a single phrase comment
                sound_gloss = self._sound_glosses_check(p, c)

                if sound_gloss != None:
                    self.sound_glosses_bag.append((i,) + sound_gloss)
                    p_preivous_buffer += p

                    # CASE 2: Inline Sound Glosses
                    if len(c) >= 5:
                        if p_preivous_buffer[-1] != "。":
                            p_preivous_buffer += "。"

                    # CASE 1: Single Phrase
                    elif re.search(r"(.+)([、。，？：；「」])", c) != None:
                        match = re.search(r"(.+)([、。，？：；「」])", c)
                        p_preivous_buffer += match.group(2)

                else:
                    new_passage.append((p_preivous_buffer + p, c))
                    p_preivous_buffer = ''

            new_flat_passages.append(new_passage)

        if remove_sound_glosses:
            self.flat_passages = new_flat_passages

    def _writeECSV(self, filename, meta, df):
        '''write a pandas.DataFrame into csv file with comments contain'''
        with open(filename, 'w', encoding='utf-8') as file:
            for key, value in meta.items():
                file.write('# {} = {}\n'.format(key, value))
            df.to_csv(file)

    def write_passages_ECSV(self, path="文選/"):
        '''writing passages into extend CSV format on the disk'''
        try:
            os.makedirs(path)
        except OSError:
            pass
        
        for i, (passage, meta) in enumerate( zip( self.flat_passages, self.flat_meta ) ):
            # define the filename based on scroll and title
            filename = os.path.join( path, '{}_Passage_{}_{}.csv'.format(i, meta['scroll'], meta['title'].replace('/', '-') ) )
            
            # write the csv files
            self._writeECSV(filename, meta, pd.DataFrame( passage, columns=["passage_text", "passage_comment"]))        