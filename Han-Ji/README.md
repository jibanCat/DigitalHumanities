# Han-Ji (漢籍) Scraper

- The scraper function is defined as a method in the `Book` class. You can scrape the html files using

```python
# get a instance of Book class
book = Book(bookname="name", date="2018-05-29", creator="MF)

# get the htmls from the Han-Ji website
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
