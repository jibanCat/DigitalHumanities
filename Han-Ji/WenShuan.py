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
            meta['poem']   = poem
            meta['category'] = category
            meta['author'] = author
            meta['title']  = title
            self.flat_meta.append(meta)       
        
        # update description
        self.description += "Grabbed meta data with {} unique author names from paths.\n".format(len(set(meta['author'] for meta in self.flat_meta)))


    def passages2tuples(self, indent=4):
        '''Call _passages2TextCommentPairs to transform self.flat_bodies, 
        to text comment pairs and store in self.flat_passages'''
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