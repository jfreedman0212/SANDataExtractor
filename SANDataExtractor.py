import copy
import re
from datetime import datetime

class Nom:
    def __init__(self):
        self.process = ""
        self.article = ""
        self.result = ""
        self.nominator = ""
        self.startdate = ""
        self.wordCountInitial = ""
        self.wordCountFinal = ""
        self.WPs = []
        self.votes = []
        self.objectors = []
        self.enddate = ""

spreadsheetConstant = 30
separator = "# "
sourceFile = "source.txt"
resultsFile = "result.txt"

lines = []
titleLines = []
noms = []

nomCounter = 0

titlesAtStartOfNoms = True
isNominatorSection = False
isSupportSection = False
isOpposeSection = False
inNomination = False

wikiDate = (
    r"\d* *(?:January|February|March|April|May|June|" +
    r"July|August|September|October|November|December) *\d*,? \d{4}"
)
dateFormat = "%d %B %Y"
dateFormatAlternate = "%B %d %Y"
patternUserLink = r"(?:\[\[|\{\{)User:"
patternNomTitle = (
    r"(^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$" +
    r"|^\[\[Wookieepedia:Good article nominations/.*\]\]$" +
    r"|^\[\[Wookieepedia:Featured article nominations/.*\]\]$)"
)
patternNomStart = "<div id=\"old-forum-warning\""
patternResultStart = (
    "^:''The following discussion is preserved " +
    r"as an archive of a \[\[Wookieepedia:"
)
patternResultEnd = r" article nomination\]\] that was '''.*'''."
patternResult = (
    "(" + patternResultStart + r"Comprehensive article nominations\|Comprehensive" +
    patternResultEnd +
    "|" + patternResultStart + r"Good articles\|Good" + # legacy structure
    patternResultEnd +
    "|" + patternResultStart + r"Good article nominations\|Good" +
    patternResultEnd +
    "|" + patternResultStart + r"Featured article nominations\|Featured" +
    patternResultEnd +
    ")"
)
patternNominator = r"^\*'''Nominated by''':.*$"
patternArchivalDate = r"^\*'''Date Archived''':.*$"
patternWordCountInitial = r"^\*'''Word count at nomination time''':.*$"
patternWordCountFinal = r"^\*'''Final word count''':.*$"
patternWPs = r"^\*'''WookieeProject \(optional\)''':.*$"
patternVotes = "^====Support====.*$"
patternComments = "^====Comments====.*$"
patternObjectors = "^====Object====.*$"
patternEnddate = r"^\**\{\{.*approved\|.*$"
patternNomEnd = r"\[\[Category:Archived nominations by "
WPlist = []
currentNom = Nom()

def fetchWPlist():
    with open("WPlist.txt", "r", encoding="utf8") as f:
        for x in f:
            x = x.rstrip("\n")
            WPlist.append(x.split(","))

def processNomTypeAndTitle(x):
    global currentNom
    global inNomination

    currentNom = Nom()
    inNomination = True

    # process nom SA process type
    if re.search("Wookieepedia:Comprehensive article nominations", x):
        currentNom.process = "CAN"
    elif re.search("Wookieepedia:Good article nominations", x):
        currentNom.process = "GAN"
    else:
        currentNom.process = "FAN"

    # process article title
    currentNom.article = re.sub(
        (
            r"(^\[\[Wookieepedia:Comprehensive article nominations/" +
            r"|^\[\[Wookieepedia:Good article nominations/" +
            r"|^\[\[Wookieepedia:Featured article nominations/" +
            r"|\]\])"
        ),
        "",
        x
    ).strip()

def processNomStart():
    global titlesAtStartOfNoms
    global nomCounter

    if titlesAtStartOfNoms:
        # check if this works
        if currentNom.article:
            pass
        else:
            titlesAtStartOfNoms = False
            for i,x in enumerate(lines, 1):
                if (
                re.search(r"^\[\[Category:Archived nominations", lines[-i]) or
                re.search(r"^Retrieving \d", lines[-i]) or
                re.search("</div>", lines[-i])
                ):
                    break
                titleLines.append(lines[-i].rstrip("\n"))
            nomCounter += 1
            processNomTypeAndTitle(titleLines[-nomCounter])
    else:
        nomCounter += 1
        processNomTypeAndTitle(titleLines[-nomCounter])

def processNomResult(x):
    if re.search("withdrawn", x):
        currentNom.result = "withdrawn"
    elif re.search("unsuccessful", x):
        currentNom.result = "unsuccessful"
    elif re.search("successful", x):
        currentNom.result = "successful"
    else:
        currentNom.result = "other"

def processNominatorAndStartDate(x):
    global isNominatorSection

    isNominatorSection = True

    # get the user input part of the nominator field
    # if it contains a link to a userpage
    if re.search(patternUserLink + r"[^\]\|\/]*", x):
        inputPart = re.sub(r"^\*'''Nominated by''':[^\[\{\/]*", "", x).strip()
    # if it doesn't
    else:
        inputPart = re.sub(r"^\*'''Nominated by''': *", "", x).strip()

    processNominator(inputPart)

    # process start date
    dateFormatCurrent = dateFormat

    if not re.search(
        (
            r"\d+ (?:January|February|March|April|May|June|" +
            r"July|August|September|October|November|December),? \d{4}"
        ),
        inputPart
    ):
        dateFormatCurrent = dateFormatAlternate
        print(
            "Alternate date format in byline signature on " +
            currentNom.process +
            ": " +
            currentNom.article
        )

    timestamp = re.findall(
        (
            r"\d{1,2}:\d{2},? " + wikiDate + r"[^0-9]*\(UTC\)"
        ),
        inputPart
    )[0]

    dateTime = re.sub(r"[^0-9]*\(UTC\)", "", timestamp)
    date = re.findall(wikiDate, dateTime)[0]

    # process date to the format used in spreadsheet
    dateSansComma = re.sub(",", "", date).strip()
    dateObject = datetime.strptime(dateSansComma, dateFormatCurrent)
    dateFinal = dateObject.strftime('%Y-%m-%d')
    dateTime = re.sub(date, "'" + dateFinal, dateTime)

    dateTime = re.sub(",", "#", dateTime)

    currentNom.startdate = dateTime

def processNominator(inputPart):
    try:
        # get a list of usernames linked in there
        userPages = re.findall(patternUserLink + r"[^\]\|\/]*", inputPart)

        # remove any duplicates
        userPages = list(dict.fromkeys(userPages))

        # trim the User: prefix
        i = 0
        while i < len(userPages):
            userPages[i] = re.sub(patternUserLink, "", userPages[i])
            i = i + 1

        userPages.sort()

        # concatenate co-nominator usernames
        currentNom.nominator += ", " + ", ".join(userPages)
    except IndexError:
        print(
            "Error in fetching username from byline signature on " +
            currentNom.process +
            ": " +
            currentNom.article
        )
        currentNom.nominator += ", " + inputPart

def processArchivalDate(x):
    currentNom.enddate = re.sub(r"^\*'''Word count at nomination time''': ", "", x).strip()
    currentNom.enddate = re.findall(
        r"\d{1,2}:\d{2},? " + wikiDate,
        currentNom.enddate
    )[0]

def processInitialWordCount(x):
    currentNom.wordCountInitial = re.sub(r"^\*'''Date Archived''': ", "", x).strip()
    currentNom.wordCountInitial = re.findall(
        r"\d+",
        currentNom.wordCountInitial
    )[0]

def processFinalWordCount(x):
    currentNom.wordCountFinal = re.sub(r"^\*'''Date Archived''': ", "", x).strip()
    currentNom.wordCountFinal = re.findall(
        r"\d+",
        currentNom.wordCountFinal
    )[0]

def processWPs(x):
    currentNom.WPs = []

    # trim field text, strip spaces, convert to uppercase
    WPfield = re.sub(
        r"^\*'''WookieeProject \(optional\)''':",
        "",
        x
    ).strip().upper()

    # traverse the list of WPs
    # and check if any of their names or redirects match the WP field
    for WookieeProject in WPlist:
        for WPname in WookieeProject:
            # prevent, e.g., "WP:NSW" being a match for "WP:N"
            # while at the same time allow for, e.g.,
            # "WP:AST" (unbracketed) at the end of the line
            if re.search(WPname.upper() + "($|[^a-zA-Z0-9])", WPfield):
                currentNom.WPs.append(
                    re.sub("Wookieepedia:WookieeProject ", "", WookieeProject[0])
                )
                break

def processOneVote(x):
    if isSupportSection:
        # omit struck votes
        if re.search("^#:<s>", x):
            pass

        # omit non-vote comments
        if re.search(r"^#(\*|:)", x):
            pass

        else:
            # fetch and save review panel vote tag if present
            if re.search(r"^# *(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x):
                currentNom.votes.append(
                    re.findall(r"^# *(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x)[0]
                )
            else:
                currentNom.votes.append("")

            # fetch and save usernames present on the vote line
            userPages = re.findall(patternUserLink + r"[^\]\|\/]*", x)

            # remove any duplicates
            userPages = list(dict.fromkeys(userPages))

            # trim the User: prefix
            i = 0
            while i < len(userPages):
                userPages[i] = re.sub(patternUserLink, "", userPages[i])
                i = i + 1

            userPages.sort()

            if len(userPages) > 1:
                # concatenate the usernames without checking for any duplicate votes
                currentNom.votes.append(", ".join(userPages))
            else:
                try:
                    # check for any duplicate votes
                    if userPages[0] in currentNom.votes:
                        # in case of duplicate vote,
                        # remove the already-added panel tag field
                        currentNom.votes.pop(-1)
                    else:
                        currentNom.votes.append(userPages[0])
                except IndexError:
                    print(
                        "Error in fetching username from vote " +
                        currentNom.process +
                        ": " +
                        currentNom.article
                    )
                    currentNom.votes.append("")

            # fetch and save the last year present on the vote line
            try:
                yearVote = re.findall(r"\d{4}", x)[-1]
            except IndexError:
                print(
                    "Error in fetching year from support vote signature on " +
                    currentNom.process +
                    ": " +
                    currentNom.article
                )
                yearVote = ""
            currentNom.votes.append(yearVote)

def endSupportSection():
    global isSupportSection
    global isOpposeSection

    isSupportSection = False
    isOpposeSection = True

    # pad the list with empty entries
    while 3 * spreadsheetConstant > len(currentNom.votes):
        currentNom.votes.append("")

def processEndDate(x):
    global isOpposeSection

    isOpposeSection = False
    currentNom.enddate = re.sub(r"(^.*approved\||[^0-9]*\(UTC\)|\}\})", "", x).strip()
    currentNom.enddate = re.findall(
        r"\d{1,2}:\d{2},? " + wikiDate,
        currentNom.enddate
    )[0]

    # process usernames in objections

    currentNom.objectors = []

def processObjector(x):
    namePart = re.findall(patternUserLink + r".*(\||\/)", x)[0]
    name = re.sub("(" + patternUserLink + r"|\|.*|\/.*)", "", namePart)
    currentNom.objectors.append(name)

def processNomEnd():
    global isOpposeSection
    global inNomination

    isOpposeSection = False

    if inNomination:
        # save end date if nom has been successful
        if currentNom.enddate:
            dateFormatCurrent = dateFormat
            
            # extract date from timestamp
            dateActual = re.findall(wikiDate, currentNom.enddate)[0]

            if not re.search(
                (
                    r"\d+ (?:January|February|March|April|May|June|" +
                    r"July|August|September|October|November|December),? \d{4}"
                ),
                dateActual
            ):
                dateFormatCurrent = dateFormatAlternate
                print(
                    "Alternate format for archival date on " +
                    currentNom.process +
                    ": " +
                    currentNom.article
                )

            # remove commas, such as between month and year
            dateCorrected = re.sub(",", "", dateActual).strip()

            # process date to the format used in spreadsheet
            dateObject = datetime.strptime(dateCorrected, dateFormatCurrent)
            dateFinal = dateObject.strftime('%Y-%m-%d')

            dateTime = re.sub(dateActual, "'" + dateFinal, currentNom.enddate)
            dateTime = re.sub(",", "#", dateTime, 1)

            currentNom.enddate = dateTime
        else:
            currentNom.enddate = "#"

        # remove duplicate usernames and
        # sort the list of usernames mentioned in objections alphabetically
        currentNom.objectors = list(dict.fromkeys(currentNom.objectors))
        currentNom.objectors.sort()

        # remove nominator from the above list
        if currentNom.nominator in currentNom.objectors:
            currentNom.objectors.remove(currentNom.nominator)

        # remove support voter names from the list
        for y in currentNom.votes:
            if y in currentNom.objectors:
                currentNom.objectors.remove(y)

        # pad the list with empty entries
        while spreadsheetConstant > len(currentNom.objectors):
            currentNom.objectors.append("")

        # save the data about the current nom
        noms.append(copy.deepcopy(currentNom))
        inNomination = False

def writeNomDataToFile():
    with open(resultsFile, "a", encoding="utf8") as f:
        for x in noms:
            f.write(
                x.nominator[2:] + separator +
                x.article + separator +
                "" + separator + # continuity
                x.process + separator +
                x.result + separator +
                x.startdate + separator +
                x.enddate + separator +
                x.wordCountInitial + separator +
                x.wordCountFinal + separator +
                "; ".join(x.WPs) + separator +
                "# ".join(x.votes) + separator +
                "# ".join(x.objectors) + "\n"
            )


fetchWPlist()

with open(sourceFile, "r", encoding="utf8") as f:
    for x in f:
        lines.append(x)

for line in lines:
    if re.search(patternNomTitle, line):
        processNomTypeAndTitle(line)

    elif re.search(patternNomStart, line):
        processNomStart()

    elif re.search(patternResult, line):
        processNomResult(line)

    elif re.search(patternNominator, line):
        processNominatorAndStartDate(line)

    elif re.search(patternArchivalDate, line):
        processArchivalDate(line)

    elif re.search(patternWordCountInitial, line):
        processInitialWordCount(line)

    elif re.search(patternWordCountFinal, line):
        processFinalWordCount(line)

    elif re.search(patternWPs, line):
        processWPs(line)

    elif re.search(patternVotes, line): # enter support votes section
        isNominatorSection = False
        isSupportSection = True

    elif re.search("^#", line): # process each vote
        processOneVote(line)

    elif re.search(patternObjectors, line):
        endSupportSection()

    elif re.search(patternComments, line):
        isOpposeSection = False

    elif re.search(patternEnddate, line):
        processEndDate(line)

    elif re.search(patternUserLink, line):
        if isNominatorSection:
            processNominator(line)
        elif isOpposeSection:
            processObjector(line)

    elif re.search(patternNomEnd, line):
        processNomEnd()

# output the nomination data as a txt (csv) file
writeNomDataToFile()
