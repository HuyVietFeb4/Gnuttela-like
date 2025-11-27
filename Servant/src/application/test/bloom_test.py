# External library
import sys
sys.path.append("../")
import rbloom
from bloom import BloomFilter
import re
bf = rbloom.Bloom(100000, 0.01)
bf1 = BloomFilter(100000, 0.01)
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
    "Chemistry-Basics_v1.pdf",
    "Genomics_Research_2021.pdf",
    "Bioinformatics-Guide-v2.pdf",
    "Artificial.Intelligence.Trends.2025.pdf",
    "Quantum_Computing_Notes.docx",
    "Blockchain-Technology-Overview.pdf",
    "Cryptography.Handbook.2022.pdf",
    "Cloud_Security_Report-v3.pdf",
    "IoT_Systems_Design_2024.pdf",
    "Edge-Computing-Applications.pdf",
    "Virtual.Reality.Manual-v1.pdf",
    "Augmented-Reality-Guide.pdf",
    "3D_Printing_Tutorial.pdf",
    "Robotics_Engineering_Notes.docx",
    "Automation.Systems_v2.pdf",
    "Control.Theory.Handbook.pdf",
    "Signal_Processing_2023.pdf",
    "Image-Recognition-Overview.pdf",
    "Speech.Processing.Guide.pdf",
    "Natural.Sciences.Intro.pdf",
    "Environmental-Science-Report.pdf",
    "Climate.Change.Analysis.2025.pdf",
    "Renewable_Energy_Notes.pdf",
    "Solar.Power.Design-v1.pdf",
    "Wind-Energy-Systems.pdf",
    "Hydropower_Engineering_2022.pdf",
    "Battery.Technology.Manual.pdf",
    "Electric.Vehicles.Report.pdf",
    "Transportation.Systems.Overview.pdf",
    "Smart.City.Design-v2.pdf",
    "Urban.Planning.Notes.pdf",
    "Architecture.Handbook.2023.pdf",
    "Civil.Engineering.Basics.pdf",
    "Mechanical_Engineering_Outline.pdf",
    "Electrical.Circuits.v1.pdf",
    "Electronics.Design.2024.pdf",
    "Semiconductor.Technology.Report.pdf",
    "Nanotechnology_Research_Notes.pdf",
    "Biotechnology.Handbook-v2.pdf",
    "Pharmaceutical.Science.Overview.pdf",
    "Medical.Imaging.Manual.pdf",
    "Healthcare.Systems.Report.pdf",
    "Public.Health.Notes.pdf",
    "Psychology.Introduction-v1.pdf",
    "Sociology.Outline.2020.pdf",
    "Political.Science.Report.pdf",
    "Economics.Analysis.2023.pdf",
    "Finance.Handbook-v2.pdf",
    "Accounting.Basics.2021.pdf",
    "Business.Management.Notes.pdf",
    "Marketing.Strategy.Report.pdf",
    "Entrepreneurship.Guide-v1.pdf",
    "E-Commerce.Trends.2024.pdf",
    "Supply.Chain.Analysis.pdf",
    "Logistics.Systems.Overview.pdf",
    "Operations.Research.Handbook.pdf",
    "Project.Management.Outline.pdf",
    "Leadership.Notes.2022.pdf",
    "Ethics.In.Business.pdf",
    "Philosophy.Introduction-v3.pdf",
    "History.World.Civilizations.pdf",
    "Geography.Notes.2021.pdf",
    "Anthropology.Report-v2.pdf",
    "Archaeology.Handbook.pdf",
    "Linguistics.Overview.2020.pdf",
    "Literature.Analysis.Notes.pdf",
    "Art.History.Report.pdf",
    "Music.Theory.Guide.pdf",
    "Film.Studies.Outline.pdf",
    "Theatre.Arts.Manual.pdf",
    "Education.Pedagogy.Notes.pdf",
    "Teaching.Methods.Report.pdf",
    "Learning.Sciences.Handbook.pdf",
    "Curriculum.Design-v1.pdf",
    "Instructional.Technology.Overview.pdf",
    "Assessment.Strategies.Notes.pdf",
    "Aerospace-Engineering-Fundamentals.pdf",
    "Materials.Science.Introduction.pdf",    
    "Astrophysics.Lecture.Notes.pdf",        
    "Organic-Chemistry-Reactions.pdf",       
    "Marine-Biology-Ecosystems.pdf",         
    "Classical.Mechanics.Problems.pdf",      
    "Microeconomics.Theory.2024.pdf",       
    "Jurisprudence.Essays.pdf",              
    "Creative.Writing.Workshop.Notes.docx",  
    "Photography.Techniques.Manual.pdf",     
    "Culinary.Arts.Basics.pdf",              
    "Welding.Safety.Guide.pdf"          
]

test_keywords = [
    ("deep", True), ("learning", True), ("notes", True), ("ai", True), ("report", True),
    ("biology", False), ("graph", True), ("networks", True), ("draft", True), ("results", True),
    ("machine", True), ("vision", True), ("manual", True), ("processing", True), ("paper", True),
    ("slides", True), ("conference", True), ("agenda", True), ("cloud", True), ("computing", True),
    ("distributed", True), ("systems", True), ("database", True), ("design", True), ("operating", True),
    ("security", True), ("economics", True), ("history", True), ("geography", True), ("genomics", True),
    ("bioinformatics", True), ("artificial", True), ("intelligence", True), ("quantum", True), ("computing", True),
    ("blockchain", True), ("cryptography", True), ("iot", True), ("edge", True), ("virtual", True),
    ("augmented", True), ("printing", True), ("robotics", True), ("automation", True), ("control", True),
    ("signal", True), ("image", True), ("speech", True), ("environmental", True), ("climate", True),
    ("renewable", True), ("solar", True), ("wind", True), ("hydropower", True), ("battery", True),
    ("electric", True), ("transportation", True), ("smart", True), ("urban", True), ("architecture", True),
    ("civil", True), ("mechanical", True), ("electrical", True), ("electronics", True), ("semiconductor", True),
    ("nanotechnology", True), ("biotechnology", True), ("pharmaceutical", True), ("medical", True), ("healthcare", True),
    ("psychology", True), ("sociology", True), ("political", True), ("economics", True), ("finance", True),
    ("accounting", True), ("business", True), ("marketing", True), ("entrepreneurship", True), ("commerce", True),
    ("supply", True), ("logistics", True), ("operations", True), ("project", True), ("leadership", True),
    ("ethics", True), ("philosophy", True), ("history", True), ("geography", True), ("anthropology", True),
    ("archaeology", True), ("linguistics", True), ("literature", True), ("art", True), ("music", True),
    ("film", True), ("theatre", True), ("education", True), ("teaching", True), ("learning", True),
    ("curriculum", True), ("instructional", True), ("assessment", True),
    ("biology", False), ("astronomy", False),
    # Additional False options
    ("zoology", False), ("meteorology", False), ("oceanography", False), ("geology", False), ("paleontology", False),
    ("astrophysics", True), ("cosmology", False), ("lingua", False), ("mythology", False), ("alchemy", False),
    ("astrology", False), ("numismatics", False), ("ornithology", False), ("entomology", False), ("horticulture", False),
    ("agriculture", False), ("fisheries", False), ("mining", False), ("aviation", False), ("naval", False),
    ("aerospace", True),  # from Aerospace-Engineering-Fundamentals.pdf
    ("materials", True),  # from Materials.Science.Introduction.pdf
    ("organic", True),    # from Organic-Chemistry-Reactions.pdf
    ("marine", True),     # from Marine-Biology-Ecosystems.pdf
    ("classical", True),  # from Classical.Mechanics.Problems.pdf
    ("mechanics", True),  # from Classical.Mechanics.Problems.pdf
    ("jurisprudence", True), # from Jurisprudence.Essays.pdf
    ("writing", True),    # from Creative.Writing.Workshop.Notes.docx
    ("photography", True), # from Photography.Techniques.Manual.pdf
    ("culinary", True),   # from Culinary.Arts.Basics.pdf
    ("welding", True),    # from Welding.Safety.Guide.pdf
    ("microeconomics", True), # from Microeconomics.Theory.2024.pdf
    # Additional False options (reinforcing non-existence)
    ("cartography", False), # Not in file list
    ("paleobotany", False), # Not in file list
    ("folklore", False),    # Not in file list
    ("etymology", False),   # Not in file list
    ("geophysics", False),  # Not in file list
    ("seismology", False),  # Not in file list
    ("veterinary", False)   # Not in file list
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
            bf1.add(keyword)

    for keyword in test_keywords:
        should_be = ' ' if keyword[1] == True else ' not '
        print(f'{keyword[0]} should{should_be}be in the list')
        print(f'Bloom filter bf output: {keyword[0] in bf}')
        print(f'Bloom filter bf1 output: {not bf1.is_available(keyword[0])}')
        print('-----------------------------------------')