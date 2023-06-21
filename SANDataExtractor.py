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
        self.WPs = []
        self.votes = []
        self.objectors = []
        self.enddate = ""

noms = []
spreadsheetConstant = 30
separator = "# "
sourceFile = "ca_noms.txt"
resultsFile = "result.txt"

isSupportSection = False
isOpposeSection = False
inNomination = False

wikiDate = (
    r"\d+ (?:January|February|March|April|May|June|" +
    r"July|August|September|October|November|December),? \d\d\d\d"
)
patternArticle = (
    r"(^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$" +
    r"|^\[\[Wookieepedia:Good article nominations/.*\]\]$" +
    r"|^\[\[Wookieepedia:Featured article nominations/.*\]\]$)"
)
patternResultStart = (
    "^:''The following discussion is preserved " +
    r"as an archive of a \[\[Wookieepedia:"
)
patternResultEnd = r" article nomination\]\] that was '''.*'''."
patternResult = (
    "(" + patternResultStart + r"Comprehensive article nominations\|Comprehensive" +
    patternResultEnd +
    "|" + patternResultStart + r"Good articles\|Good" + # legacy wording
    patternResultEnd +
    "|" + patternResultStart + r"Good article nominations\|Good" +
    patternResultEnd +
    "|" + patternResultStart + r"Featured article nominations\|Featured" +
    patternResultEnd +
    ")"
)
patternNominator = r"^\*'''Nominated by''':.*$"
patternArchivalDate = r"^\*'''Date Archived''':.*$"
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
    # get the user input part of the nominator field
    # if it contains a link to a userpage
    if re.search(r"\[\[User:[^\]\|\/]*", x):
        inputPart = re.sub(r"^\*'''Nominated by''':[^\[]*", "", x).strip()
    # if it doesn't
    else:
        inputPart = re.sub(r"^\*'''Nominated by''': *", "", x).strip()

    try:
        # get a list of usernames linked in there
        userPages = re.findall(r"\[\[User:[^\]\|\/]*", inputPart)

        # remove any duplicates
        userPages = list(dict.fromkeys(userPages))

        # trim the User: prefix
        i = 0
        while i < len(userPages):
            userPages[i] = re.sub(r"\[\[User:", "", userPages[i])
            i = i + 1

        userPages.sort()

        # concatenate co-nominator usernames
        if len(userPages) > 1:
            currentNom.nominator = ", ".join(userPages)
        else:
            currentNom.nominator = userPages[0]
    except IndexError:
        print(
            "Error in fetching username from byline signature on " +
            currentNom.process +
            ": " +
            currentNom.article
        )
        currentNom.nominator = inputPart

    # process start date
    try:
        timestamp = re.findall(
            (
                r"\d\d:\d\d, " + wikiDate + r"[^0-9]*\(UTC\)"
            ),
            inputPart
        )[0]

        dateTime = re.sub(r"[^0-9]*\(UTC\)", "", timestamp)
        date = re.findall(wikiDate, dateTime)[0]

        # process date to the format used in spreadsheet
        dateSansComma = re.sub(",", "", date)
        dateObject = datetime.strptime(dateSansComma, "%d %B %Y")
        dateFinal = dateObject.strftime('%Y-%m-%d')

        dateTime = re.sub(date, "'" + dateFinal, dateTime)
        dateTime = re.sub(",", "#", dateTime)

        currentNom.startdate = dateTime

    except IndexError:
        print(
            "Error in fetching date from byline signature on " +
            currentNom.process +
            ": " +
            currentNom.article
        )

        wikiDateTemp = (
            "(?:January|February|March|April|May|June|" +
            r"July|August|September|October|November|December) \d+,? \d\d\d\d"
        )

        timestamp = re.findall(
            (
                r"\d\d:\d\d, " + wikiDateTemp + r"[^0-9]*\(UTC\)"
            ),
            inputPart
        )[0]

        dateTime = re.sub(r"[^0-9]*\(UTC\)", "", timestamp)
        date = re.findall(wikiDateTemp, dateTime)[0]

        # process date to the format used in spreadsheet
        dateSansComma = re.sub(",", "", date)
        dateObject = datetime.strptime(dateSansComma, "%B %d %Y")
        dateFinal = dateObject.strftime('%Y-%m-%d')

        dateTime = re.sub(date, "'" + dateFinal, dateTime)
        dateTime = re.sub(",", "#", dateTime)

        currentNom.startdate = dateTime

def processArchivalDate(x):
    currentNom.enddate = re.sub(r"^\*'''Date Archived''': ", "", x).strip()
    currentNom.enddate = re.findall(
        r"\d\d:\d\d, \d+ " +
        r"(?:January|February|March|April|May|June" +
        r"|July|August|September|October|November|December),? \d\d\d\d",
        currentNom.enddate
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
            if re.search(r"^#(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x):
                currentNom.votes.append(
                    re.findall(r"^#(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x)[0]
                )
            else:
                currentNom.votes.append("")

            # fetch and save usernames present on the vote line
            userPages = re.findall(r"\[\[User:[^\]\|\/]*", x)

            # remove any duplicates
            userPages = list(dict.fromkeys(userPages))

            # trim the User: prefix
            i = 0
            while i < len(userPages):
                userPages[i] = re.sub(r"\[\[User:", "", userPages[i])
                i = i + 1

            userPages.sort()

            if len(userPages) > 1:
                # concatenate the usernames without checking for any duplicate votes
                currentNom.votes.append(", ".join(userPages))
            else:
                # check for any duplicate votes
                if userPages[0] in currentNom.votes:
                    # in case of duplicate vote,
                    # remove the already-added panel tag field
                    currentNom.votes.pop(-1)
                else:
                    currentNom.votes.append(userPages[0])

            # fetch and save the last year present on the vote line
            try:
                yearVote = re.findall(r"\d\d\d\d", x)[-1]
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
        r"\d\d:\d\d, \d+ (?:January|February|March|April|May|June" +
        r"|July|August|September|October|November|December),? \d\d\d\d",
        currentNom.enddate
    )[0]

    # process usernames in objections

    currentNom.objectors = []

def processObjector(x):
    if isOpposeSection:
        namePart = re.findall(r"\[\[User:.*\|", x)[0]
        name = re.sub(r"(\[\[User:|\|.*)", "", namePart)
        currentNom.objectors.append(name)

def processNomEnd():
    global isOpposeSection
    global inNomination

    isOpposeSection = False

    if inNomination:
        # save end date if nom has been successful
        if currentNom.enddate:
            # extract date from timestamp
            dateActual = re.findall(wikiDate, currentNom.enddate)[0]

            # remove commas, such as between month and year
            dateCorrected = re.sub(",", "", dateActual)

            # process date to the format used in spreadsheet
            dateObject = datetime.strptime(dateCorrected, "%d %B %Y")
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
                x.nominator + separator +
                x.article + separator +
                "" + separator + # continuity
                x.process + separator +
                x.result + separator +
                x.startdate + separator +
                x.enddate + separator +
                "; ".join(x.WPs) + separator +
                "# ".join(x.votes) + separator +
                "# ".join(x.objectors) + "\n"
            )


fetchWPlist()

with open(sourceFile, "r", encoding="utf8") as f:
    for x in f:

        if re.search(patternArticle, x):
            processNomTypeAndTitle(x)

        elif re.search(patternResult, x):
            processNomResult(x)

        elif re.search(patternNominator, x):
            processNominatorAndStartDate(x)

        elif re.search(patternArchivalDate, x):
            processArchivalDate(x)

        elif re.search(patternWPs, x):
            processWPs(x)

        elif re.search(patternVotes, x): # enter support votes section
            isSupportSection = True

        elif re.search("^#", x): # process each vote
            processOneVote(x)

        elif re.search(patternObjectors, x):
            endSupportSection()

        elif re.search(patternComments, x):
            isOpposeSection = False

        elif re.search(patternEnddate, x):
            processEndDate(x)

        elif re.search(r"\[\[User:", x):
            processObjector(x)

        elif re.search(patternNomEnd, x):
            processNomEnd()

# output the nomination data as a txt (csv) file
writeNomDataToFile()
