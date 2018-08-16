import os
import re
import urllib
from urllib import request
from selenium import webdriver
from bs4 import BeautifulSoup

def char_sinica_search(key, url = 'http://char.iis.sinica.edu.tw/Search/'):
    # search in http://char.iis.sinica.edu.tw/Search/ simply is adding '?SearchValue=' + XXX
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

def normalization_sinica_search(key, url = "http://char.iis.sinica.edu.tw/API/"):
    # search in http://char.iis.sinica.edu.tw/API/ simply is adding 'normalization_SQL.aspx?str=' + XXX
    URL = urllib.parse.urljoin(url, 'normalization_SQL.aspx?str=' + urllib.parse.quote(key) )

    # standard way to parse the website
    req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    page = request.urlopen(req)

    try:
        soup = BeautifulSoup(page, 'lxml')
    except Exception as e:
        soup = BeautifulSoup(req.text, 'html5lib')

    UNICODE = soup.find("unicode").text
    try:
        return UNICODE, chr(int(UNICODE.lower(), 16))
    except ValueError as e:
        print("[Error] {}, no such search result for {}".format(e, key))

def rare_char_converter(text, driver_path, normalization=True):
    """
    Give a text, and return a list of rare chars that based on the tagging results of 
    char sinica search JS API.

    Args: 
        text : string, the text you want to find the fragments of rare chars (構字形)
        driver_path : string, the path to your selenium driver
    """
    # append JS_API to the bottom of the text file
    JS_API = """
    <script language="javascript">
    window.history.forward(1);
    </script>
    <script src="http://char.iis.sinica.edu.tw/API/ics.js" language="javascript"></script>
    <script language="JavaScript">
    processPage("red","24", "DFKai-sb");
    </script>
    """

    with open("temp.html", "w", encoding="utf-8") as file:
        file.write(text + JS_API)    

    # open the chrome driver
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.get("file://" + os.path.join(os.getcwd(), "temp.html"))

    # get the page source after running the JS API
    page = driver.page_source

    # close the diver
    driver.close()

    # remove the file
    os.remove("temp.html")

    # convert the page to bs4 object
    soup = BeautifulSoup(page, "lxml")

    # convert rare char to unicode
    if normalization == True:
        bag_of_rare_char_unicode = {
            char["alt"] : normalization_sinica_search(char['alt'])
            for char in soup.find_all("img")
        }
        bag_of_rare_char_unicode = {key: value for key,value in bag_of_rare_char_unicode.items()
                           if value != None}

    else:
        bag_of_rare_char_unicode = {
            char["alt"] : next(
                iter(char_sinica_search(char["alt"]))
            ) for char in soup.find_all("img")
        }

    return bag_of_rare_char_unicode