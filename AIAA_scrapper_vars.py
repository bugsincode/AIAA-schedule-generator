global DL_force, DL_folder, colorscheme, session, url_base, doc, FS_lines, \
       FS_idx, FS_idx_lim, noqrcodes        


class AIAA_technical_paper:
    def __init__(self, data_primary_key=None, result_card_title=None, 
                 result_card_sub_title=None, paper_number=None, 
                 start_time=None, authors: [str]=[], affil: [str]=[],
                 url=None, doi=None):
        self.data_primary_key = data_primary_key
        self.result_card_title = result_card_title
        self.result_card_sub_title = result_card_sub_title
        self.paper_number = paper_number
        self.start_time = start_time
        self.authors = authors
        self.affil = affil
        self.url = url
        self.doi = doi
        

class AIAA_technical_session:
    def __init__(self, name=None, data_primary_key=None, data_utc_date=None, 
                 data_type=None, day=None, start_time=None, end_time=None, 
                 category=None, subtitle=None, location=None, description=None,
                 papers: [AIAA_technical_paper]=[]):
        self.data_primary_key = data_primary_key
        self.data_utc_date = data_utc_date
        self.data_type = data_type
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.category = category
        self.subtitle = subtitle
        self.location = location
        self.description = description
        self.papers = papers


class AIAA_technical_session_grouping:
    def __init__(self, data_utc_date=None, data_date=None, data_type=None,
                 data_end_time=None, data_start_time=None, id=None, day=None, 
                 start_time=None, list_time=None, 
                 sessions: [AIAA_technical_session]=[]):
        self.data_utc_date = data_utc_date
        self.data_date = data_date
        self.data_type = data_type
        self.data_end_time = data_end_time
        self.data_start_time = data_start_time
        self.id = id
        self.day = day
        self.start_time = start_time
        self.list_time = list_time
        self.sessions = sessions
        
        