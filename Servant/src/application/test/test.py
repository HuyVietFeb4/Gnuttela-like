# External library
import rbloom
import re
bf = rbloom.Bloom(100000, 0.01)
# Just the file names
real_files = [
    "Deep_Learning_Notes_v2.pdf",
    "AI Research Report (2025).docx",
    "Graph-Neural-Networks-Overview.txt",
    "Project Plan Draft 1.pdf",
    "Data.Analysis.Results.2024.csv",
    "Machine_Learning-Guide.pdf",
    "Computer Vision Manual v3.docx",
    "Natural.Language.Processing.Paper.pdf",
    "Reinforcement-Learning_Slides.ppt",
    "AI Conference Agenda 2023.pdf",
    "Cloud_Computing_Overview-v1.pdf",
    "Distributed Systems Lecture 2022.pdf",
    "Database.Design.Basics_v2.pdf",
    "Operating-Systems_Notes.docx",
    "Networking Fundamentals 101.pdf",
    "Cyber_Security-Guide-v5.pdf",
    "Software Engineering Outline.pdf",
    "Algorithms.Handbook.2020.pdf",
    "Data_Structures_Reference-v2.pdf",
    "Python Programming Tutorial 3.pdf",
    "Java.Programming.Notes-v1.pdf",
    "C++ Basics 101.pdf",
    "Web-Development Guide.pdf",
    "Mobile_App-Design_v4.pdf",
    "Big.Data.Analytics.2021.pdf",
    "Statistics_For_DataScience-v2.pdf",
    "Linear Algebra Notes.pdf",
    "Calculus.Workbook-v3.pdf",
    "Physics Fundamentals 2020.pdf",
    "Chemistry-Basics_v1.pdf"
]


test_keywords = [
    ("deep", True),          # from Deep_Learning_Notes_v2.pdf
    ("learning", True),      # appears in multiple files
    ("notes", True),         # appears in several
    ("ai", True),            # appears in AI Research Report
    ("report", True),        # appears in AI Research Report
    ("biology", False),      # not in any file
    ("graph", True),         # Graph-Neural-Networks
    ("networks", True),      # Graph-Neural-Networks
    ("draft", True),         # Project Plan Draft
    ("results", True),       # Data.Analysis.Results
    ("machine", True),       # Machine_Learning-Guide
    ("vision", True),        # Computer Vision Manual
    ("manual", True),        # Computer Vision Manual
    ("processing", True),    # Natural Language Processing Paper
    ("paper", True),         # Natural Language Processing Paper
    ("slides", True),        # Reinforcement-Learning_Slides
    ("conference", True),    # AI Conference Agenda
    ("agenda", True),        # AI Conference Agenda
    ("cloud", True),         # Cloud_Computing_Overview
    ("computing", True),     # Cloud_Computing_Overview
    ("distributed", True),   # Distributed Systems Lecture
    ("systems", True),       # Distributed Systems Lecture
    ("database", True),      # Database.Design.Basics
    ("design", True),        # Database.Design.Basics
    ("operating", True),     # Operating-Systems_Notes
    ("security", True),      # Cyber_Security-Guide
    ("biology", False),      # not present
    ("economics", False),    # not present
    ("history", False),      # not present
    ("geography", False)     # not present
]


def create_keyword_list(filename: str):
    filename = filename.lower()
    filename = re.sub(r'[ .\-_]', ' ', filename)
    pattern = r'[a-z0-9._\-()&\[\]+=,]+'
    return re.findall(pattern, filename)

def create_bf(files):
    '''
        Breaks down a filename into keywords and adds them to the Bloom filter.
    '''
    pass

    
# Add each file name to the Bloom filter
# for f in files:
#     bf.add(f)

# for file in test_files:
#     or_not = ' ' if file[1] == False else ' not '
#     print(f'{file[0]} should{or_not}be in the list')
#     print(f'Bloom filter output: {file[0] in bf}')
#     print('-----------------------------------------')

if __name__ == "__main__":
    for real_file in real_files:
        keyword_list = create_keyword_list(real_file)
        for keyword in keyword_list:
            bf.add(keyword)

    for keyword in test_keywords:
        should_be = ' ' if keyword[1] == True else ' not '
        print(f'{keyword[0]} should{should_be}be in the list')
        print(f'Bloom filter output: {keyword[0] in bf}')
        print('-----------------------------------------')