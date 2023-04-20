# AIAA-schedule-generator
Generates an offline pdf of the AIAA schedule for the technical sessions of the conferences (was made to work for AIAA Scitech 2023 but handles Aviation 2023 also).
The first time running the code will be slow as it will download each webpage's html code to obtain information.
This data will be saved locally such that if the code stops halfway through, it will not have to redownload the previous data to generate the schedule.
It also helps debugging the code as it otherwise runs relatively quickly once the data is locally available.
The pdf can be generated with or without QR codes, which saves space. 
The link used to generate the QR codes is also embedded in the image so you can click on the code and it will open the page.
A color scheme option allows for a fancy look, but also saving ink if you plan on printing certain pages.



Bugs:
- We are not loading/writing all the TS... (i.e. missing Forums and whatever)
- 'underfull' when compiling Latex
- total page number broken again

Additions:
- Time converter so we have 24 hrs format but also the start+end time of TP
- Bibtex format of all papers. That way, we generate a large Bibtex of all papers, 
  and we just cite them in the Latex with a custom format that looks good ?
- Table of contents for pages of each day maybe also a hardcoded page for the morning vs afternoon

Ideas:
- Look into Scrapy or PyQuery

