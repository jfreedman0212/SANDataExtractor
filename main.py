import pywikibot
import mwparserfromhell
import re
from enum import StrEnum


class Continuity(StrEnum):
    CANON = 'canon'
    LEGENDS = 'legends'
    NON_CANON = 'non-canon'
    NON_LEGENDS = 'non-legends'
    OUT_OF_UNIVERSE = 'oou'


CANON_PARAMS = {
    'can',
}

OOU_CANON_PARAMS = {
    'dotj',
    'tor',
    'thr',
    'fotj',
    'rote',
    'aor',
    'tnr',
    'rofo',
    'cnjo'
}

LEGENDS_PARAMS = {
    'leg'
}

OOU_LEGENDS_PARAMS = {
    'pre',
    'btr',
    'old',
    'imp',
    'reb',
    'new',
    'njo',
    'lgc',
    'inf',
}

NON_CANON_PARAMS = {
    'noncanon',
    'ncc'
}

NON_LEGENDS_PARAMS = {
    'ncl'
}

OOU_PARAMS = {
    'real',
    'rwp',
    'rwm'
}


def retrieve_continuity_from_article(article_name):
    site = pywikibot.Site(user='jsfbot')
    page = pywikibot.Page(site, article_name)

    # sometimes the article name changes. follow the redirect if this happens
    if page.isRedirectPage():
        page = page.getRedirectTarget()

    # skip_style_tags=True is necessary because some Top tags have styling in
    # them. the parser will skip the Top tag in those cases w/o this attribute.
    wikicode = mwparserfromhell.parse(page.text, skip_style_tags=True)

    # The "Top" template on the wook contains a variety of info about the
    # article. Many of these "tags" can be used to infer the continuity
    # the article belongs to.
    top = None

    for template in wikicode.filter_templates():
        if template.name.strip() == 'Top':
            top = template
            break

    continuities = set()

    # just skip it if there's no continuities
    if top is None:
        print(f"{article_name} does not have a Top template.")
        return continuities

    if article_name.endswith('/Legends'):
        continuities.add(Continuity.LEGENDS)

    for kv_pair in top.params:
        # there are two types of paramters:
        #   1. flat values, e.g. {{foo|bar}}
        #   2. key-value pairs, e.g. {{foo|bar=baz}}
        # the first case is what we want, which is where showkey is False.
        if kv_pair.showkey:
            continue

        # additionally, the name field will be the index for those. the value
        # field is what actually contains the text we want
        param = str(kv_pair.value)

        if param in CANON_PARAMS:
            continuities.add(Continuity.CANON)

        if param in OOU_CANON_PARAMS:
            continuities.add(Continuity.CANON)
            continuities.add(Continuity.OUT_OF_UNIVERSE)

        if param in LEGENDS_PARAMS:
            continuities.add(Continuity.LEGENDS)

        if param in OOU_LEGENDS_PARAMS:
            continuities.add(Continuity.LEGENDS)
            continuities.add(Continuity.OUT_OF_UNIVERSE)

        if param in NON_CANON_PARAMS:
            continuities.add(Continuity.NON_CANON)

        if param in NON_LEGENDS_PARAMS:
            continuities.add(Continuity.NON_LEGENDS)

        if param in OOU_PARAMS:
            continuities.add(Continuity.OUT_OF_UNIVERSE)

    # if nothing, assume canon
    if len(continuities) == 0:
        continuities.add(Continuity.CANON)

    # can't be canon AND non-canon. non-canon overrides canon
    if Continuity.NON_CANON in continuities and Continuity.CANON in continuities:
        continuities.remove(Continuity.CANON)

    # non-legends overrides legends. if we find both, non-legends wins
    if Continuity.NON_LEGENDS in continuities and Continuity.LEGENDS in continuities:
        continuities.remove(Continuity.LEGENDS)

    return continuities


def get_article_from_status_article(status_article_name):
    article_name = status_article_name

    # for the most part, the nomination article name will match the
    # name for the article 1:1. However, sometimes the same article
    # is nominated multiple times. This means the name of the Status
    # Article will be something like: Original Article Name (second nomination)
    #
    # This will remove that and just leave the original article name
    match = re.search(r'\s+\((\w+\s+nomination)\)$', article_name)
    if match:
        start_index = match.span()[0]
        article_name = article_name[:start_index]

    return article_name

