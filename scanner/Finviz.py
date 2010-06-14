import urllib2
import lxml.html

URL="http://finviz.com/quote.ashx?t="

def get_float(symbol):
    response = urllib2.urlopen(URL + symbol)
    doc = lxml.html.parse(response).getroot()
    try:
        return doc.xpath("//td[.='Shs Float']/following-sibling::*[1]/b")[0].text
    except IndexError: # Element could not be found
        return ''

