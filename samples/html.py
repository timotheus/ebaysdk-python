import os, sys
import smtplib
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

import ebaysdk
from ebaysdk import html, parallel

def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")

    (opts, args) = parser.parse_args()
    return opts, args

def _intuit(api):

    soup = api.response_soup()
    t = soup.findAll('td', {'class': 'td1'})

    msg = []
    msg.append("\nIntuit")
    msg.append("-----------------------------")

    for link in t[1::]:
        msg.append(link.findNext('a').findAll(text=True)[0])
        linkdict = dict((x, y) for x, y in link.findNext('a').attrs)
        msg.append(linkdict.get('href', '<no link>'))
        msg.append("\n")

    return "\n".join(msg)

def _amazon(api):

    soup = api.response_soup()
    t = soup.findAll('a')

    msg = []
    msg.append("\nAmazon")
    msg.append("-----------------------------")

    for link in t[1::2]:
        linkdict = dict((x, y) for x, y in link.attrs)
        msg.append(linkdict.get('title', '<notitle>'))
        msg.append(linkdict.get('href', '<nolink>'))
        msg.append("\n")

    return "\n".join(msg)

def _tivo(api):

    soup = api.response_soup()
    t = soup.findAll('dd', {'id': 'Marketing, Sales, Product Management'})
    
    links = t[0].findAll('a')

    msg = []
    msg.append("\nTivo")
    msg.append("-----------------------------")

    for link in links:

        linkdict = dict((x, y) for x, y in link.attrs)
        msg.append(link.findAll(text=True)[0])
        msg.append("http://hire.jobvite.com/CompanyJobs/Careers.aspx?page=Job%%20Description&j=%s" % linkdict.get('href', '<nolink>').split("'")[-2])
        msg.append("\n")

    return "\n".join(msg)

def _oracle(api):

    soup = api.response_soup()
    #print soup
    #return ""

    rows = soup.findAll('table', {'class': 'x1h'})
    print rows[0].findAll('a')

    for row in rows:
        print row

    msg = []
    msg.append("\Oracle")
    msg.append("-----------------------------")
    '''
    for link in links:

        linkdict = dict((x, y) for x, y in link.attrs)
        msg.append(link.findAll(text=True)[0])
        msg.append("http://hire.jobvite.com/CompanyJobs/Careers.aspx?page=Job%%20Description&j=%s" % linkdict.get('href', '<nolink>').split("'")[-2])
        msg.append("\n")
    '''
    return "\n".join(msg)
    

def _ebay(api):

    soup = api.response_soup()
    t = soup.findAll('td', {'class': 'td1'})

    msg = []
    msg.append("\neBay")
    msg.append("-----------------------------")

    for link in t[1::]:
        msg.append(link.findNext('a').findAll(text=True)[0])
        linkdict = dict((x, y) for x, y in link.findNext('a').attrs)
        msg.append(linkdict.get('href', '<no link>'))
        msg.append("\n")

    return "\n".join(msg)

def run(opts):
    p = parallel()
    api1 = html(parallel=p, debug=opts.debug)
    api1.execute('http://jobs.intuit.com/search/advanced-search/ASCategory/Product%20Management/ASPostedDate/-1/ASCountry/-1/ASState/California/ASCity/-1/ASLocation/-1/ASCompanyName/-1/ASCustom1/-1/ASCustom2/-1/ASCustom3/-1/ASCustom4/-1/ASCustom5/-1/ASIsRadius/false/ASCityStateZipcode/-1/ASDistance/-1/ASLatitude/-1/ASLongitude/-1/ASDistanceType/-1')
    api2 = html(parallel=p, debug=opts.debug)
    api2.execute('https://highvolsubs-amazon.icims.com/jobs/search?ss=1&searchKeyword=&searchCategory=30651')
    api3 = html(parallel=p, debug=opts.debug)
    api3.execute('http://hire.jobvite.com/CompanyJobs/Careers.aspx?c=qMW9Vfww')
    api4 = html(parallel=p, debug=opts.debug)
    api4.execute('http://jobs.ebaycareers.com/search/product-manager/ASCategory/Product%20Management/ASPostedDate/-1/ASCountry/-1/ASState/California/ASCity/-1/ASLocation/-1/ASCompanyName/-1/ASCustom1/-1/ASCustom2/-1/ASCustom3/-1/ASCustom4/-1/ASCustom5/-1/ASIsRadius/false/ASCityStateZipcode/-1/ASDistance/-1/ASLatitude/-1/ASLongitude/-1/ASDistanceType/-1')
    api5 = html(parallel=p, debug=opts.debug)
    api5.execute('https://irecruitment.oracle.com/OA_HTML/OA.jsp?page=/oracle/apps/irc/candidateSelfService/webui/VisJobSchPG&_ri=821&SeededSearchFlag=N&Contractor=Y&Employee=Y&OASF=IRC_VIS_JOB_SEARCH_PAGE&_ti=345582308&retainAM=Y&addBreadCrumb=N&oapc=4&oas=HfwdjxRAvk-kqRstV7E-tA..')
    p.wait()

    if p.error():
        raise(p.error())

    msg = [
        _intuit(api1),
        _amazon(api2),
        _tivo(api3),
        _ebay(api4),
        #_oracle(api5),
    ]

    msg.append("Other Job Boards\n")
    msg.append(
        "Mozilla Board:\nhttp://careers.mozilla.org/en-US/position/oUFGWfwV\n"
    )
    msg.append(
        "Oracle Board:\nhttps://irecruitment.oracle.com/OA_HTML/OA.jsp?page=/oracle/apps/irc/candidateSelfService/webui/VisJobSchPG&_ri=821&SeededSearchFlag=N&Contractor=Y&Employee=Y&OASF=IRC_VIS_JOB_SEARCH_PAGE&_ti=345582308&retainAM=Y&addBreadCrumb=N&oapc=4&oas=HfwdjxRAvk-kqRstV7E-tA..\n"
    )
    msg.append(
        "Amazon Board:\nhttps://www.a9.com/careers/?search_text=&group=Product%20Manager&type=\n"
    )
    msg.append(
        "Yelp Board:\nhttp://www.yelp.com/careers\n"
    )    
    msg.append(
        "Intel Board:\nhttp://www.intel.com/jobs/jobsearch/index_js.htm?Location=200000016&JobCategory=30160190084\n"
    )
    msg.append(
        "Electonic Arts:\nhttps://performancemanager4.successfactors.com/career?company=EA&career_ns=job_listing_summary&navBarLevel=JOB_SEARCH&_s.crb=hyfmSy2nuvCyziY826tSvCbNp08%3d\n"
    )    
    
    sess = smtplib.SMTP('smtp.gmail.com', 587)
    sess.starttls()
    sess.login('tkeefer@gmail.com', 'kum@@r')

    headers = [
        "Subject: Bright New Future",
        "MIME-Version: 1.0",
        "Content-Type: text/plain"
    ]
    
    headers = "\r\n".join(headers)
    body = "\n".join(msg)

    body = body.encode('utf-8')

    sess.sendmail('tkeefer@gmail.com', ['tkeefer@gmail.com', 'sdunavan@gmail.com'], "%s\r\n\r\n%s" %(headers, body))
    
    sess.quit()

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)

