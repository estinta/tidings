from datetime import datetime
import feedparser
import re
import time

RSS_URLS = {
    'yahoo': "http://finance.yahoo.com/rss/headline?s=",
    'google': "http://www.google.com/finance/company_news?output=rss&q=",
    'msn': "http://moneycentral.msn.com/community/rss/generate_feed.aspx?feedType=0&Symbol="
}

YAHOO_DATE = re.compile(r'([A-Za-z]{3}), (\d{,2}) ([A-Za-z]{3}) (\d{4}) (\d{,2}):(\d{2}):(\d{2}) Etc/GMT')

def yahoo_date_parser(date_string):
    '''They like inventing their own funky format, here it is:
    Mon, 21 Jun 2010 17:15:35 Etc/GMT
    '''
    dow, day, month, year, hour, minute, second = \
            YAHOO_DATE.search(date_string).groups()
    cleaned = "%d %s %d %d:%d:%d" % (int(day), month, int(year),
            int(hour), int(minute), int(second))
    t = time.strptime(cleaned, "%d %b %Y %H:%M:%S")
    return t
feedparser.registerDateHandler(yahoo_date_parser)

def get_news(symbol, source):
    if source in RSS_URLS:
        return get_rss_news(symbol, source)
    else:
        # TODO for briefing.com news
        return None

def get_rss_news(symbol, source):
    news = []
    url = RSS_URLS[source]
    feed = feedparser.parse(url + symbol)
    for entry in feed.entries:
        if 'updated_parsed' in entry:
            pub_date = datetime(*entry.updated_parsed[:6])
            news.append({
                'pub_date': pub_date,
                'description': entry.summary,
                'title': entry.title,
                'link': entry.link,
                'guid': entry.id,
                'source': source,
            })
    return news

def parse_briefing_news(response):
    if not response:
        return None
    parsed_data = {}
    doc = lxml.html.parse(response).getroot()
    # Here is what we are looking at finding in this document:
    # table.search-results-lip
    # tr.goldRowBold
    # << each article
    # tr
    # td (date, always first td element)
    # td....
    # td.result-lip-article
    #   div.search-lip-title (title)
    #   div.search-lip-article (description)
    # << end foreach

    # there should just be one
    news = doc.cssselect("table.search-results-lip")[0]
    for row in news.cssselect("tr"):
        cl = row.get("class")
        if cl and 'goldRowBold' in cl.split():
            # skip the header row
            continue
        date = row.xpath('td[1]/div/text()')[0]
        title_ele = row.cssselect("td.result-lip-article div.search-lip-title")
        title = etree.tostring(title_ele[0], encoding=unicode, method='text').strip()
        desc_ele = row.cssselect("td.result-lip-article div.search-lip-article")
        desc = etree.tostring(desc_ele[0], encoding=unicode, method='html').strip()
        print title, "::::", desc
    return None

# vim: set ts=4 sw=4 et:
