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
WPlist = [["Wookieepedia:WookieeProject Aliens", "WP:ALIENS", "WP:AS"], ["Wookieepedia:WookieeProject Ambition", "WP:AMB"], ["Wookieepedia:WookieeProject Astrography", "WP:AST"], ["Wookieepedia:WookieeProject Battlefront", "WP:Battlefront", "WP:BF", "WP:SWBF"], ["Wookieepedia:WookieeProject Chiss", "WP:Chiss", "WP:CHISS"], ["Wookieepedia:WookieeProject Comics", "WP:CO", "WP:COMICS"], ["Wookieepedia:WookieeProject Creators", "WP:CREA", "WP:CREATORS"], ["Wookieepedia:WookieeProject Data Seekers", "WP:DS"], ["Wookieepedia:WookieeProject Durge's Lance", "WP:CIS", "WP:SEP"], ["Wookieepedia:WookieeProject Entertainment and Culture", "WP:ENT", "WP:EAC", "Wookieepedia:WookieeProject Entertainment", "WP:Entertainment"], ["Wookieepedia:WookieeProject Ewoks", "WP:E", "WP:Ewoks", "WP:EWOKS"], ["Wookieepedia:WookieeProject Fantasy Flight Games", "WP:FFGAMES", "WP:FFG"], ["Wookieepedia:WookieeProject Galaxies", "WP:SWG"], ["Wookieepedia:WookieeProject Galaxy's Edge", "WP:GE"], ["Wookieepedia:WookieeProject Knights of the Old Republic", "WP:KOTOR"], ["Wookieepedia:WookieeProject Legacy's Era", "WP:Legacy", "WP:LE"], ["Wookieepedia:WookieeProject LEGO", "WP:LEGO"], ["Wookieepedia:WookieeProject New Sith Wars", "WP:NSW"], ["Wookieepedia:WookieeProject Novels", "WP:N", "WP:Novels", "Wookieeproject: Novels", "WP:NOVELS"], ["Wookieepedia:WookieeProject Pride", "WP:PRIDE", "WP:Pride"], ["Wookieepedia:WookieeProject Rebels", "WP:Rebels", "WP:REBELS", "WP:SWR"], ["Wookieepedia:WookieeProject Resistance", "WP:Resistance", "WookieeProject: Resistance"], ["Wookieepedia:WookieeProject Star Wars: Card Trader", "WP:SWCT"], ["Wookieepedia:WookieeProject Tales of the Jedi", "WP:TOTJ", "WP:Totj"], ["Wookieepedia:WookieeProject The Clone Wars", "WP:TCW", "WookieeProject The Clone Wars"], ["Wookieepedia:WookieeProject The High Republic", "WP:THR"], ["Wookieepedia:WookieeProject The Mandalorian", "WP:Mando", "WP:TMND"], ["Wookieepedia:WookieeProject The New Jedi Order", "WP:NJO"], ["Wookieepedia:WookieeProject The Old Republic", "WP:TOR"], ["Wookieepedia:WookieeProject Video Games", "WP:VG"], ["Wookieepedia:WookieeProject Warfare", "WP:Warfare"], ["Wookieepedia:WookieeProject Women", "WP:WOMEN", "WP:Women"]]

f = open("source.txt", "r")
for x in f:
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
    currentNom.WPs = []
    WPfield = re.sub("^\*'''WookieeProject \(optional\)''':", "", x).strip().upper()
    for WookieeProject in WPlist:
      for WPname in WookieeProject:
        if re.search(WPname.upper(), WPfield):
          currentNom.WPs.append(re.sub("Wookieepedia:WookieeProject ", "", WookieeProject[0]))
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
    ", ".join(x.WPs) + ",\n" +
    x.votes.rstrip() + ",\n" +
    x.objectors.rstrip() + ",\n" +
    x.enddate.rstrip() + ",\n")
f.close()