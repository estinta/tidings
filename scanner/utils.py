import cookielib
from datetime import datetime, timedelta
import feedparser
import lxml.etree
import lxml.html
import re
import time
import urllib2

from django.db.models import Q
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlencode
from .models import News, Stock

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


def validate_credentials(profile, save=True):
    df = DataFetcher(profile)
    try:
        if not profile.ibd_user or not profile.ibd_password:
            success = None
        else:
            try:
                success = df.ibd_login()
                if success:
                    stock = Stock(ticker='GOOG')
                    # if we don't get data back, we failed
                    if not df.ibd_retrieve_stock(stock):
                        success = False
            except Exception, e:
                success = False

        profile.ibd_valid = success

        if not profile.briefing_user or not profile.briefing_password:
            success = None
        else:
            success = df.briefing_login()
        profile.briefing_valid = success
    finally:
        df.destroy()

    if save:
        profile.save()

    return profile

class DataFetcher(object):

    user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.10) Gecko/20100928 Firefox/3.6.10"
    headers = {'User-Agent': user_agent}

    finviz_url = "http://finviz.com/quote.ashx?t="
    news_rss_urls = {
        'yahoo': "http://finance.yahoo.com/rss/headline?s=",
        'google': "http://www.google.com/finance/company_news?output=rss&q=",
        'msn': "http://moneycentral.msn.com/community/rss/generate_feed.aspx?feedType=0&Symbol="
    }

    ibd_company_group_re = re.compile('(.*) RANK WITHIN THE (.*) GROUP \(\d+ STOCKS\)')

    def __init__(self, profile):
        self.profile = profile
        self._ibd_login = None
        self._briefing_login = None
        cookiejar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

    def ibd_login(self, force=False):
        # we cache this the first time it is called
        logged_in = getattr(self, '_ibd_login')
        if not force and logged_in is not None:
            return logged_in
        if not self.profile.ibd_user or not self.profile.ibd_password:
            self._ibd_login = False
        else:
            params = urlencode({
                'strEmail': self.profile.ibd_user,
                'strPassword': self.profile.ibd_password,
                'blnRemember': 'False'
            })
            ibd_login_url = "http://www.investors.com/Services/SiteAjaxService.asmx/MemberSingIn"
            req = urllib2.Request(ibd_login_url, params, headers=self.headers)
            try:
                response = self.opener.open(req)
                data = response.read()
                if "SOK" in data:
                    self._ibd_login = True
                else:
                    self._ibd_login = False
            except urllib2.URLError, e:
                print "ibd login failure", e
                self._ibd_login = False
        return self._ibd_login

    def ibd_logout(self):
        # currently no need to logout
        pass

    def briefing_login(self, force=False):
        # we cache this the first time it is called
        logged_in = getattr(self, '_briefing_login')
        if not force and logged_in is not None:
            return logged_in
        if not self.profile.briefing_user or \
                not self.profile.briefing_password:
            self._briefing_login = False
        else:
            login = self.briefing_do_login()
            print "first login attempt:", login
            if login and self.briefing_is_locked_out():
                print "locked out?", "yes"
                self.briefing_clear_session()
                login = self.briefing_do_login()
                print "second login attempt:", login
                if login:
                    login = not self.briefing_is_locked_out()
                    print "not locked out?", login
            self._briefing_login = login

        return self._briefing_login
 
    def briefing_do_login(self):
        params = urlencode({
            'DefaultPageSelect': '',
            'LoginButton': 'LogIn',
            'LoginButton.x': '26',
            'LoginButton.y': '11',
            'Password': self.profile.briefing_password,
            'SelectedDefaultPage': '-1',
            'UserName': self.profile.briefing_user,
            '__EVENTARGUMENT': '',
            '__EVENTTARGET': '',
            '__EVENTVALIDATION': '/wEWDQL6nYKAAgLP+tHIDAKvruq2CALSxeCRDwLXt5f5AQL26uXRCwLpudD/DgLk9sGoDgK5zubeAQLd2Z7uAQL3r4njCwKA1/KzDAL+jNCfDw==',
            '__VIEWSTATE': '/wEPDwUKLTMwNjc3NzM2N2QYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgQFClJlbWVtYmVyTWUFCUF1dG9Mb2dJbgUQRGVmYXVsdFN0YXJ0UGFnZQULTG9naW5CdXR0b24=',
        })
        headers = self.headers.copy()
        headers['Cookie'] = 'testcookie=test=test'
        briefing_login_url = 'https://www.briefing.com/login/LoginInPlayEq.aspx'
        req = urllib2.Request(briefing_login_url, params,
                headers=headers)
        try:
            response = self.opener.open(req)
            data = response.read()
        except urllib2.URLError, e:
            return False
        headers = response.info()
        # if we were successful, we will get a redirect in probably two ways
        if "Refresh" in headers or \
                "window.location.replace" in data:
            return True
        else:
            return False

    def briefing_is_locked_out(self):
        url = 'http://www.briefing.com/InPlayEq/InPlay/InPlay.htm'
        try:
            response = self.opener.open(url)
            data = response.read()
            if re.search(r'_concurrencyExceededDisplay', data):
                return True
            return False
        except urllib2.URLError, e:
            print "urlerror", e
            return None

    def briefing_clear_session(self):
        params = urlencode({
            '__EVENTARGUMENT': '',
            '__EVENTTARGET': '_deleteLiveSessions',
            '__EVENTVALIDATION': '/wEWAgLJ05bqAQKj+ZH5DA==',
            '__VIEWSTATE': '/wEPDwUKMTgwMzEzODM3MmRk',
        })
        concurrency_url = 'https://www.briefing.com/login/ConcurrencyExceededBriefingInPlay.aspx'
        try:
            response = self.opener.open(concurrency_url, params)
            data = response.read()
            return re.search(r'Your session has been successfully cleared', data)
        except urllib2.URLError, e:
            print "clear fail", e
            return False

    def briefing_logout(self):
        url = 'https://www.briefing.com/Login/LogoutInPlayEq.aspx'
        try:
            response = self.opener.open(url)
            data = response.read()
            return re.search(r'SUCCESSFULLY LOGGED OUT', data)
        except urllib2.URLError, e:
            return False

    def destroy(self):
        if self._ibd_login:
            self.ibd_logout()
        if self._briefing_login:
            self.briefing_logout()

    def update_finviz(self, stock):
        try:
            response = self.opener.open(self.finviz_url + stock.ticker)
        except urllib2.URLError:
            print "Could not connect to finviz"
            return stock
        doc = lxml.html.parse(response).getroot()
        try:
            value = doc.xpath("//td[.='Shs Float']/following-sibling::*[1]/b")[0].text
            stock.finviz_float = value
            stock.finviz_last_update = datetime.utcnow()
        except IndexError:
            # Element could not be found
            print "Finviz index error"
        return stock

    def update_ibd(self, stock):
        if not self.ibd_login():
            return stock
        try:
            stock_dict = self.ibd_retrieve_stock(stock)
        except Exception, e:
            print "could not fetch IBD data", e
            return stock
        if not stock_dict:
            return stock
        stock.ibd_industry_rank = stock_dict['industry_group_rank']
        stock.ibd_earnings_due_date = stock_dict['earnings_due_date']
        stock.company_name = stock_dict['company_name']
        stock.ibd_industry_group = stock_dict['industry_group']
        stock.ibd_earnings_percentage_lastquarter = stock_dict[
                'eps_perc_change']
        stock.ibd_sales_percentage_lastquarter = stock_dict[
                'sales_perc_change']
        stock.ibd_eps_rank = stock_dict['eps_rating']
        stock.ibd_last_update = datetime.utcnow()
        return stock

    def update_news(self, stock, force_news, news_date):
        news_items = []
        if force_news or stock.yahoo_last_update < news_date:
            news_items.extend(self.get_rss_news(stock, 'yahoo'))
            stock.yahoo_last_update = datetime.utcnow()
        if force_news or stock.google_last_update < news_date:
            news_items.extend(self.get_rss_news(stock, 'google'))
            stock.google_last_update = datetime.utcnow()
        if force_news or stock.msn_last_update < news_date:
            news_items.extend(self.get_rss_news(stock, 'msn'))
            stock.msn_last_update = datetime.utcnow()

        # Slightly hacky, but MySQL silently truncates our values otherwise
        # so we lose. This ensures we can do equality matching without any
        # problems.
        guid_len = News._meta.get_field('guid').max_length

        for item in news_items:
            guid = item['guid'][:guid_len]
            if News.objects.filter(stock=stock,
                    source=item['source'], guid=guid).exists():
                continue
            news = News()
            news.stock = stock
            for key, value in item.items():
                # description, title, link, pub_date, source, guid (overridden below)
                news.__setattr__(key, value)
            news.guid = guid
            news.save()

    def parse_investor_table(self, doc, title):
        '''Helper for tables that contain a
        <td><a..>{{title}}</a></td><td>{{value}}</td> structure.'''
        title_element = doc.xpath("//td[contains(a, '%s')]" % title)[0]
        if title_element is not None:
            return title_element.getnext().text.strip()
        return "N/A"

    def ibd_retrieve_stock(self, stock):
        '''This is the messy part. It parses the output using LXML and makes a
        dictionary of values of interest. If there is breakage, its probably in
        here.'''
        ibd_url = "http://www.investors.com/StockResearch/StockCheckup.aspx?symbol="
        req = urllib2.Request(ibd_url + stock.ticker, headers=self.headers)
        response = self.opener.open(req)
        if not response:
            return None

        parsed_data = {}
        doc = lxml.html.parse(response).getroot()
        company_group = doc.cssselect("#stock-checkup-group-performance strong")[0]
        company_group = company_group.text.strip()
        company_group_match = self.ibd_company_group_re.match(company_group)
        parsed_data['company_name'], parsed_data['industry_group'] = \
                company_group_match.groups()

        parsed_data['industry_group_rank'] = self.parse_investor_table(doc,
                'Industry Group Rank')

        parsed_data['earnings_due_date'] = self.parse_investor_table(doc,
                'EPS Due Date')

        parsed_data['eps_rating'] = self.parse_investor_table(doc, 'EPS Rating')

        parsed_data['eps_perc_change'] = self.parse_investor_table(doc, 
                'EPS % Chg (Last Qtr)')

        parsed_data['sales_perc_change'] = self.parse_investor_table(doc,
                'Sales % Chg (Last Qtr)')
        return parsed_data

    def get_rss_news(self, stock, source):
        news = []
        url = self.news_rss_urls[source]
        feed = feedparser.parse(url + stock.ticker)
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

    def update_briefing(self, stock):
        if not self.briefing_login():
            print "could not login to Briefing.com, skipping"
            return stock
        briefing_url = 'https://www.briefing.com/GeneralContent/InPlayEQ/Active/TickerSearch/TickerSearchInPlayEq.aspx?SearchTextBox='
        response = self.opener.open(briefing_url + stock.ticker)
        if not response:
            return stock

        # Slightly hacky, but MySQL silently truncates our values otherwise
        # so we lose. This ensures we can do equality matching without any
        # problems.
        guid_len = News._meta.get_field('guid').max_length

        response = response.read()
        data = unicode(response, 'utf8')
        doc = lxml.html.fromstring(data)
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

        try:
            # there should just be one
            news = doc.cssselect("table.search-results-lip")[0]
            for row in news.cssselect("tr"):
                cl = row.get("class")
                if cl and 'goldRowBold' in cl.split():
                    # skip the header row
                    continue
                date = row.xpath('td[1]/div/text()')[0]
                title_ele = row.cssselect("td.result-lip-article div.search-lip-title")
                title = lxml.etree.tostring(title_ele[0], encoding=unicode, method='text').strip()
                desc_ele = row.cssselect("td.result-lip-article div.search-lip-article")
                desc = lxml.etree.tostring(desc_ele[0], encoding=unicode, method='html').strip()

                guid = date + '::' + title
                guid = guid[:guid_len]
                if News.objects.filter(stock=stock,
                        source='briefing', guid=guid).exists():
                    continue
                # Yes, we will be storing these ones as ET
                date = time.strptime(date, '%d-%b-%y %H:%M ET')
                # convert from struct_time to datetime object
                date = datetime(*date[:6])
                news = News(source='briefing', stock=stock, guid=guid,
                        title=title, description=desc, pub_date=date)
                news.save()

            stock.briefing_last_update = datetime.utcnow()
        except IndexError, e:
            # Element could not be found. Not good, but better than throwing
            # a 500 back to the user because of it.
            print "Briefing index error"
            # Save the response if we need to do later debugging as to what
            # we actually got back
            output = open("/tmp/briefing_news.html", 'wb')
            output.write(data)
            output.close()

        return stock

    def fetch_all_data(self, tickers=None, force_finviz=False, force_ibd=False,
            force_news=False, force_briefing=False):
        qs = Stock.objects.all()
        if tickers != None:
            qs = qs.filter(ticker__in=tickers)

        finviz_date = datetime.utcnow() - timedelta(hours=24)
        ibd_date = datetime.utcnow() - timedelta(hours=1)
        news_date = datetime.utcnow() - timedelta(minutes=15)
        if  not (force_finviz or force_ibd or force_news or force_briefing):
            # fetch all stocks that may require updating
            qs = qs.filter(
                    Q(finviz_last_update__lt=finviz_date) |
                    Q(ibd_last_update__lt=ibd_date) |
                    Q(yahoo_last_update__lt=news_date) |
                    Q(google_last_update__lt=news_date) |
                    Q(msn_last_update__lt=news_date) |
                    Q(briefing_last_update__lt=news_date))

        for stock in qs:
            # first, get the Finviz data up to date
            if force_finviz or stock.finviz_last_update < finviz_date:
                self.update_finviz(stock)

            # next is IBD
            if self.profile.ibd_valid:
                if force_ibd or stock.ibd_last_update < ibd_date:
                    self.update_ibd(stock)

            # finally, news. force/date check handled internally
            self.update_news(stock, force_news, news_date)

            # briefing is a bit of a different beast
            if self.profile.briefing_valid:
                if force_briefing or stock.briefing_last_update < news_date:
                    self.update_briefing(stock)

            # save the darn thing
            stock.save()

# vim: set ts=4 sw=4 et:
