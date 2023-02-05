import AIAA_scrapper_vars as AIAA_vs

from pylatex import Document, Command
from pylatexenc.latexencode import unicode_to_latex
from pylatex.package import Package
from pylatex.utils import NoEscape
import os
import pickle
import qrcode
#import re
#import html2text
#from html.parser import HTMLParser


def find_all(a_str, sub):
    # Stolen from:
    # https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches


def escape_all(strin, escme):
    # Escape the commas
    i = list(find_all(strin,escme))
    if i:
        # This executes if the array is non-empty
        for j in reversed(i):
            # Reverse iterate so we don't change index positions
            strin = strin[:j] + '{' + escme +'}' + strin[j+1:]
    return strin


def latexproof(strin):
    # Stolen from:
    # https://stackoverflow.com/questions/25202007/python-translate-with-multiple-characters
    swapdict = {
        '&':'\&',
        '%':'\%',
        '$':'\$',
        '#':'\#',
        '_':'\_',
        '{':'\{',
        '}':'\}',
        '~':'\textasciitilde',
        '^':'\textasciicircum',
        '\\':'\\textbackslash'
        }
    
    # Could do unicode_to_latex() as well
    return ''.join([swapdict.get(x, x) for x in strin])

        
def genDoc():
    # Create the Latex document to contain the schedule
    doc = Document()
    
    # Add our packages
    doc.packages.append(Package('geometry'))                    
    doc.packages.append(Package('fancyhdr'))
    doc.packages.append(Package('xcolor'))
    doc.packages.append(Package('graphicx'))
    doc.packages.append(Package('multirow'))
    doc.packages.append(Package('tcolorbox','skins,breakable'))
    doc.packages.append(Package('placeins'))
    doc.packages.append(Package('etoolbox'))
    doc.packages.append(Package('hyperref'))
    
    # Set font
    doc.preamble.append(NoEscape('\\renewcommand{\\familydefault}'
                                 '{\sfdefault}'))
    
    # Set geometry
    doc.preamble.append(NoEscape('\geometry{letterpaper,'
        'left=0.3cm,right=0.3cm,headheight=0.5cm,top=0.2cm,bottom=0.2cm,'
        'foot=0cm,footskip=0cm,includeheadfoot=True}'))
     
    # Add image path
    doc.preamble.append(NoEscape('\graphicspath{{' + AIAA_vs.DL_folder + 
                                 'Images/}}'))
    
    # Add document header
    doc.preamble.append(NoEscape(
        '\\fancypagestyle{header}{\n'
        '\\fancyfoot{}\n'
        '\\renewcommand{\headrulewidth}{0pt}\n'
        '\\renewcommand{\\footrulewidth}{0pt}\n'
        '\\fancyhead[L]{AIAA Scitech 2023 | \leftmark \ | \\rightmark}\n'
        '\\fancyhead[R]{Page \\thepage\ of \pageref{LastPage}}}\n'))
    
    # Add to main document
    doc.append(NoEscape('\\thispagestyle{empty}\n\pagestyle{header}'))
    
    # Command for custom colors
    doc.preamble.append(NoEscape(
        '\definecolor{col1}{HTML}{'+AIAA_vs.colorscheme[0]+'} \n' 
        '\definecolor{col2}{HTML}{'+AIAA_vs.colorscheme[1]+'} \n'
        '\definecolor{col3}{HTML}{'+AIAA_vs.colorscheme[2]+'} \n'
        '\definecolor{col4}{HTML}{'+AIAA_vs.colorscheme[3]+'} \n' 
        '\definecolor{col5}{HTML}{'+AIAA_vs.colorscheme[4]+'} \n'
        '\definecolor{col6}{HTML}{'+AIAA_vs.colorscheme[5]+'} \n'))
    
    # Command to have custom section and subsections without numbering
    # but also have them in the header
    doc.preamble.append(NoEscape(
        '\\newcommand\mysection[1]{\section*{#1}'
        #'%\\addcontentsline{toc}{chapter}{\protect\\numberline{}#1} \n'
        '\def\leftmark{#1}}\n'
        '\\newcommand\mysubsection[1]{\subsection*{#1}'
        #'%\\addcontentsline{toc}{section}{\protect\\numberline{}#1} \n'
        '\def\\rightmark{#1}}\n'))
    
    # Command to format a Technical Paper
    if (AIAA_vs.noqrcodes):
        # No QR codes. TP number becomes the link
        doc.preamble.append(NoEscape(
            '\\newcommand{\TP}[4]{ \n'
            '\\begin{tcolorbox}[ \n'
            'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=0pt,boxrule=3pt, \n'
            'colback=col1,colframe=col2, \n'
            'fonttitle=\\bfseries,coltitle=white,title=\href{#4}{#1}, \n'
            'before skip=0pt,after skip=0pt,arc=0pt,outer arc=0pt] \n'
            '#2 \end{tcolorbox} } \n' ))
    else:
        doc.preamble.append(NoEscape(
            '\\newcommand{\TP}[4]{ \n'
            '\\begin{tcolorbox}[ \n'
            'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=0pt,boxrule=3pt, \n'
            'colback=col1,colframe=col2, \n'
            'fonttitle=\\bfseries,coltitle=white,title=#1, \n'
            'before skip=0pt,after skip=0pt,arc=0pt,outer arc=0pt] \n'
            '\\begin{minipage}{0.89\\textwidth} #2 \end{minipage} \hfill \n'
            '\\begin{minipage}{0.1\\textwidth} \n'
            '\href{#4}{\n'
            '\includegraphics[trim={30 30 30 30},'
            'clip,width=\\textwidth]{#3}} \n'
            '\end{minipage} \n' + '\end{tcolorbox} } \n' ))
    
    # Command to format a Technical Session
    # ifstrempty takes care of removing the 'body' of the TS when no TP are 
    # found and #2 is empty
    doc.preamble.append(NoEscape(
        '\\newcommand{\TS}[2]{ \n'
        '\ifstrempty{#2}{ \n'
        '\\begin{tcolorbox}[enhanced jigsaw, \n'
        'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=0pt, \n'
        'toprule=5pt,bottomrule=5pt,leftrule=5pt,rightrule=0pt, \n' 
        'colback=col4,colframe=col4, \n'
        'fontupper=\\bfseries,colupper=white, \n'
        'before skip=0pt,after skip=0pt,arc=0pt,outer arc=0pt]'
        '#1 \end{tcolorbox} }{ \n'
        '\\begin{tcolorbox}[enhanced jigsaw,breakable, \n'
        'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=0pt, \n'
        'toprule=5pt,bottomrule=5pt,leftrule=5pt,rightrule=0pt, \n'
        'colback=col3,colframe=col4, \n'
        'fonttitle=\\bfseries,coltitle=white,enforce breakable, \n'
        'title after break=(continued) #1, title=#1, \n'
        'before skip=0pt,after skip=0pt,arc=0pt,outer arc=0pt] #2 \n' 
        '\end{tcolorbox} } } \n' ))
    # Must use 'enforce breakable' (which is not recommended) for a tcolorbox 
    # nested in a breakable boxas otherwise the nested box will be defaulted 
    # to unbreakable
    
    # Command to format a Technical Session Grouping
    # doc.preamble.append(NoEscape(
    #     '\\newcommand{\TSG}[2]{ \n'
    #     '\\begin{tcolorbox}[enhanced jigsaw,breakable, \n'
    #     'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=0pt, \n'
    #     'toprule=5pt,bottomrule=5pt,leftrule=5pt,rightrule=0pt, \n'
    #     'colback=col5,colframe=col6, \n'
    #     'fonttitle=\\bfseries,coltitle=white, \n'
    #     'title after break=(continued) #1,title=#1, \n'
    #     'before skip=0pt,after skip=0pt,arc=0pt,outer arc=0pt] #2 \n' 
    #     '\end{tcolorbox} } \n' ))
    # Adding the TSG and forcing the TS as breakable doesn't make the 
    # TP go all the way to the bottom of pages...
    return doc


def pageDL(url,filename,wtxt=False):
    fullfile = AIAA_vs.DL_folder + filename + '.html'
    re_dl = True
    if (not AIAA_vs.DL_force):
        # Check if we already downloaded this file
        file_exists = os.path.exists(fullfile)
        if (file_exists):
            re_dl = False
            data = pickle.load(open(fullfile,'rb'))
            
            #file = open(fullfile, 'r')
            #data = file.read().replace('\n', '')
            #file.close()
            
    if (re_dl):
        #response = requests.get(url)
        response = AIAA_vs.session.get(url)
        data = response.text
        
        # Split string by lines
        datb = data.split('\r\n')
        # Remove empty strings
        datb = list(filter(None,datb))
        
        # Write webpage data to file
        pickle.dump(datb,open(fullfile,'wb'))
        #file = open(fullfile, 'w')
        #for line in data:
        #    file.write(line)
        #file.close()
        
    if (wtxt):
        # For debug
        file = open( AIAA_vs.DL_folder + filename + '.html', 'w')
        file.write(str(data))
        # Can also parse the html out
        #file.write(html2text.html2text(str(data)))
        file.close()
        
    return data


def paperLoader(lines,idx,idx_lim,TPnum,ts):
    #global session, url_base
    tag1 = 'class="result-card-title">'
    tag2 = '<a href="' # Tag2 is before tag1, but it is not unique to papers
    tag3 = '<p class="result-card-sub-title">'
    tag4 = '<strong>'
    tag5 = '<i data-feather=\'clock\'></i><span>' # Clock starting tag
    tag6 = '</ul>' # Last tag of the authors
    tag7 = ' - <em>' # Tag between author and affiliation

    tp = AIAA_vs.AIAA_technical_paper()
    tp.authors = []
    tp.affil = []
    
    ierr = 0 # No TP found yet
    
    # Start looking for tag1 at index provided
    flag = True
    while flag:
        line = lines[idx]
        # Search TP starting and ending tags as 
        # tag2 also appears in 'Panel Discussion' (and perhaps others)
        #   which can cause issues later so we check data_primary_key to
        #   not work on the 'Panel Dscussion'
        
        ibeg = line.find(tag2) # Tag2 comes up first in the line
        iend = line.find(tag1)
        if ((ibeg != -1) and (iend != -1)):
            # Found TP
            ierr = 1
            flag = False

            tp.data_primary_key = line[ (ibeg+len(tag2)):(iend-2) ]
            # We could directly load the TP and try to extract the leftover
            # data but we would not be able to rely on tags, instead we would 
            # need to remove most html tags and assume what is left is always 
            # the same info in the same order...
    
            # Generate URL to later request the TP and DOI or generate
            # QR code based on URL if no DOI
            tp.url = AIAA_vs.url_base + tp.data_primary_key
    
            ibeg = line.find(tag1)
            tp.result_card_title = line[ (ibeg+len(tag1)):-4 ]
            # Remove unicode characters (mu, sigma, ...)
            tp.result_card_title = unicode_to_latex(tp.result_card_title)
            # Escape the commas
            tp.result_card_title = escape_all(tp.result_card_title,',')
            # Code below escapes commas too
            #ibeg = list(find_all(tp.result_card_title,','))
            #if ibeg:
            #    # This executes if the array is non-empty
            #    for iend in reversed(ibeg):
            #        # Reverse iterate so we don't change index positions
            #        tp.result_card_title = tp.result_card_title[:iend] +
            #                               '{,}' + 
            #                               tp.result_card_title[iend+1:]
            
            # Increase line index as we read everything on this line
            idx += 1
            line = lines[idx]
            ibeg = line.find(tag3)
            #iend = line.find('</p>')
            tp.result_card_sub_title = line[ (ibeg+len(tag3)):-4 ] #iend ]
                
            # These TP cause issues with their partially missing info
            # (Here we must use the names that are escaped !)
            badTP = ['Boundary Layer Turbulence Flight Experiment in Memory of Dr. Michael Holden: Project Definition (Invited Talk)',
                     'Overview of NASA EDL Technology Strategy and EDL Session Organization',
                     'Panel Discussion',
                     'Overview Talk-Dr. Alok Majumdar',
                     'Invited talk with Dan Hauser',
                     'Invited Talk: Adam Smith et al.{,} Low Leakage Valves for long duration missions',
                     'Presenter Q\\&A',
                     'Invited Talk: Koki Ho'
                     ]

            if (not (tp.result_card_title in badTP)):
                # Actual good TP
                TPnum += 1
    
                # Search additional tags on some future line
                flag2 = True
                while flag2:
                    line = lines[idx]
                    i1 = line.find(tag4)
                    i2 = line.find(tag5)
                    if (i1 != -1):
                        # Found tag
                        flag2 = False
                        tp.paper_number = line[ (i1+len(tag4)):(len(tag4)+14) ]
                        #tp.start_time = line[ -14:-7 ]
                        tp.start_time = line[ (i2+len(tag5)):(i2+len(tag5)+5) ]
                        
                        # Skip a line
                        idx += 2
                        
                        # Get authors and affiliations
                        flag3 = True
                        while flag3:
                            line = lines[idx]
                            i1 = line.find(tag6)
                            
                            if (i1 == -1):
                                # DID NOT find ending tag so we still have an
                                # author
                                line = line[ 4:-10 ]
    
                                # Split author and affiliation
                                i1 = line.find(tag7)
                                #tp.authors.append([ line[:i1], 
                                #                    line[(i1+len(tag7)):] ])
                                tp.authors.append( line[:i1] )
                                tp.affil.append( line[(i1+len(tag7)):] )
                                
                                idx += 1
                            else:
                                # Ending tag found
                                flag3 = False
                                
                            if (idx == idx_lim):
                                # Out of bounds
                                flag3 = False
        
                    else:    
                        # Tag not found
                        idx += 1
                    if (idx == idx_lim):
                        # Out of bounds
                        flag2 = False
            else:
                # Some session with different formatting found
                # Set values to not get the DOI and only do URL QR code
                ibeg = -2
                iend = -2
                
        else:
            # Tag not found
            idx += 1
        if (idx == idx_lim):
            # Out of bounds
            flag = False
            ierr = -1
    
    # If we found everything, load the TP to get URL and DOI
    if ((ibeg > -1) and (iend > -1)):
        # Assume all info for TP was found
        TP_lines = pageDL(tp.url,'DL_TP_'+tp.data_primary_key[10:])

        tag6 = '<a href="https://doi.org/'
        
        TP_idx = 0
        flag = True
        TP_idx_lim = len(TP_lines)
        while flag:
            TP_line = TP_lines[TP_idx]
            # Search starting tag of DOI
            i1 = TP_line.find(tag6)
            if (i1 != -1):
                # Found TP
                flag = False
                tp.doi = TP_line[ (i1+9):(i1+len(tag6)+19) ]
            else:   
                # Tag not found
                TP_idx += 1
            if (TP_idx == TP_idx_lim):
                # Out of bounds
                flag = False
        
        if (TPnum == 1):
            # For first TP append session name as well
            AIAA_vs.doc.append(NoEscape('\\TS{' + ts.subtitle + ' | ' + 
                ts.location + '}{\n'))
        
        aths = ''
        i1 = len(tp.authors)
        if (i1 == 1):
            # One author, just print them
            aths = aths + latexproof(str(tp.authors[0])) + ' ('
            aths = aths + latexproof(str(tp.affil[0]  )) + ')\n'
        elif (i1 > 1):
            # Multiple authors, check affiliations to combine them
            # Go through all authors minus last one (whose affiliation 
            # written regardless)
            for i2 in range(i1-1):
                if (tp.affil[i2] == tp.affil[i2+1]):
                    # Same affiliation as next author, do not append
                    # affiliation
                    aths = aths + latexproof(str(tp.authors[i2])) + ', '
                else:
                    # Different affiliation than next author, append 
                    # affiliation
                    aths = aths + latexproof(str(tp.authors[i2])) + ' ('
                    aths = aths + latexproof(str(tp.affil  [i2])) + '),\n'
            
            # Add last author and its affiliation
            aths = aths + latexproof(str(tp.authors[i1-1])) + ' ('
            aths = aths + latexproof(str(tp.affil  [i1-1])) + ')\n'
            
        doi =''
        if (tp.doi):
            # Generate QR code
            img = qrcode.make(tp.doi)
            # Save as an image file
            img.save(AIAA_vs.DL_folder + 'Images/' + tp.doi[-4:] + '.png')
            
            doi = tp.doi[-4:]
            AIAA_vs.doc.append(NoEscape('\\TP{' + 
                tp.result_card_title + '} \n {' +
                tp.result_card_sub_title + ' | ' + 
                tp.paper_number + '\\\ \n' + aths + '}{' +
                doi + '}{' + tp.doi + '} \n' ))
        else:
            # Generate QR code based on TP's URL
            img = qrcode.make(tp.url)
            # Save as an image file
            # Assume the last 8 characters of the URL are unique enough 
            # for no collisions with another session that has no DOI
            img.save(AIAA_vs.DL_folder + 'Images/' + 'NoDOI' + 
                     tp.data_primary_key[-8:] + '.png')
            
            AIAA_vs.doc.append(NoEscape('\\TP{' + 
                tp.result_card_title + '} \n {' +
                tp.result_card_sub_title + ' | ' + 
                tp.paper_number + '\\\ \n' + aths + '}{NoDOI' +
                tp.data_primary_key[-8:] + '}{' + 
                tp.url + '} \n' ))
             
    # To debug the TP causing issues
    #if (tp.result_card_title == 'Presenter Q\\&A'):
    #if (ts.subtitle == 'FD-60'):
    #    AIAA_vs.doc.generate_pdf('Schedule', clean_tex=False)
    #    exit
    #    print('TS:' + tp.result_card_title)
                
    elif ((ibeg == -2) and (iend == -2)):
        # Found a TP with different format
        
        # Apped session info if first session
        if (TPnum == 1):
            AIAA_vs.doc.append(NoEscape('\\TS{' + ts.subtitle + ' | ' + 
                ts.location + '}{\n'))
            
        # Generate QR code based on TP's URL
        img = qrcode.make(tp.url)
        # Save as an image file
        # Assume the last 8 characters of the URL are unique enough 
        # for no collisions with another session that has no DOI
        img.save(AIAA_vs.DL_folder + 'Images/' + 'NoDOI' + 
                 tp.data_primary_key[-8:] + '.png')
        
        AIAA_vs.doc.append(NoEscape('\\TP{' + 
            tp.result_card_title + '} \n {' +
            tp.result_card_sub_title + '\n }{NoDOI' +
            tp.data_primary_key[-8:] + '}{' + 
            tp.url + '} \n' ))
        
    return tp, idx, ierr, TPnum
            
            
def sessionLoader(lines,idx,idx_lim):
    #global session, url_base
    tag1 = '<div class="session-unit "'
    tag2 = 'data-primary-key'
    tag3 = 'data-utc-date'
    tag4 = 'data-type'
    tag5 = '<time class="schedule-widget-day-abbrev">'
    tag6 = '<time class="start">'
    tag7 = '<time class="end">'
    tag8 = '<div class="session-category">'
    #tag8 = '<a class="schedule-widget-title-notmobile"'
    tag9 = '<div class="subtitle">'
    # Location is tricky...
    # Maybe use: <div class="schedule-location-blocks">
    tag10 = '<div class="label-block icon-in-person">'

    ts = AIAA_vs.AIAA_technical_session()
    ierr = 0 # No TS found yet
    
    # Start looking for tag1 at index provided
    flag = True
    while flag:
        line = lines[idx]
        # Search TS starting tag
        i1 = line.find(tag1)
        if (i1 != -1):
            ierr = 1
            # Found TS
            flag = False

            ibeg = line.find(tag2)
            iend = line.find(tag3)
            ts.data_primary_key = line[ (ibeg+len(tag2)+2):(iend-2) ]
            
            ibeg = line.find(tag3)
            iend = line.find(tag4)
            ts.data_utc_date    = line[ (ibeg+len(tag3)+2):(iend-2) ]
            
            ibeg = line.find(tag4)
            ts.data_type        = line[ (ibeg+len(tag4)+2):-2 ]
            
            # Search additional tag on some future line
            flag2 = True
            while flag2:
                line = lines[idx]
                i1 = line.find(tag5)
                if (i1 != -1):
                    # Found tag
                    flag2 = False
                    ts.day = line[ (i1+len(tag5)):-7 ]
                    
                    # Search additional tag on some future line
                    flag3 = True
                    while flag3:
                        line = lines[idx]
                        i1 = line.find(tag6)
                        if (i1 != -1):
                            # Found tag
                            flag3 = False
                            ts.start_time = line[ (i1+len(tag6)):(i1+len(tag6)+5) ]
                            
                            i1 = line.find(tag7)
                            ts.end_time   = line[ (i1+len(tag7)):(i1+len(tag7)+5) ]
                        
                            # Search additional tag on some future line
                            flag4 = True
                            while flag4:
                                line = lines[idx]
                                i1 = line.find(tag8)
                                if (i1 != -1):
                                    # Found tag
                                    flag4 = False
                                    ts.category = line[ (i1+len(tag8)):-6 ]
                        
                                    # Search additional tag on some future line
                                    flag5 = True
                                    while flag5:
                                        line = lines[idx]
                                        i1 = line.find(tag9)
                                        if (i1 != -1):
                                            # Found tag
                                            flag5 = False
                                            ts.subtitle = line[ (i1+len(tag9)):-6 ]
                        
                                            # Search additional tag on some future line
                                            flag6 = True
                                            while flag6:
                                                line = lines[idx]
                                                i1 = line.find(tag10)
                                                if (i1 != -1):
                                                    # Found tag
                                                    flag6 = False
                                                    
                                                    # Value is on next line
                                                    idx += 1
                                                    line = lines[idx]
                                                    ts.location = line.strip()
                                                    
                                                    # Could try to get the description here
                                                    # ts.description
           
                                                else:
                                                    # Tag not found
                                                    idx += 1
                                                if (idx == idx_lim):
                                                    # Out of bounds
                                                    flag6 = False
                        
                                        else:
                                            # Tag not found
                                            idx += 1
                                        if (idx == idx_lim):
                                            # Out of bounds
                                            flag5 = False
                        
                                else:
                                    # Tag not found
                                    idx += 1
                                if (idx == idx_lim):
                                    # Out of bounds
                                    flag4 = False
                        
                        else:
                            # Tag not found
                            idx += 1
                        if (idx == idx_lim):
                            # Out of bounds
                            flag3 = False
                            
                else:    
                    # Tag not found
                    idx += 1
                if (idx == idx_lim):
                    # Out of bounds
                    flag2 = False
        
        else:            
            # Tag not found
            idx += 1
        if (idx == idx_lim):
            # Out of bounds
            flag = False
            ierr = -1
            
    if (i1 != -1):                                        
        # Load the TS
        url = (AIAA_vs.url_base + '/Category/' + ts.data_primary_key)
        TS_lines = pageDL(url,'DL_TS_'+ts.data_primary_key)
        TS_idx = 0
        TS_idx_lim = len(TS_lines)
        
        #print('TS URL: ',url)
        
        # We could read the tags from the TS, but instead we only read
        # the different TP until we run out of lines
        ierr2 = 1
        TPnum = 0
        while ierr2 > 0:
            tp, TS_idx, ierr2, TPnum = paperLoader(TS_lines,TS_idx,
                                                   TS_idx_lim,TPnum,ts)
            ts.papers.append(tp)
        
        if (TPnum == 0):
            # No TP found, make a short TS
            AIAA_vs.doc.append(NoEscape('\\TS{' + ts.subtitle + ' | ' + 
                ts.location + '}{}\n'))
        else:
            # Standard closure
            AIAA_vs.doc.append(NoEscape('}'))
        
    #AIAA_vs.doc.generate_pdf('Schedule', clean_tex=False)
    #exit

    # We only search for one technical session at the time
    # Thus call the function again for another TS
    return ts, idx, ierr


def sessionGroupingLoader(lines,idx,idx_lim):
    #global session, url_base
    tag1 = '<div class="session-unit  technical-session-grouping "'
    tag2 = 'data-utc-date'
    tag3 = 'data-date'
    tag4 = 'data-type'
    tag5 = 'data-end-time'
    tag6 = 'data-start-time'
    tag7 = 'id'
    tag_op1 = '<time class="schedule-widget-day-abbrev">'
    tag_op2 = '<time class="start">'
    
    tsg = AIAA_vs.AIAA_technical_session_grouping()
    ierr = 0 # No TSG found yet
    
    # Start looking for tag1
    flag = True
    while flag:
        line = lines[idx]
        # Search starting tag of technical session grouping
        i1 = line.find(tag1)
        
        if (i1 != -1):
            # Found technical session grouping
            flag = False
            
            ibeg = line.find(tag2)
            iend = line.find(tag3)
            tsg.data_utc_date   = line[ (ibeg+len(tag2)+2):(iend-2) ]
            
            ibeg = line.find(tag3)
            iend = line.find(tag4)
            tsg.data_date       = line[ (ibeg+len(tag3)+2):(iend-2) ]
            
            ibeg = line.find(tag4)
            iend = line.find(tag5)
            tsg.data_type       = line[ (ibeg+len(tag4)+2):(iend-2) ]
            
            ibeg = line.find(tag5)
            iend = line.find(tag6)
            tsg.data_end_time   = line[ (ibeg+len(tag5)+2):(iend-2) ]
            
            ibeg = line.find(tag6)
            iend = line.find(tag7)
            tsg.data_start_time = line[ (ibeg+len(tag6)+2):(iend-2) ]
            
            ibeg = line.find(tag7)
            tsg.id              = line[ (ibeg+len(tag7)+2):-2 ]
            
            # Search additional tag on some future line
            flag2 = True
            while flag2:
                line = lines[idx]
                i2 = line.find(tag_op1)
                
                if (i2 != -1):
                    # Found tag
                    flag2 = False
                    tsg.day = line[ (i2+len(tag_op1)):-7 ]
                    
                    # Search additional tag on some future line
                    flag3 = True
                    while flag3:
                        line = lines[idx]
                        i3 = line.find(tag_op2)
                        
                        if (i3 != -1):
                            # Found tag
                            flag3 = False
                            tsg.start_time = line[ (i3+len(tag_op2)):-7 ]
                        
                        else:
                            # Tag not found
                            idx += 1
                        if (idx == idx_lim):
                            # Out of bounds
                            flag3 = False
                            
                else:    
                    # Tag not found
                    idx += 1
                if (idx == idx_lim):
                    # Out of bounds
                    flag2 = False
        
        else:            
            # Tag not found
            idx += 1
        if (idx == idx_lim):
            # Out of bounds
            flag = False
    
    if (i1 != -1):
        # Assume all info for technical session grouping was found
        print('Loading TSG: '+tsg.data_type)
        
        # Format TSG in nice manner
        #AIAA_vs.doc.append(NoEscape('\\TSG{' + tsg.start_time + ' | ' + 
        #    tsg.data_type + '}{ \n'))
        AIAA_vs.doc.append(Command('mysubsection',
           tsg.start_time + ' | ' + tsg.data_type ))
    
        # Generate URL to request the technical sessions within grouping
        url = (AIAA_vs.url_base + 
               '/Schedule/_GetTechnicalSessionGroupingPanel?' +
               'start=' + tsg.data_start_time +
               '&resultsPerPage=100' +
               '&sort=0' +
               '&end=' + tsg.data_end_time +
               '&type=' + tsg.data_type +
               '&pageNumber=0' +
               '&date=' + tsg.data_date)
               # Below tags are optional: 
               #'' + tsg.data_utc_date +
               #'' + tsg.id +
               #'' + tsg.day)
        
        lines = pageDL(url,'DL_TSG_'+tsg.data_start_time+'_'+tsg.data_type)
        
        # Set index for technical sessions to be added
        idx_ts = 0
        
        tag_op3 = '<time class="list-time">'
        # Start looking for tag_op3
        idx = 0
        idx_lim = len(lines)
        flag = True
        while flag:
            line = lines[idx]
            # Search time tag of technical session grouping
            i1 = line.find(tag_op3)
            if (i1 != -1):
                # Found tag
                flag = False
                
                tsg.list_time = line[ (i1+len(tag_op3)):-7 ]
                
                # Iterate on sessions as long as we have leftover lines
                flag2 = True
                while flag2:                    
                    # Look for a technical session
                    ts, idx, ierr = sessionLoader(lines,idx,idx_lim)
                    if (ierr > 0):
                        # No errors, found TS, append it to list
                        tsg.sessions.append(ts)
                        idx_ts += 1
                        
                        print('TS Loaded: '+ str(idx_ts) + ' | ' + ts.subtitle )
                        
                    else:
                        # We did not find anymore sessions, quit TSG function
                        flag = False
                        flag2 = False

            else:            
                # Tag not found
                idx += 1
            if (idx == idx_lim):
                # Out of bounds
                flag = False
                ierr = -1
                
    if (i1 == -1):
        ierr = -2
        print('Error: Technical Session Grouping did not get info !')
        
    
    #AIAA_vs.doc.append(NoEscape('}'))
        
    #AIAA_vs.doc.generate_pdf('Schedule', clean_tex=False)
    #exit
    
    return tsg, idx, ierr
    
    
def dayLoader(idx_lim):
    tag1 = '<div class="session-unit  technical-session-grouping'

    AIAA_vs.FS_idx += 1
    # Find sessions or session groups
    flag_grp = True
    while flag_grp:
        line = AIAA_vs.FS_lines[AIAA_vs.FS_idx]
        i1 = line.find(tag1)
        if (i1 != -1):
            # Technical Session Grouping
            tsg, idx, ierr = sessionGroupingLoader(AIAA_vs.FS_lines, 
                                                   AIAA_vs.FS_idx, idx_lim)
            AIAA_vs.FS_idx += 1 # For debug
            
            #AIAA_vs.doc.generate_pdf('Schedule', clean_tex=False)
            #exit
    
        else:
            AIAA_vs.FS_idx += 1
            
        if (AIAA_vs.FS_idx == idx_lim):
            # Out of bounds
            flag_grp = False
            #print('Out of bounds: dayLoader')
    return

