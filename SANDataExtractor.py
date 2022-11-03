import copy
import re

class Nom:
  pass

noms = []
patternArticle = "^\[\[Wookieepedia:Comprehensive article nominations/.*\]\]$"

f = open("source.txt", "r")
for x in f:
  #print(x)
  if re.search(patternArticle, x):
    currentNom = Nom()
    currentNom.article = re.findall(patternArticle, x)[0]
  elif "result" in x:
    currentNom.result = x
  elif "nominator" in x:
    currentNom.nominator = x
  elif "startdate" in x:
    currentNom.startdate = x
  elif "WPs" in x:
    currentNom.WPs = x
  elif "votes" in x:
    currentNom.votes = x
  elif "objectors" in x:
    currentNom.objectors = x
  elif "enddate" in x:
    currentNom.enddate = x
    noms.append(copy.deepcopy(currentNom))
f.close()

f = open("result.txt", "a")
for x in noms:
    print(x.article.rstrip() + ", " +
    x.result + ", " +
    x.nominator + ", " +
    x.startdate + ", " +
    x.WPs + ", " +
    x.votes + ", " +
    x.objectors + ", " +
    x.enddate)

    f.write(x.article.rstrip() + ", " +
    x.result.rstrip() + ", " +
    x.nominator.rstrip() + ", " +
    x.startdate.rstrip() + ", " +
    x.WPs.rstrip() + ", " +
    x.votes.rstrip() + ", " +
    x.objectors.rstrip() + ", " +
    x.enddate.rstrip() + "\n")
f.close()