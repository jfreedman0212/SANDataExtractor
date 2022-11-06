import copy
import re

class Nom:
  pass

noms = []
patternArticle = "^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$"
patternResult = "^:''The following discussion is preserved as an archive of a \[\[Wookieepedia:Comprehensive article nominations\|Comprehensive article nomination\]\] that was '''.*'''."
patternNominator = "^\*'''Nominated by''':.*$"
patternWPs = "^\*'''WookieeProject \(optional\)''':.*$"
patternVotes = "^====Support====.*$"
patternObjectors = "^====Object====.*$"
patternEnddate = "^.*approved\|.*$"

f = open("source.txt", "r")
for x in f:
  #print(x)
  if re.search(patternArticle, x):
    currentNom = Nom()
    currentNom.article = re.sub("(^\[\[Wookieepedia:Comprehensive article nominations/|\]\])", "", x).strip()
  elif re.search(patternResult, x):
    currentNom.result = re.sub("(^:''The following discussion is preserved as an archive of a \[\[Wookieepedia:Comprehensive article nominations\|Comprehensive article nomination\]\] that was '''|\.|''')", "", x).strip()
  elif re.search(patternNominator, x):
    string = re.sub("^\*'''Nominated by''':[^\[]*", "", x).strip()
    namePart = re.findall("\[\[User:.*\|", string)[0]
    name = re.sub("(\[\[User:|\|.*)", "", namePart)
    datePart = re.findall("\d\d:\d\d, \d+ (?:January|February|March|April|May|June|July|August|September|October|November|December) \d\d\d\d \(UTC\)", string)[0]
    date = re.sub(" \(UTC\)", "", datePart)
    currentNom.nominator = name
    currentNom.startdate = date
  elif re.search(patternWPs, x):
    WPlist = re.sub("^\*'''WookieeProject \(optional\)''':", "", x).strip()
    WPs = re.findall("", WPlist)
    currentNom.WPs = WPlist
  elif re.search(patternVotes, x):
    currentNom.votes = re.findall(patternVotes, x)[0]
  elif re.search(patternObjectors, x):
    currentNom.objectors = re.findall(patternObjectors, x)[0]
  elif re.search(patternEnddate, x):
    currentNom.enddate = re.sub("(^.*approved\|| \(UTC\)|\}\})", "", x).strip()
    noms.append(copy.deepcopy(currentNom))
f.close()

f = open("result.txt", "a")
for x in noms:
    #change newlines to spaces
    f.write(x.article.rstrip() + ",\n" +
    x.result.rstrip() + ",\n" +
    x.nominator.rstrip() + ",\n" +
    x.startdate.rstrip() + ",\n" +
    x.WPs.rstrip() + ",\n" +
    x.votes.rstrip() + ",\n" +
    x.objectors.rstrip() + ",\n" +
    x.enddate.rstrip() + ",\n")
f.close()