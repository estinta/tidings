from datetime import datetime
import feedparser
import re
import time

RSS_URLS = {
    'yahoo': "http://finance.yahoo.com/rss/headline?s=",
    'google': "http://www.google.com/finance/company_news?output=rss&q=",
    'msn': "http://moneycentral.msn.com/community/rss/generate_feed.aspx?feedType=0&Symbol="
}

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.10) Gecko/20100928 Firefox/3.6.10"

HEADERS={'User-Agent': USER_AGENT}

HTML_TAGS = re.compile('<.*?>')

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

# vim: set ts=4 sw=4 et:
