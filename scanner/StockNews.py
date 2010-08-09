from datetime import datetime
import feedparser
import re
import time

URLS = {
    'Yahoo': "http://finance.yahoo.com/rss/headline?s=",
    'Google': "http://www.google.com/finance/company_news?output=rss&q=",
    'MSN': "http://moneycentral.msn.com/community/rss/generate_feed.aspx?feedType=0&Symbol="
}

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2"

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

def get_sources():
    return URLS.keys()

def get_news(symbol):
    news = {}
    for source, url in URLS.items():
        news[source] = []
        feed = feedparser.parse(url + symbol)
        for entry in feed.entries:
            summary = entry.summary
            summary = summary.replace('\n', '')
            summary = summary.replace('\r', '')
            summary = summary.replace('\t', '')
            summary = HTML_TAGS.sub('', summary)
            summary = summary.encode('ascii', 'replace')
            if 'updated_parsed' in entry:
                pub_date = datetime(*entry.updated_parsed[:6])
                news[source].append(
                    {
                        'pub_date': pub_date,
                        'description': summary,
                        'title': entry.title.encode('ascii', 'replace'),
                        'link': entry.link,
                        'guid': entry.id,
                        }
                    )
    return news
