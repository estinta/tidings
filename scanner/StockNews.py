import feedparser
import re

URLS = {'Yahoo': "http://finance.yahoo.com/rss/headline?s=",
        'Google': "http://www.google.com/finance/company_news?output=rss&q=",
        'MSN': "http://moneycentral.msn.com/community/rss/generate_feed.aspx?feedType=0&Symbol="}
USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2"

HEADERS={'User-Agent': USER_AGENT}

HTML_TAGS = re.compile('<.*?>')

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
                pub_date = '%d/%d/%d' % (
                        entry.updated_parsed.tm_mon,
                        entry.updated_parsed.tm_mday,
                        entry.updated_parsed.tm_year)
                news[source].append(
                    {
                        'pub_date': pub_date,
                        'description': summary,
                        'title': entry.title.encode('ascii', 'replace'),
                        'link': entry.link,
                        }
                    )
    return news
