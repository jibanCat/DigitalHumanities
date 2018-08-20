# Han-Ji (漢籍) Fetcher

- The fetcher function is defined as a method in the `Book` class. You can fetch the html files using

```python
from Book import Book
# get a instance of Book class
book = Book(bookname="name", date="2018-05-29", creator="MF)

# get the htmls from the Han-Ji website, The UR
book.fetch_data('http://hanchi.ihp.sinica.edu.tw/ihpc/hanji?@30^1389784921^802^^^60311004001000010006@@460127924',
                pages_limit=1000, print_bookmark=False,)
```

- Now, `bs4` objects are stored in the `book.flat_bodies` list. You can write the html files into `data` folder via

```python
# writing htmls into a folder
book.write_htmls(path="data")

# loading files to book
book.load_htmls(path="data")
```

- Exctract the bookmark (the dependencies of the poems) out of the page, just typed

```python
book.extract_paths()
```

- To preview the first page of Han-Ji page in a pretty HTML format, type

```python
book.pretty_print(0) # 0 for the first page in fetched Han-Ji data
```

- To convert rare char components (構字形) in `book.flat_bodies` html sources, type

```python
# if the {name}_rare_char.json exist in your path
book.update_rare_chars()
```

otherwise

```python
# if the {name}_rare_char.json does not exist
driver_path = '(PATH to your selenium driver)'
book.extract_rare_chars(driver_path) # this line would take a very long time, be careful before you execute it
book.write_rare_chars() # write to name_rare_char.json
book.update_rare_chars()
```

- To count the occurances of the phrase attached with a certain character, use `book.char_word_counts`. See _`SongShu` Organizer_ for futher details.  

```python
# list the 5 most common words with the last character == `char`,  
# consider phrase with length 2 to 6.
# char should be a string
book.char_word_counts(char, limits=(1, 5)).most_common(5)
```

Note: before using `char_word_counts` method, make sure you already extraced passages to `book.flat_passages`.

## WenXuan (文選) Organizer

- The `WenXuan.py` was designed as a wrapper of the `Book.py` and have specific methods to organize the texts files in WenXuan

```python
from WenXuan import WenXuan
# get a instance out of WenXuan class
wenxuan = WenXuan('2018-05-29', 'MF')
wenxuan.fetch_data(URL="(URL for Han-Ji WenXuan)",
                pages_limit=1000, print_bookmark=True,)

# organize the text files
wenxuan.extract_all()
```

- Writing to CSV: `WenXuan.py` provides a method to write `wenxuan.flat_passages` and `wenxuan.flat_meta` to a series of CSV files in folder (default folder is `"/文選"`). Metadata is listed in the comments (`#`) in the headers.

```python
wenxuan.write_passages_ECSV()
```

- To count the occurances of the phrase attached with a certain character, e.g., '曰':

```python
wenxuan.char_word_counts('曰', limits=(1, 4)).most_common(5)
# [('子曰', 3517), ('書曰', 3495), ('詩曰', 2843), ('善曰', 2029), ('注曰', 2018)]
```

## SongShu (宋書) Organizer

- The `SongShu.py` was also designed as a wrapper of `Book.py` class. SongShu organizer separated every pieces of works into passages.

```python
from SongShu import SongShu
songshu = SongShu("2018-06-28", "MF")
songshu.fetch_data(URL="(The first page URL of SongShu in Han-Ji)", pages_limit=2000, print_bookmark=True)
songshu.write_htmls()
```

- To recover the fetched data we downloaded last time, run

```python
songshu = SongShu("2018-06-28", "MF")
songshu.load_htmls()
# [Info] Stop at loading data/ShongShu_0851.html.
# [Info] Total length of the data is 851.
```

- To extract metadata, bookmarks, and organize the passages:

```python
# preprocessing the songshu data to get metadata and bookmarks
# and separate the passages in every pages
songshu.extract_all()
```  

The <font color="#A60628">Warning</font> in the above output cell show that some pages in SongShu do not have a clear definition of **separating the passages**.

- To count the occurances of the phrase attached with a certain character, e.g., '洲':

```python
songshu.char_word_counts('洲', limits=(1, 5)).most_common(5)
# [('蔡洲', 14), ('鬱洲', 9), ('嶸洲', 6), ('崢嶸洲', 6), ('至蔡洲', 6)]
```

In this way, it is possible to extract natural geographical names.

## Rare Character Identifier

Some characters in Han-Ji are rare chars. In this case, if we use `urllib` to parse the source page, we only get the fragments of the rare chars (構字形). 

To resolve this situation, we can use JavaScript API in http://char.iis.sinica.edu.tw/API/normalization.htm to acquire the fragments of chars, and then we can use the fragments to search the correct rare char unicodes. 

The following lines show how to fetch the a bag of rare char unicodes from a text string:

```python
from rare_char_converter import rare_char_converter

selenium_driver = "(PATH TO YOUR SELENIUM DRIVER)"
text = "(YOUR HAN-JI TEXT)"
rare_char_converter(text, selenium_driver)
# Return: dict, {"(fragments of char)" : (UNICODE, string of the rare char)}
```