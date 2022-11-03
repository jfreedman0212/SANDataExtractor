import copy
import re

class Nom:
  def __init__(self):
    self.article = ""
    self.result = ""
    self.nominator = ""
    self.WPs = ""
    self.votes = ""
    self.objectors = ""
    self.enddate = ""

noms = []
patternArticle = "^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$"
patternResult = "^:''The following discussion is preserved as an archive of a \[\[Wookieepedia:Comprehensive article nominations\|Comprehensive article nomination\]\] that was '''.*'''."
patternNominator = "^\*'''Nominated by''': .*$"
patternWPs = "^\*'''WookieeProject \(optional\)''':.*$"
patternVotes = "^====Support====.*$"
patternObjectors = "^====Object====.*$"
patternEnddate = "^.*approved\|.*$"

f = open("source.txt", "r")
for x in f:
  #print(x)
  if re.search(patternArticle, x):
    currentNom = Nom()
    currentNom.article = re.findall(patternArticle, x)[0]
  elif re.search(patternResult, x):
    currentNom.result = re.findall(patternResult, x)[0]
  elif re.search(patternNominator, x):
    currentNom.nominator = re.findall(patternNominator, x)[0]
  elif re.search(patternWPs, x):
    currentNom.WPs = re.findall(patternWPs, x)[0]
  elif re.search(patternVotes, x):
    currentNom.votes = re.findall(patternVotes, x)[0]
  elif re.search(patternObjectors, x):
    currentNom.objectors = re.findall(patternObjectors, x)[0]
  elif re.search(patternEnddate, x):
    currentNom.enddate = re.findall(patternEnddate, x)[0]
    noms.append(copy.deepcopy(currentNom))
f.close()

f = open("result.txt", "a")
for x in noms:
    #change newlines to spaces
    f.write(x.article.rstrip() + ",\n" +
    x.result.rstrip() + ",\n" +
    x.nominator.rstrip() + ",\n" +
    x.WPs.rstrip() + ",\n" +
    x.votes.rstrip() + ",\n" +
    x.objectors.rstrip() + ",\n" +
    x.enddate.rstrip() + "\n")
f.close()