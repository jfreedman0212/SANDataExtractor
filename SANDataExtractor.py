import copy
import re
from datetime import datetime

class Nom:
  pass

noms = []
spreadsheetConstant = 30
isSupportSection = False
isOpposeSection = False
inNomination = False
separator = "# "

sourceFile = "ca_noms.txt"
resultsFile = "result.txt"
wikiDate = (
  "\d+ (?:January|February|March|April|May|June|" +
  "July|August|September|October|November|December),? \d\d\d\d"
)
patternArticle = (
  "(^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$" +
  "|^\[\[Wookieepedia:Good article nominations/.*\]\]$" +
  "|^\[\[Wookieepedia:Featured article nominations/.*\]\]$)"
)
patternResultStart = (
  "^:''The following discussion is preserved " +
  "as an archive of a \[\[Wookieepedia:"
)
patternResultEnd = " article nomination\]\] that was '''.*'''."
patternResult = (
  "(" + patternResultStart + "Comprehensive article nominations\|Comprehensive" +
  patternResultEnd +
  "|" + patternResultStart + "Good articles\|Good" + # legacy wording
  patternResultEnd +
  "|" + patternResultStart + "Good article nominations\|Good" +
  patternResultEnd +
  "|" + patternResultStart + "Featured article nominations\|Featured" +
  patternResultEnd +
  ")"
)
patternNominator = "^\*'''Nominated by''':.*$"
patternArchivalDate = "^\*'''Date Archived''':.*$"
patternWPs = "^\*'''WookieeProject \(optional\)''':.*$"
patternVotes = "^====Support====.*$"
patternComments = "^====Comments====.*$"
patternObjectors = "^====Object====.*$"
patternEnddate = "^\**\{\{.*approved\|.*$"
patternNomEnd = "\[\[Category:Archived nominations by "
WPlist = []

f = open("WPlist.txt", "r")
for x in f:
  x = x.rstrip("\n")
  WPlist.append(x.split(","))
f.close()

f = open(sourceFile, "r", encoding="utf8")
for x in f:

  # process nom SA process type and article title

  if re.search(patternArticle, x):
    currentNom = Nom()
    inNomination = True
    currentNom.WPs = []
    currentNom.objectors = []
    currentNom.enddate = ""

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
        "(^\[\[Wookieepedia:Comprehensive article nominations/" +
        "|^\[\[Wookieepedia:Good article nominations/" +
        "|^\[\[Wookieepedia:Featured article nominations/" +
        "|\]\])"
      ),
      "",
      x
    ).strip()


  # process nom result

  elif re.search(patternResult, x):
    if re.search("withdrawn", x):
      currentNom.result = "withdrawn"
    elif re.search("unsuccessful", x):
      currentNom.result = "unsuccessful"
    elif re.search("successful", x):
      currentNom.result = "successful"
    else:
      currentNom.result = "other"
    

  # process nominator name and nom start date

  elif re.search(patternNominator, x):
    # get the user input part of the nominator field
    # if it contains a link to a userpage
    if re.search("\[\[User:[^\]\|\/]*", x):
      inputPart = re.sub("^\*'''Nominated by''':[^\[]*", "", x).strip()
    # if it doesn't
    else:
      inputPart = re.sub("^\*'''Nominated by''': *", "", x).strip()

    try:
      # get a list of usernames linked in there
      userPages = re.findall("\[\[User:[^\]\|\/]*", inputPart)

      # remove any duplicates
      userPages = list(dict.fromkeys(userPages))

      # trim the User: prefix
      i = 0
      while i < len(userPages):
        userPages[i] = re.sub("\[\[User:", "", userPages[i])
        i = i + 1
      
      userPages.sort()

      # concatenate co-nominator usernames
      if len(userPages) > 1:
        currentNom.nominator = ", ".join(userPages)
      else:
        currentNom.nominator = userPages[0]
    except:
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
          "\d\d:\d\d, " + wikiDate + "[^0-9]*\(UTC\)"
        ),
        inputPart
      )[0]

      dateTime = re.sub("[^0-9]*\(UTC\)", "", timestamp)
      date = re.findall(wikiDate, dateTime)[0]

      # process date to the format used in spreadsheet
      dateSansComma = re.sub(",", "", date)
      dateObject = datetime.strptime(dateSansComma, "%d %B %Y")
      dateFinal = dateObject.strftime('%Y-%m-%d')

      dateTime = re.sub(date, "'" + dateFinal, dateTime)
      dateTime = re.sub(",", "#", dateTime)

      currentNom.startdate = dateTime

    except:
      print(
        "Error in fetching date from byline signature on " +
        currentNom.process +
        ": " +
        currentNom.article
      )

      wikiDateTemp = (
        "(?:January|February|March|April|May|June|" +
        "July|August|September|October|November|December) \d+,? \d\d\d\d"
      )
      
      timestamp = re.findall(
        (
          "\d\d:\d\d, " + wikiDateTemp + "[^0-9]*\(UTC\)"
        ),
        inputPart
      )[0]

      dateTime = re.sub("[^0-9]*\(UTC\)", "", timestamp)
      date = re.findall(wikiDateTemp, dateTime)[0]

      # process date to the format used in spreadsheet
      dateSansComma = re.sub(",", "", date)
      dateObject = datetime.strptime(dateSansComma, "%B %d %Y")
      dateFinal = dateObject.strftime('%Y-%m-%d')

      dateTime = re.sub(date, "'" + dateFinal, dateTime)
      dateTime = re.sub(",", "#", dateTime)

      currentNom.startdate = dateTime


  # process archival date if present

  elif re.search(patternArchivalDate, x):
    currentNom.enddate = re.sub("^\*'''Date Archived''': ", "", x).strip()
    currentNom.enddate = re.findall(
      "\d\d:\d\d, \d+ " +
      "(?:January|February|March|April|May|June|July|August|September|October|November|December),? \d\d\d\d",
      currentNom.enddate
    )[0]
  
  # process WPs

  elif re.search(patternWPs, x):
    currentNom.WPs = []
    
    # trim field text, strip spaces, convert to uppercase
    WPfield = re.sub(
      "^\*'''WookieeProject \(optional\)''':",
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


  # process support votes

  # initialize
  elif re.search(patternVotes, x):
    isSupportSection = True
    currentNom.votes = []

  # process each vote
  elif re.search("^#", x):
    if isSupportSection:
      # omit struck votes
      if re.search("^#:<s>", x):
        pass

      # omit non-vote comments
      if re.search("^#(\*|:)", x):
        pass

      else:
        # fetch and save review panel vote tag if present
        if re.search("^#(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x):
          currentNom.votes.append(
            re.findall("^#(\{\{Inq\}\}|\{\{AC\}\}|\{\{EC\}\})", x)[0]
          )
        else:
          currentNom.votes.append("")
        
        # fetch and save usernames present on the vote line
        userPages = re.findall("\[\[User:[^\]\|\/]*", x)

        # remove any duplicates
        userPages = list(dict.fromkeys(userPages))

        # trim the User: prefix
        i = 0
        while i < len(userPages):
          userPages[i] = re.sub("\[\[User:", "", userPages[i])
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
          yearVote = re.findall("\d\d\d\d", x)[-1]
        except:
          print(
            "Error in fetching year from support vote signature on " +
            currentNom.process +
            ": " +
            currentNom.article
          )
          yearVote = ""
        currentNom.votes.append(yearVote)

  # wrap up with support votes
  elif re.search(patternObjectors, x):
    isSupportSection = False
    isOpposeSection = True

    # pad the list with empty entries
    while 3 * spreadsheetConstant > len(currentNom.votes):
        currentNom.votes.append("")


  # check for Comments section
  elif re.search(patternComments, x):
    isOpposeSection = False


  # fetch nom end date, if present

  elif re.search(patternEnddate, x):
    isOpposeSection = False
    currentNom.enddate = re.sub("(^.*approved\||[^0-9]*\(UTC\)|\}\})", "", x).strip()
    currentNom.enddate = re.findall("\d\d:\d\d, \d+ (?:January|February|March|April|May|June|July|August|September|October|November|December),? \d\d\d\d", currentNom.enddate)[0]


  # process usernames in objections

    currentNom.objectors = []

  elif re.search("\[\[User:", x):
    if isOpposeSection:
      namePart = re.findall("\[\[User:.*\|", x)[0]
      name = re.sub("(\[\[User:|\|.*)", "", namePart)
      currentNom.objectors.append(name)


  #wrap up with usernames in objections

  elif re.search(patternNomEnd, x):  
    isOpposeSection = False

    if inNomination == True:
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
f.close()


# output the nomination data as a txt (csv) file

f = open(resultsFile, "a", encoding="utf8")

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

f.close()