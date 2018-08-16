# Rare Char Hack in Python

> **NOTE: 我發現用缺字查詢應該不是 JS API 真正在抓構字時用的方法！應該要用正規化查詢😁 只是我很懶，這禮拜暫時不想去爬正規劃查詢。改天再來改一下。**

Academia Sinca provide a search engine for rare characters. The link to the website is :point_right: http://char.iis.sinica.edu.tw/

They also provided a `JavaScript` API for web page to embed and fillup the rare char based on **the structure of the fragments (構字形)**.

For example, we input 山山山, the result would return something like the combination of 山山山。
![](https://i.imgur.com/IEtCgp2.png)

The best way to hack this thing in Python is to use JavaScript API and get the Uicode of the rare char. However, the Javascript somehow only capture the **image of the rare char** and the **combination of the fragments (構字形)**

For example, ![](https://i.imgur.com/Q6LeLon.png)
`alt` :point_right: 構字形
`src` :point_right: image

## Simple Hack Using `urllib`
```python=
import re
import urllib
from urllib import request
from bs4 import BeautifulSoup

def char_sinica_search(key, url = 'http://char.iis.sinica.edu.tw/Search/'):
    # search in http://char.iis.sinica.edu.tw/Search/ simply is adding '?SearchValue=' + XXX
    headers = {'User-Agent': 'Mozilla/5.0'}
    URL = urllib.parse.urljoin(url, '?SearchValue=' + urllib.parse.quote(key) )

    # standard way to parse the website
    req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    page = request.urlopen(req)
    try:
        soup = BeautifulSoup(page, 'lxml')
    except Exception as e:
        soup = BeautifulSoup(req.text, 'html5lib')

    # get the link to go to the web of the image
    chars = soup.find_all('a', {'target' : "char"})
    if len(chars) != 1:
        print('[Warning] Multiple mathcings. Please change to a specific input.')
        
    for char in chars:
        
        # standard way to parse again
        URL  = urllib.parse.urljoin( url, char['href'] )
        req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        page = request.urlopen(req)
        soup = BeautifulSoup(page, 'lxml')

        # this time we want the unicode
        try:
            _blank = soup.find_all('a', text=re.compile(r' 前往查看 '), attrs={'target':'_blank'})[0]
            UNICODE = _blank['href'].split('/')[-1]

            # and we want the rare_char
            onclick = soup.find_all('input', {'value': '複製Unicode字元', 'type':'button', 'onclick':True})[0]
            rare_char = re.findall(r"addClipboard\('(.)'\)",onclick['onclick'])[0]
            yield UNICODE, rare_char
        except IndexError as e:
            print('[Warning] 查無資料！', e)
            yield None
```

This is a generator which could get the results of sinica rare char search. You can loop over it if you want to get multiple outputs:
```python
for char in char_sinica_search("山山山"):
    print(char)
[Warning] Multiple mathcings. Please change to a specific input.
# ('U+21DC8', '\uf6f8')
# ('U+213A8', '\uecb5')
# ('U+21EE6', '\uf83f')
# ('U+22275', '\ue36f')
# ('U+24E22', '\ue809')
# ('U+242EB', '\uef9d')
# ('U+26776', '\ueb95')
# ('U+26784', '\ueb96')
# ('U+232CE', '\uf752')
# ('U+21999', '\ue743')
# ('U+239A3', '\uf479')
# [Warning] 查無資料！ list index out of range  
```
If there is no unicode for the result char, it would warn that 查無資料. 

Otherwise, if you only want the top result (first search):
```python
next(iter(char_sinica_search("山山山")))
# ('U+21DC8', '\uf6f8')
```

## Combine JavaScript API and `char_sinica_search` hack

To use JavaScript API, copy-paste these lines into the bottom of your text file (say, `test.html`)
```html
<script language="javascript">
window.history.forward(1);
</script>
<script src="http://char.iis.sinica.edu.tw/API/ics.js" language="javascript"></script>
<script language="JavaScript">
processPage("red","24", "DFKai-sb");
</script>
```

Use `selenium` to allow JavaScript to run:
```python 
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome(executable_path='(PATH TO CHROME DRIVER)/chromedriver')
driver.get("file://" + "/(PATH TO YOUR DIRECTORY)/test.html")
page = driver.page_source # get source page

driver.close()
```

This line give you all combinataions of fragments (構字形) in the `test.html`:
```python
[char["alt"] for char in soup.find_all("img")]
# ['\uf06f',
# '桼\uf6a4\uf4dd',
# '山\uf6a4卬',
# '桼\uf6a4\uf4dd',
# '\uf5fe\uf6a3石',
# '巾\uf6a4軍']
```

And, convert fragments into rare char via feeding them into `char_sinica_search`:
```python
[next(iter(char_sinica_search(char["alt"]))) for char in soup.find_all("img")]
# [('U+3B25', '㬥'),
#  ('U+48DB', '䣛'),
#  ('U+21D59', '\uf6b0'),
#  ('U+48DB', '䣛'),
#  ('U+40AE', '䂮'),
#  ('U+3853', '㡓')]
```
![](https://i.imgur.com/SVaRssl.png)

Exactly what we expect.