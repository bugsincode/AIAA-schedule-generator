# AIAA-schedule-generator
Generates an offline pdf of the AIAA schedule for the technical sessions of the conferences (was made to work for AIAA Scitech 2023).

Bugs:
- We are not loading/writing all the TS... (i.e. missing Forums and whatever)
- 'underfull' when compiling Latex

Additions:
- Time converter so we have 24 hrs format but also the start+end time of TP
- Bibtex format of all papers. That way, we generate a large Bibtex of all papers, 
  and we just cite them in the Latex with a custom format that looks good ?
- Table of contents for pages of each day maybe also a hardcoded page for the morning vs afternoon

Ideas:
- Look into Scrapy or PyQuery

