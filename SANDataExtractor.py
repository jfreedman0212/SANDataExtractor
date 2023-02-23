import copy
import re
from datetime import datetime

class Nom:
  pass

noms = []
spreadsheetConstant = 30
isSupportSection = False
isOpposeSection = False
separator = "# "

sourceFile = "ca_nom_archive_2022.txt"
resultsFile = "result.txt"
wikiDate = (
  "\d+ (?:January|February|March|April|May|June|" +
  "July|August|September|October|November|December) \d\d\d\d"
)
patternArticle = (
  "(^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$" +
  "|^\[\[Wookieepedia:Good article nominations/.*\]\]$" +
  "|^\[\[Wookieepedia:Featured article nominations/.*\]\]$)"
)
patternResult = (
  "(^:''The following discussion is preserved as an archive " +
  "of a \[\[Wookieepedia:Comprehensive article nominations\|Comprehensive " +
  "article nomination\]\] that was '''.*'''." +
  "|^:''The following discussion is preserved as an archive of a " +
  "\[\[Wookieepedia:Good articles\|Good article nomination\]\] " +
  "that was '''.*'''." +
  "|^:''The following discussion is preserved as an archive of a " +
  "\[\[Wookieepedia:Featured article nominations\|Featured article nomination\]\]" +
  " that was '''.*'''.)"
)
patternNominator = "^\*'''Nominated by''':.*$"
patternWPs = "^\*'''WookieeProject \(optional\)''':.*$"
patternVotes = "^====Support====.*$"
patternComments = "^====Comments====.*$"
patternObjectors = "^====Object====.*$"
patternEnddate = "^\**\{\{.*approved\|.*$"
patternNomEnd = "\[\[Category:Archived nominations by "
WPlist = [["Wookieepedia:WookieeProject Aliens",
"WP:ALIENS",
"WP:Aliens",
"WP:AS",
"WookieeProject Aliens"],
["Wookieepedia:WookieeProject Ambition",
"WP:AMB",
"WP:AMBITION",
"WP:Ambition",
"WookieeProject Ambition"],
["Wookieepedia:WookieeProject Astrography",
"WP:AST",
"WP:ASTROGRAPHY",
"WP:Astrography",
"WP:ASTRO",
"WP:Astro",
"WookieeProject Astrography"],
["Wookieepedia:WookieeProject Atlas",
"WP:Atlas",
"WP:ATLAS",
"WP:EA",
"WP:TEA",
"WookieeProject Atlas"],
["Wookieepedia:WookieeProject Battlefront",
"WP:Battlefront",
"WP:BATTLEFRONT",
"WP:BF",
"WP:SWBF",
"WookieeProject Battlefront"],
["Wookieepedia:WookieeProject Chiss",
"WP:Chiss",
"WP:CHISS",
"WP:Zahn",
"WookieeProject Chiss"],
["Wookieepedia:WookieeProject Collaboration",
"WP:COLLABORATION",
"WP:Collaboration",
"WookieeProject Collaboration"],
["Wookieepedia:WookieeProject Comics",
"WP:CO",
"WP:COMICS",
"WP:Comics",
"WookieeProject Comics"],
["Wookieepedia:WookieeProject Creators",
"WP:CREA",
"WP:CREATORS",
"WP:Creators",
"WookieeProject Creators"],
["Wookieepedia:WookieeProject Data Seekers",
"WP:DS",
"WP:Data Seekers",
"WookieeProject Data Seekers"],
["Wookieepedia:WookieeProject Durge's Lance",
"WP:CIS",
"WP:SEP",
"WP:Durge's Lance",
"WookieeProject Durge's Lance"],
["Wookieepedia:WookieeProject Entertainment and Culture",
"WP:ENT",
"WP:EAC",
"Wookieepedia:WookieeProject Entertainment",
"WP:Entertainment",
"WP:ENTERTAINMENT"
"WP:Entertainment and Culture",
"WookieeProject Entertainment and Culture"],
["Wookieepedia:WookieeProject Ewoks",
"WP:E",
"WP:Ewoks",
"WP:EWOKS",
"WookieeProject Ewoks"],
["Wookieepedia:WookieeProject Fantasy Flight Games",
"WP:FFGAMES",
"WP:FFG",
"WP:Fantasy Flight Games",
"WookieeProject Fantasy Flight Games"],
["Wookieepedia:WookieeProject Galaxies",
"WP:SWG",
"WP:Galaxies",
"WP:GALAXIES",
"WookieeProject Galaxies"],
["Wookieepedia:WookieeProject Galaxy's Edge",
"WP:GE",
"WP:Galaxy's Edge",
"WookieeProject Galaxy's Edge"],
["Wookieepedia:WookieeProject Knights of the Old Republic",
"WP:KOTOR",
"WP:KotOR",
"WP:Knights of the Old Republic",
"WookieeProject Knights of the Old Republic"],
["Wookieepedia:WookieeProject Legacy Era",
"WP:Legacy",
"WP:LEGACY"
"WP:LE",
"WP:Legacy Era",
"WookieeProject Legacy Era"],
["Wookieepedia:WookieeProject LEGO",
"WP:LEGO",
"WP:Lego",
"WookieeProject LEGO"],
["Wookieepedia:WookieeProject Mandalore",
"WP:MANDO",
"WP:Mando",
"WP:Mandalore",
"WP:MANDALORE",
"WookieeProject Mandalore"],
["Wookieepedia:WookieeProject Massive Damage",
"WP:MD",
"WP:Massive Damage",
"WookieeProject Massive Damage"],
["Wookieepedia:WookieeProject New Sith Wars",
"WP:NSW",
"WP:New Sith Wars",
"WookieeProject New Sith Wars"],
["Wookieepedia:WookieeProject Novels",
"WP:N",
"WP:NOV",
"WP:Novels",
"Wookieeproject: Novels",
"WP:NOVELS",
"WookieeProject Novels"],
["Wookieepedia:WookieeProject Pride",
"WP:PRIDE",
"WP:Pride",
"WookieeProject Pride"],
["Wookieepedia:WookieeProject Real World Music",
"WP:RWM",
"WP:Real World Music",
"WookieeProject Real World Music"],
["Wookieepedia:WookieeProject Rebels",
"WP:Rebels",
"WP:REBELS",
"WP:SWR",
"WookieeProject Rebels"],
["Wookieepedia:WookieeProject Resistance",
"WP:Resistance",
"WookieeProject: Resistance",
"WookieeProject Resistance",
"WP:RESISTANCE"],
["Wookieepedia:WookieeProject Star Wars: Card Trader",
"WP:SWCT",
"WP:Card Trader",
"WookieeProject Star Wars: Card Trader"],
["Wookieepedia:WookieeProject Tales of the Jedi",
"WP:TOTJ",
"WP:Totj",
"WP:TotJ",
"WP:Tales of the Jedi",
"WookieeProject Tales of the Jedi"],
["Wookieepedia:WookieeProject The Clone Wars",
"WP:TCW",
"WP:The Clone Wars",
"WookieeProject The Clone Wars"],
["Wookieepedia:WookieeProject The Force Unleashed",
"WP:TFU",
"WP:The Force Unleashed",
"WookieeProject The Force Unleashed"],
["Wookieepedia:WookieeProject The High Republic",
"WP:THR",
"WP:The High Republic",
"WookieeProject The High Republic"],
["Wookieepedia:WookieeProject The Mandalorian",
"WP:TMND",
"WP:The Mandalorian",
"WP:Mandalorian",
"WP:MANDALORIAN",
"WookieeProject The Mandalorian"],
["Wookieepedia:WookieeProject The New Essential Guide to Characters",
"WP:NEGTC",
"WookieeProject The New Essential Guide to Characters"],
["Wookieepedia:WookieeProject The New Jedi Order",
"WP:NJO",
"WP:TNJO",
"WP:The New Jedi Order",
"WookieeProject The New Jedi Order"],
["Wookieepedia:WookieeProject The Old Republic",
"WP:TOR",
"WP:SWTOR",
"WP:The Old Republic",
"WookieeProject The Old Republic"],
["Wookieepedia:WookieeProject Video Games",
"WP:VG",
"WP:Video Games",
"WP:Video games",
"WookieeProject Video Games"],
["Wookieepedia:WookieeProject Warfare",
"WP:Warfare",
"WP:EGTW",
"WP:TEGTW",
"WP:EGtW",
"WP:TEGtW",
"WookieeProject Warfare"],
["Wookieepedia:WookieeProject Women",
"WP:WOMEN",
"WP:Women",
"WookieeProject Women"]
]

f = open(sourceFile, "r", encoding="utf8")
for x in f:

  # process nom SA process type and article title

  if re.search(patternArticle, x):
    currentNom = Nom()
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
    currentNom.result = re.sub(
      (
        "(" +
        "^:''The following discussion is preserved as an archive of a " +
        "\[\[Wookieepedia:Comprehensive article nominations\|Comprehensive " +
        "article nomination\]\] that was '''" +
        "|'''\. <span style=\"color: red;\">" +
        "'''Please do not modify it.'''<\/span>\[\[Category:Wookieepedia " +
        "Comprehensive article nomination pages archive\|\{\{SUBPAGENAME\}\}\]\]" +
        "|^:''The following discussion is preserved as an archive of a " +
        "\[\[Wookieepedia:Good article nominations\|Good " +
        "article nomination\]\] that was '''" +
        "|^:''The following discussion is preserved as an archive of a " +
        "\[\[Wookieepedia:Good articles\|Good " +
        "article nomination\]\] that was '''" +
        "|'''\. <span style=\"color: red;\">" +
        "'''Please do not modify it.'''<\/span>\[\[Category:Wookieepedia " +
        "Good article nomination pages archive\|\{\{SUBPAGENAME\}\}\]\]" +
        "|^:''The following discussion is preserved as an archive of a " +
        "\[\[Wookieepedia:Featured article nominations\|Featured " +
        "article nomination\]\] that was '''" +
        "|'''\. <span style=\"color: red;\">" +
        "'''Please do not modify it.'''<\/span>\[\[Category:Wookieepedia " +
        "Featured article nomination pages archive\|\{\{SUBPAGENAME\}\}\]\]" +
        "|'''. <span style=\"color: red;\">" +
        "'''Please do not modify it.'''<\/span>\{\{SpecialCategorizer\|" +
        "\[\[Category:Wookieepedia Featured article nomination pages archive" +
        "\|\{\{SUBPAGENAME\}\}\]\]\}\}"
        ")"
      ),
      "",
      x
    ).strip()


  # process nominator name and nom start date

  elif re.search(patternNominator, x):
    # get the user input part of the nominator field
    string = re.sub("^\*'''Nominated by''':[^\[]*", "", x).strip()

    # get a list of usernames linked in there
    userPages = re.findall("\[\[User:[^\]\|\/]*", string)

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

    # process start date
    datePart = re.findall(
      (
        "\d\d:\d\d, " + wikiDate + " \(UTC\)"
      ),
      string
    )[0]

    dateTime = re.sub(" \(UTC\)", "", datePart)
    dateTime = re.sub(",", "#", dateTime)

    # process date to the format used in spreadsheet
    date = re.findall(wikiDate, dateTime)[0]
    dateObject = datetime.strptime(date, "%d %B %Y")
    dateFinal = dateObject.strftime('%Y-%m-%d')
    dateTime = re.sub(date, "'" + dateFinal, dateTime)

    currentNom.startdate = dateTime


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
        yearVote = re.findall("\d\d\d\d", x)[-1]
        currentNom.votes.append(yearVote)

  # wrap up with support votes
  elif re.search(patternObjectors, x):
    isSupportSection = False
    isOpposeSection = True

    # pad the list with empty entries
    while 3 * spreadsheetConstant > len(currentNom.votes):
        currentNom.votes.append("")


  # process usernames in objections

    currentNom.objectors = []

  elif re.search("\[\[User:", x):
    if isOpposeSection:
      namePart = re.findall("\[\[User:.*\|", x)[0]
      name = re.sub("(\[\[User:|\|.*)", "", namePart)
      currentNom.objectors.append(name)


  # fetch nom end date

  elif re.search(patternEnddate, x):
    currentNom.enddate = re.sub("(^.*approved\|| \(UTC\)|\}\})", "", x).strip()


  #wrap up with usernames in objections

  elif re.search(patternNomEnd, x):  
    isOpposeSection = False

    # save nom end date
    if currentNom.enddate:
      dateTime = re.sub(",", "#", currentNom.enddate)

      # process date to the format used in spreadsheet
      date = re.findall(wikiDate, dateTime)[0]
      dateObject = datetime.strptime(date, "%d %B %Y")
      dateFinal = dateObject.strftime('%Y-%m-%d')
      dateTime = re.sub(date, "'" + dateFinal, dateTime)

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