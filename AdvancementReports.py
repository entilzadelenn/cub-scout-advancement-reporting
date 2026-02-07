import pandas as pd
from datetime import datetime
import json, re, os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import shutil

def dbg(msg):
    if(debugging):
        print("DEBUG: " + str(msg)+"\n")


def makePackPDF(fname):
    #create the pack report
    packDoc = SimpleDocTemplate(fname, pagesize=letter)
    styles = getSampleStyleSheet()  
    packElements = []
    
    #register custom fonts
    pdfmetrics.registerFont(TTFont("Candara", "Candara.ttf"))
    pdfmetrics.registerFont(TTFont("Candarab", "Candarab.ttf"))

    styles["Title"].fontName = "Candarab"
    styles["Title"].fontSize = 25
    styles["Normal"].fontName = "Candara"
    styles["Normal"].fontSize = 10

    return (packDoc, packElements, styles)
    
def sanitizeinput(fname):
    with open(fname, "rb") as f:
        data = f.read()

    # Remove 0xA0
    data = data.replace(b"\xA0", b"")

    # Replace 0x93 with 0x22
    data = data.replace(b"\x93", b"\x22")
    data = data.replace(b"\x94", b"\x22")
    data = data.replace(b"\x92", b"\x27")

    with open(fname, "wb") as f:
        f.write(data)

def makeDenPDF(fname):
    #create the den report
    denDoc = SimpleDocTemplate(fname, pagesize=landscape(letter), rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36)
    denElements = []
    
    return (denDoc, denElements)

def makeTitlePage(doc, elements, styles, subtitle, landscape=False):
    # --- Title Page ---
    logo_path = "logos" + os.sep + "logo.png"  # replace with your pack's logo. You may also need to change the draw heigh/width to get the right ratio
    logo = Image(logo_path)
    logo.drawHeight = 3 * inch
    logo.drawWidth = 3 * inch

    # Center the logo (Spacer to push it down vertically)
    if not landscape:
        elements.append(Spacer(1, 2 * inch))
    elements.append(logo)
    elements.append(Spacer(1, 0.5 * inch))

    # Title
    title = Paragraph("Pack " + PACK_NUM + " Advancement Report", styles["Title"])
    elements.append(title)
    secondTitle = Paragraph(subtitle, styles["Title"])
    elements.append(secondTitle)
    elements.append(Spacer(1, 1 * inch))
  
    # Get the current date and time
    now = datetime.now()

    # Format the date and time into a "pretty" format
    # Example output: Wednesday, July 24, 2024 at 03:30 PM
    pretty_date = now.strftime("%A, %B %d, %Y at %I:%M %p")
    subtitle = Paragraph("Generated on " + pretty_date, styles["Normal"])
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(subtitle)

    # --- Page break ---
    elements.append(PageBreak())
   
def createReqs():
    scout_reqs = {}
    for rank in ranks:
        for scoutname in scoutsByRank[rank]:
            scout_data = {}
            for adventure in adventures[rank]:
                scout_data[adventure] = {}
                for requirement in adventures[rank][adventure]:
                    scout_data[adventure][requirement] = "incomplete"
            scout_reqs[scoutname] = scout_data            


    return scout_reqs

   
def analyzeRequirements(scout_reqs):
    # Set of "completed" markers
    completed_markers = {"Approved", "Awarded", "ApprovedAwarded", "AwardedApproved"}
    
    # Regular expression to extract leading number
    number_regex = re.compile(r"^\s*(\d+)")
    
    
    # Iterate through the rows starting from row 1 (since row 0 has scout names)
    current_adventure = None
    current_rank = None
    for idx, row in df.iloc[3:].iterrows(): #skip row 0, 1, and 2 which have scout names and ranks
        first_col = str(row[0]).strip()  # first column of the row
        
        #check if this starts a new rank
        '''if first_col in ranks:
            current_rank = first_col
            current_adventure = None
            continue #go to next row
        '''
        #compensates for a scoutbook issue where the ranks aren't being printed
        for rank in ranks:
            if first_col in adventures[rank]:
                current_rank = rank
                current_adventure = first_col
                continue

        # Check if this row starts a new adventure
        '''if first_col in adventures[current_rank]:
            current_adventure = first_col
            continue  # move to next row
        '''
        if current_adventure:
            # Only consider rows where the first column starts with a number
            match = number_regex.match(first_col)
            if match:
                requirement_num = match.group(1)  # extract the number as string
                
               
                
                # Check each scout's column for completion, and mark it complete if they've done it
                for i, scout in enumerate(scout_names):  # columns start at 1
                    if scout not in scoutsByRank[current_rank]:
                        continue    #skip scouts who aren't this current rank

                    cell_val = str(row[i]).strip()
                    if cell_val in completed_markers:
                        scout_reqs[scout][current_adventure][requirement_num] = "completed"
            else:
                # If the row doesn't start with a number and isn't a new adventure or rank, ignore it
                continue  
    
    #deal with the elective adventures
    for idx, row in df.iloc[3:].iterrows():
        first_col = str(row[0]).strip()  # first column of the row
        
        if "a. lion elective" in first_col.lower():
            current_adventure = "Lion Elective Adventure 2"
            current_rank = "Lion"
        elif "b. lion elective" in first_col.lower():
            current_adventure = "Lion Elective Adventure"
            current_rank = "Lion"
        elif "a. tiger elective" in first_col.lower():
            current_adventure = "Tiger Elective Adventure 2"
            current_rank = "Tiger"
        elif "b. tiger elective" in first_col.lower():
            current_adventure = "Tiger Elective Adventure"
            current_rank = "Tiger"
        elif "a. wolf elective" in first_col.lower():
            current_adventure = "Wolf Elective Adventure 2"
            current_rank = "Wolf"
        elif "b. wolf elective" in first_col.lower():
            current_adventure = "Wolf Elective Adventure"
            current_rank = "Wolf"
        elif "a. bear elective" in first_col.lower():
            current_adventure = "Bear Elective Adventure 2"
            current_rank = "Bear"
        elif "b. bear elective" in first_col.lower():
            current_adventure = "Bear Elective Adventure"
            current_rank = "Bear"
        elif "a. webelos elective" in first_col.lower():
            current_adventure = "Webelos Elective Adventure 2"
            current_rank = "Webelos"
        elif "b. webelos elective" in first_col.lower():
            current_adventure = "Webelos Elective Adventure"
            current_rank = "Webelos"
        elif "a. arrow of light elective" in first_col.lower():
            current_adventure = "Arrow of Light Elective Adventure 2"
            current_rank = "Arrow of Light"
        elif "b. arrow of light elective" in first_col.lower():
            current_adventure = "Arrow of Light Elective Adventure"
            current_rank = "Arrow of Light"
        else:
            continue

       
        requirement_num = "1"
      
        # Check each scout's column for completion
        for i, scout in enumerate(scout_names, start=0):
            if scout not in scoutsByRank[current_rank]:
                continue
            cell_val = str(row[i]).strip()
            if cell_val in completed_markers:
                scout_reqs[scout][current_adventure][requirement_num] = "completed"  
              
    return scout_reqs

def findCompletion(scout_reqs):
    for scout in scout_names[1:]:
        #scout_data = scout_reqs.get(scout, {})
        scout_data = scout_reqs[scout]
        # Count total requirements and completed
        total_reqs = 0
        total_completed = 0
        for adventure in scout_data:
            
            for req in scout_data[adventure]:
                total_reqs += 1
                if scout_data[adventure][req] == "completed":
                    total_completed += 1
        
        pct_complete = (total_completed / total_reqs * 100) if total_reqs > 0 else 0
            
        scout_completion.append((scout, pct_complete))
        
    scout_completion.sort(key=lambda x: x[1], reverse=True)
    
    return scout_completion
    
    

def makeDenOverview(denElements, styles, packElements, rank):
    #Logos to use
    main_logo = Image("logos" + os.sep + "Logo.png", width=1.0*inch, height=1.0*inch)
    den_logo = Image("logos" + os.sep + rank + ".png", width=1.0*inch, height=1.0*inch)

    #title and subtitles
    titlepara = Paragraph(rank + " Den Snapshot", styles["Title"])
    subtitlepara = Paragraph("Progress Towards Rank", styles["Title"])
  
    centerblock = [titlepara, subtitlepara]
    #put the header in a table
    title_table = Table(
        [[main_logo, centerblock, den_logo]],
        colWidths=[1.25*inch, 4.5*inch, 1.2*inch]
    )
    
    
    title_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))

    #put the header on the page for the den report
    denElements.append(title_table)
    denElements.append(Spacer(1, 12))

    #put the header on the page for the pack report
    packElements.append(title_table)
    packElements.append(Spacer(1, 12))


    NAME_WIDTH = 150
    BAR_WIDTH = 300
    BAR_HEIGHT = 12
    
    for scout, pct in scout_completion:
        
        #skip anyone not in this den
        
        if scout not in scoutsByRank[rank]:
            continue
        
        line = Drawing(NAME_WIDTH + BAR_WIDTH + 60, BAR_HEIGHT + 6)

        # Scout name
        line.add(String(
            0,
            0,
            scout,
            fontName="Candara",
            fontSize=15
        ))

        # --- Remaining portion (yellow, full width) ---
        line.add(Rect(
            NAME_WIDTH,
            0,
            BAR_WIDTH,
            BAR_HEIGHT,
            fillColor=colors.yellow,
            strokeColor=colors.black
        ))

        # --- Completed portion (blue, partial width) ---
        completed_width = BAR_WIDTH * (pct / 100)

        line.add(Rect(
            NAME_WIDTH,
            0,
            completed_width,
            BAR_HEIGHT,
            fillColor=colors.darkblue,
            strokeColor=None
        ))

        # Percentage label
        line.add(String(
            NAME_WIDTH + BAR_WIDTH + 5,
            0,
            #f"{int(pct)}%",
            f"{pct:.1f}%",
            fontName="Candara",
            fontSize=15
        ))

        denElements.append(line)
        packElements.append(line)
        denElements.append(Spacer(1, 6))
        packElements.append(Spacer(1, 6))
        
    # --- Page break ---
    denElements.append(PageBreak())
    packElements.append(PageBreak())

def buildRequirementSnapshot(denElements, styles, rank):
    #add the page title
        #Logos to use
    main_logo = Image("logos" + os.sep + "Logo.png", width=1.0*inch, height=1.0*inch)
    den_logo = Image("logos" + os.sep + rank + ".png", width=1.0*inch, height=1.0*inch)

    #title and subtitles
    titlepara = Paragraph(rank + " Den Outstanding Requirements", styles["Title"])
    
    #put the header in a table
    title_table = Table(
        [[main_logo, titlepara, den_logo]],
        colWidths=[1.25*inch, 4*inch, 1.2*inch, 3*inch]
    )
    
    title_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))

    #put the header on the page for the den report
    denElements.append(title_table)
    denElements.append(Spacer(1, 12))

    #look up the adventures and scouts for the current rank
    current_reqs = {}
    scoutsWhoNeed = {}
    for adv in adventures[rank]:
        current_reqs[adv] = {}
        scoutsWhoNeed[adv] = {}
        for req in adventures[rank][adv]:
            current_reqs[adv][req] = 0
            scoutsWhoNeed[adv][req] = []
            
    current_scouts = scoutsByRank[rank]

    for scout in scout_reqs:
        #skip the kids who aren't in this rank
        if scout not in current_scouts:
            continue
        scout_data = scout_reqs[scout]  
        for adv in scout_data:
            for req in scout_data[adv]:
                if scout_data[adv][req] == 'incomplete':
                    current_reqs[adv][req] += 1
                    scoutsWhoNeed[adv][req].append(scout)
                    
    sorted_current_reqs = sorted([(adv, req, count)
        for adv, reqs in current_reqs.items()
        for req, count in reqs.items()
    ],
    key=lambda x: x[2],
    reverse=True)
    
    # Build a list of rows for the table
    table_data = [["Adventure", "Req#", "Requirement Description", "Outstanding", "Scouts"]]    
    
    for (adventure, req_num, count) in sorted_current_reqs:
        if count == 0:
            continue #don't print requirements if everyone has completed them
        # Get requirement description from adventures JSON
        #description = adventures.get(adventure, {}).get(req_num, "")
        description = adventures[rank][adventure][req_num]
        adv_paragraph = Paragraph(adventure, styles["Normal"])
        desc_paragraph = Paragraph(description, styles["Normal"])
        needText = "<br/>".join(scoutsWhoNeed[adventure][req_num])
        need_list = Paragraph(needText, styles["Normal"])
        table_data.append([adv_paragraph, req_num, desc_paragraph, str(count), need_list])
    
    
    # Create Table
    table = Table(table_data, colWidths=[1.75*inch, .5*inch, 4.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Candarab"),
        ("FONTSIZE", (0,0), (-1,0), 12),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    
    denElements.append(table)
    

    # --- Page break ---
    denElements.append(PageBreak())

def addScoutReportPage(scout, denElements, styles, rank):
    #create a PDF for this scout's individual report card
    scoutdoc = SimpleDocTemplate(os.path.join(rank, scout+".pdf"), pagesize=letter)
    scoutElements = []
    
    '''title_text = f"{scout} Rank Advancement Report"
    
    denElements.append(Paragraph(title_text, styles["Title"]))
    denElements.append(Spacer(1, 0.3*inch))
    
    scoutElements.append(Paragraph(title_text, styles["Title"]))
    scoutElements.append(Spacer(1, 0.3*inch))
    '''
    #Logos to use
    main_logo = Image("logos" + os.sep + "Logo.png", width=1.0*inch, height=1.0*inch)
    den_logo = Image("logos" + os.sep + rank + ".png", width=1.0*inch, height=1.0*inch)

    #title and subtitles
    titlepara = Paragraph(f"{scout} Rank Advancement Report", styles["Title"])
      
    #put the header in a table
    title_table = Table(
        [[main_logo, titlepara, den_logo]],
        colWidths=[1.25*inch, 4.5*inch, 1.2*inch]
    )
    
    
    title_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))

    #put the header on the page for the den report
    denElements.append(title_table)
    denElements.append(Spacer(1, 12))
    scoutElements.append(title_table)
    scoutElements.append(Spacer(1, 12))




    
    # --- Bar chart for percent completion ---
    scout_data = scout_reqs[scout] 

   
    for ascout, pct in scout_completion:
        if ascout is not scout:
            continue
        # Simple horizontal bar chart using Drawing
        bar_width = 6*inch
        bar_height = 0.4*inch
        drawing = Drawing(bar_width, bar_height)
        
        # Background bar (grey)
        drawing.add(Rect(0, 0, bar_width, bar_height, fillColor=colors.lightgrey, strokeColor=colors.black))
        
        # Completed portion (green)
        completed_width = bar_width * (pct / 100)
        drawing.add(Rect(0, 0, completed_width, bar_height, fillColor=colors.green, strokeColor=None))
        
        # Percentage text
        drawing.add(String(bar_width/2, bar_height/2 - 4, f"{pct:.1f}% Complete", 
                           fontName="Candarab", fontSize=12, fillColor=colors.black, textAnchor="middle"))
        drawing.hAlign = "CENTER"
        denElements.append(drawing)
        denElements.append(Spacer(1, 0.3*inch))
        scoutElements.append(drawing)
        scoutElements.append(Spacer(1, 0.3*inch))
        break
    
    # --- Paragraph explaining outstanding items ---
    explanation = ("This scout still needs to complete the following items to earn their rank "
                       "by the end of the scouting year:")
    scoutElements.append(Paragraph(explanation, styles["Normal"]))
    scoutElements.append(Spacer(1, 0.2*inch))
    
    for adventure in scout_data:
        headerPrinted = False
        for req in scout_data[adventure]:
            if scout_data[adventure][req] == 'incomplete':
                if not headerPrinted:
                    # Adventure name as subheading
                    denElements.append(Spacer(1, 0.1*inch))
                    scoutElements.append(Spacer(1, 0.1*inch))
                    denElements.append(Paragraph(f"<b>{adventure}</b>", styles["Heading3"]))
                    scoutElements.append(Paragraph(f"<b>{adventure}</b>", styles["Heading3"]))
                    headerPrinted = True
                description = adventures[rank][adventure][req]
                denElements.append(Paragraph(f"{req}. {description}", styles["Normal"]))
                scoutElements.append(Paragraph(f"{req}. {description}", styles["Normal"]))
                denElements.append(Spacer(1, 0.05*inch))
                scoutElements.append(Spacer(1, 0.05*inch))
    
    # --- Page break ---
    denElements.append(PageBreak())
    
    #print the individual doc
    scoutdoc.build(scoutElements)
        

####main####
debugging = True
ranks = ["Lion", "Tiger", "Wolf", "Bear", "Webelos", "Arrow of Light"]
PACK_NUM = "1234"
PACK_OUTPUT_PDF = "Pack " + PACK_NUM + " Advancement Report.pdf"
DEN_OUTPUT_PDF = " Den Advancement Report.pdf"
CSV_FILE = "reportbuilder.csv"
JSON_FILE = "requirements.json"


#Sanitize the input file because internet advancement adds weird stuff
sanitizeinput(CSV_FILE)

#create the pack overview PDF
(packDoc, packElements, styles) = makePackPDF(PACK_OUTPUT_PDF)
makeTitlePage(packDoc, packElements, styles, "Pack Overview")



#build a roster of all the scouts sorted by rank
df = pd.read_csv(CSV_FILE, header=None) #read in the CSV file
scout_names = df.iloc[0].tolist()
scout_ranks = df.iloc[2].tolist()
scout_ranks_completed = df.iloc[1].tolist()

scoutsByRank = {rank: [] for rank in ranks}

for idx, (name, r) in enumerate(zip(scout_names, scout_ranks)):
    if r in scoutsByRank:
        scoutsByRank[r].append(name)
    else:
        completed_rank = scout_ranks_completed[idx]
        if completed_rank in scoutsByRank:
            scoutsByRank[completed_rank].append(name) 



#build a structure of all the rank requirements
with open(JSON_FILE) as f:
    adventures = json.load(f)

    
#create the structure that will hold the completed requirements
scout_reqs = createReqs()    
    
#parse the CSV to figure out who has completed each requirement
analyzeRequirements(scout_reqs)




scout_completion = [] #stores the percentage of rank scout has achieved
scout_completion = findCompletion(scout_reqs)



#for each rank
for rank in ranks:
    dbg("working on " + rank + " rank")
    reportname = rank + " " + DEN_OUTPUT_PDF
    
    #create the den report for the rank
    (denDoc, denElements) = makeDenPDF(reportname)
    makeTitlePage(denDoc, denElements, styles, rank + " Den Overview", True)
    
    #Make the overview for each den
    makeDenOverview(denElements, styles, packElements, rank)
    
    #add the requirements to the pack and den reports
    buildRequirementSnapshot(denElements, styles, rank)

    
    #create a folder for the den if it doesn't exist
    if not os.path.exists(rank):
        os.mkdir(rank)
    
    #output individual scout report cards
    for scout in scoutsByRank[rank]:
        addScoutReportPage(scout, denElements, styles, rank)
        
    #create the den report
    denDoc.build(denElements)
    
    #copy the den report file to the folder for the den
    shutil.copy(reportname, os.path.join(rank, reportname))

#print the finished pack PDF

packDoc.build(packElements)
