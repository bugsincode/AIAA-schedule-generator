import AIAA_scrapper_vars as AIAA_vs
import AIAA_scrapper_functions as AIAA_fc

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pylatex import NewPage, Command
from pylatex.utils import NoEscape
import os
import qrcode

# Usual AIAA page structure (sometimes it differs):
# AIAA_full_schedule                (FS )
#  AIAA_day                         (DAY)
#   AIAA_technical_session_grouping (TSG)
#    AIAA_technical_session         (TS )
#     AIAA_technical_paper          (TP )

# Remove QR codes for a concise schedule
AIAA_vs.noqrcodes = False
# AIAA
AIAA_vs.colorscheme = ['FFFFFF','78af03','1a3d6d','151b47','f7f27d','8a2932']
# Grayscale (for printing)
#AIAA_vs.colorscheme = ['FFFFFF','565656','FFFFFF','000000','FFFFFF','000000']

# The code will check locally if the necessary HTML files are present to 
# avoid downloading them again to generate the schedule. This can be disabled
# to force re-downloading the files using the option 'DL_force'
AIAA_vs.DL_force  = False
AIAA_vs.url_base = 'https://virtualscitech.aiaa.org'
AIAA_vs.DL_folder = './AIAA_data/'
# Create the directory (webpage data) and subdirectory (QR code images)
os.makedirs(os.path.dirname(AIAA_vs.DL_folder+'Images/'), exist_ok=True)

# Start the Latex document
AIAA_vs.doc = AIAA_fc.genDoc()

# Generate QR code for GitHub repo
QR_1_link = 'https://github.com/bugsincode/AIAA-schedule-generator'
img = qrcode.make(QR_1_link)
# Save as an image file
img.save(AIAA_vs.DL_folder + 'Images/QR_1.png')
# QR code for the AIAA 'link'
QR_2_link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
img = qrcode.make(QR_2_link)
img.save(AIAA_vs.DL_folder + 'Images/QR_2.png')

# Make the first page
AIAA_vs.doc.append(NoEscape(
    '\\begin{tcolorbox}[ \n'
    'top=0pt,bottom=0pt,left=0pt,right=0pt,boxsep=2pt, \n'
    'boxrule=5pt,enhanced, \n'
    'frame style={left color=col3,right color=col4}, \n'
    'interior style={bottom color=col2,top color=col1}, \n'
    'before skip=0pt,after skip=0pt,arc=0pt,outer arc=5pt] \n'
    '\\begin{minipage}{1.9cm} \n'
    '\href{' + QR_1_link + '}{\n' +
    '\includegraphics[trim={30 30 30 30},' +
    'clip,width=\\textwidth]{QR_1}} \n' +
    '\end{minipage} \n'
    '\\begin{minipage}{0.8\\textwidth} \n'
    '\\begin{center} \n'
    '\\begin{Huge} \n'
    '\\textrm{Offline AIAA schedule that is actually useful.}\n'
    '\end{Huge} \\\\ \n'
    '\\ \\\\ \n'
    '$\leftarrow$ Checkout the code \hfill Checkout the AIAA online version'
    '$\\rightarrow$ \n'
    '\end{center} \n'
    '\end{minipage} \n'
    '\hfill \n'
    '\\begin{minipage}{1.9cm} \n'
    '\hfill \n'
    '\href{' + QR_2_link + '}{\n' +
    '\includegraphics[trim={30 30 30 30},' +
    'clip,width=\\textwidth]{QR_2}} \n' +
    '\end{minipage} \n'
    '\end{tcolorbox} \n'
    ))

# Connection retries in case "Max retries..." fails
AIAA_vs.session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
#AIAA_vs.session.mount('http://', adapter)
AIAA_vs.session.mount('https://', adapter)

# Request a "full" schedule (which doesn't include much...)
AIAA_vs.FS_lines = AIAA_fc.pageDL(AIAA_vs.url_base + 
                          '/Schedule/_FullScheduleRequest','DL_FS')

# Find the first day
FS_tag1 = '<time class="day-date list-title">'
AIAA_vs.FS_idx = 4 # Set to 0, but we want to skip Sunday (the first day)
AIAA_vs.FS_idx_lim = len(AIAA_vs.FS_lines)
FS_flag = True
while FS_flag:
    line = AIAA_vs.FS_lines[AIAA_vs.FS_idx]
    i1 = line.find(FS_tag1)
    
    if (i1 != -1):
        # Get the day
        line = line[ (i1+len(FS_tag1)):-7 ]
        # Create Latex section for day
        AIAA_vs.doc.append(Command('mysection',line))
        
        # Escape the commas
        line = AIAA_fc.escape_all(line,',')
        
        print('Loading day: '+line)
        
        # Find which line the next day starts so we only give the necessary 
        # lines to dayLoader()
        FS_flag2 = True
        FS_idx2 = AIAA_vs.FS_idx + 1
        while FS_flag2:
            #print( 'Debug: ' + str(AIAA_vs.FS_idx) + '|' + 
            #      str(AIAA_vs.FS_idx_lim) + '|' + str(FS_idx2) )
            line = AIAA_vs.FS_lines[FS_idx2]
            i2 = line.find(FS_tag1)
            if (i2 != -1):
                # Found the next day
                FS_flag2 = False
            else:
                # Did not find the next day
                if (FS_idx2 + 1 == AIAA_vs.FS_idx_lim):
                    # Out of bounds
                    FS_flag2 = False
                else:
                    # Increment line index
                    FS_idx2 += 1
                    
        # If we are on the last day, FS_idx2 will be the number of lines in
        # the file which allows the dayLoader() to read everything left
        
        AIAA_fc.dayLoader(FS_idx2)
        
        # End page and start new page between days
        AIAA_vs.doc.append(Command('hrulefill \\\ '))
        AIAA_vs.doc.append(NewPage())
        #AIAA_vs.doc.append(Command('FloatBarrier'))
        
    if (i1 != -1):
        # Found a day, assign the next day's index to start the search
        AIAA_vs.FS_idx = FS_idx2 - 1 # Minus one might not be needed
    else:
        # No day found, increment line index
        AIAA_vs.FS_idx += 1
        
    #print( 'Debug: ' + str(AIAA_vs.FS_idx) + '|' + str(AIAA_vs.FS_idx_lim) )
    
    if (AIAA_vs.FS_idx == AIAA_vs.FS_idx_lim):
        # Out of bounds
        FS_flag = False
        
print('Finished parsing schedule.')

AIAA_vs.doc.generate_pdf('Schedule', clean_tex=False)

print('Finished generating schedule as pdf.')

