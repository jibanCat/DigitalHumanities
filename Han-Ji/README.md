# Han-Ji (漢籍) Scraper
This Scraper was designed for special purpose, so the output format is `.csv`
and we separated the passages iteself (本文) and the comments (註) into different columns.

The general usage of this script: just typing the following command in the terminal
```bash
python Scraping --URL=hanji?@72^74245715^802^^^60407005000900010001@@355855896
```
The `--URL` flag takes the last part of url address of the text page of Han-Ji (漢籍), 
but it is fine if you feed in the whole url like `--URL=http://hanchi.ihp.sinica.edu.tw/ihpc/hanji?@72^74245715^802^^^60407005000900010001@@355855896`.

----
## Details of the Output Format
- Passage (本文): file name is `(#)_Passage_(Name of the Passage).csv`.

| Column Name | passage (本文, 段落) | comment (註, 本文段落之後的第一個註) |
| ---- | ----    | ----    |
| Criteria    | _ | `<font size=?></font>`, font tags with a size attribute |

- Head (標題): file name is `(#)_Head_(Name of the Passage).csv`.

| Column Name | passage (標題) | comment (註, 標題之後的第一個註) | author (作者，其實也有可能抓到的不是作者) |
| ---- | ----    | ----    | ---- |
| Criteria    | `<h3></h3>`, `h3` tag | `<font size=?></font>`, font tags with a size attribute | `<div align=?></div>`, `div` tag with a align attribute |
