from django.conf import settings
from django.utils.http import urlencode

import urllib2
import cookielib
import lxml.html
import re
import datetime

LOGIN_URL = "http://www.investors.com/Services/SiteAjaxService.asmx/MemberSingIn"
URL = "http://www.investors.com/StockResearch/StockCheckup.aspx?symbol="

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.10) Gecko/20100928 Firefox/3.6.10"
HEADERS={'User-Agent': USER_AGENT}

COMPANY_GROUP_RE = re.compile('(.*) RANK WITHIN THE (.*) GROUP \(\d+ STOCKS\)')

def login(opener, username, password):
    req = urllib2.Request(LOGIN_URL,
            urlencode({'strEmail': username,
                'strPassword': password,
                'blnRemember': 'False'}), headers=HEADERS)
    try:
        response = opener.open(req)
        data = response.read()
    except urllib2.URLError, e:
        print "login", e
        return False
    # were we successful logging in?
    if "SOK" in data:
        return True
    return False

def get_stock(opener, symbol):
    req = urllib2.Request(URL + symbol, headers=HEADERS)
    try:
        response = opener.open(req)
        return response
    except urllib2.URLError, e:
        print "get_stock failed", e
        return None

def parse_investor_table(doc, title):
    '''Helper for tables that contain a
    <td><a..>{{title}}</a></td><td>{{value}}</td> structure.'''
    title_element = doc.xpath("//td[contains(a, '%s')]" % title)[0]
    if title_element is not None:
        return title_element.getnext().text.strip()
    return "N/A"

def parse_stock(response):
    '''This is the messy part. It parses the output using LXML and makes a
    dictionary of values of interest. If there is breakage, its probably in
    here.'''
    if not response:
        return None
    parsed_data = {}
    doc = lxml.html.parse(response).getroot()
    company_group = doc.cssselect("#stock-checkup-group-performance strong")[0]
    company_group = company_group.text.strip()
    company_group_match = COMPANY_GROUP_RE.match(company_group)
    parsed_data['company_name'], parsed_data['industry_group'] = \
            company_group_match.groups()

    parsed_data['industry_group_rank'] = parse_investor_table(doc,
            'Industry Group Rank')

    parsed_data['earnings_due_date'] = parse_investor_table(doc,
            'EPS Due Date')

    parsed_data['eps_rating'] = parse_investor_table(doc, 'EPS Rating')

    parsed_data['eps_perc_change'] = parse_investor_table(doc, 
            'EPS % Chg (Last Qtr)')

    parsed_data['sales_perc_change'] = parse_investor_table(doc,
            'Sales % Chg (Last Qtr)')
    return parsed_data
# vim: set ts=4 sw=4 et:
