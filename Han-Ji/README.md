# Han-Ji (漢籍) Scraper
This Scraper was designed for special purpose, so the output format is `.csv`
and we separated the passages iteself (本文) and the comments (註) into different columns.

The general usage of this script: just typing the following command in the terminal
```bash
python Scraping.py --URL=hanji?@72^74245715^802^^^60407005000900010001@@355855896
```
The `--URL` flag takes the last part of url address of the text page of Han-Ji (漢籍), 
but it is fine if you feed in the whole url like `--URL=http://hanchi.ihp.sinica.edu.tw/ihpc/hanji?@72^74245715^802^^^60407005000900010001@@355855896`.

----
## Details of the Output Format
- Passage (本文): file name is `(#)_Passage_(Name of the Passage).csv`.

| Column Name | passage (本文) | comment (註) |
| ---- | ----    | ----    |
| Criteria    | _ | `<font size=?></font>`, font tags with a size attribute |

- Head (標題): file name is `(#)_Head_(Name of the Passage).csv`.

| Column Name | passage (標題) | comment (註) | author (作者) |
| ---- | ----    | ----    | ---- |
| Criteria    | `<h3></h3>`, `h3` tag | `<font size=?></font>`, font tags with a size attribute | `<div align=?></div>`, `div` tag with a align attribute |


Note: not everytime the author column would captch author's name. Anything with `align` attribute would appear in this column.
---

# Writing to XML Files
If anyone want to write the `.csv` files into XML format, I provided a script to do this job: 

```bash
python HanJi_csv2xml.py --filename_passage 1_Passage_西都賦\(P.5\).csv
```

after `--filename_passage` flag is the `.csv` file you want to convert. Please note that you only have to provide `(#)_Passage_(Name of the Passage).csv` files for the flag, and the script would automatically read the head files. 

The choice of XML format is like this:
```html
<lg type="poem">
  <author></author>
  <head>
    <l>西都賦 </l>
  </head>
  <l>有西都賓問於東都主人曰：「蓋聞皇漢之初經營也，嘗有意乎都河洛矣。輟而弗康，寔用西遷，作我上都。主人聞其故而覩其制乎？」<comment>孝經鈎命決曰：道機合者稱皇。尚書曰：厥既得吉卜，乃經營。東都有河南洛陽，故曰河洛也。鄭玄論語注曰：輟，止也，張衛切。孔安國尚書傳曰：康，安也。穀梁傳曰：葬我君桓公。我君，接上下也。</comment></l>
  <l>主人曰：「未也。願賓攄懷舊之蓄念，發思古之幽情。博我以皇道，弘我以漢京。」<comment>廣雅曰：攄，舒也。孔安國尚書傳曰：蓄，積也。論語，顏淵曰：夫子博我以文。</comment></l>
  <l>賓曰：「唯唯。<comment>禮記曰：父召，無諾，唯而起。</comment></l>
...
...
</lg>
```

Please feel free to modify the script to change the XML tags and fit your own study purpose.