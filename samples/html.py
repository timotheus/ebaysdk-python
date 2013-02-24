import os, sys
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

    print "Intuit"
    print "------\n"

    for link in t[1::]:

        print link.findNext('a').findAll(text=True)[0]
        linkdict = dict((x, y) for x, y in link.findNext('a').attrs)
        print linkdict.get('href', '<no link>')


def _amazon(api):

    soup = api.response_soup()
    t = soup.findAll('a')

    print "Amazon"
    print "------\n"

    for link in t[1::2]:
        linkdict = dict((x, y) for x, y in link.attrs)
        print linkdict.get('title', '<notitle>')
        print linkdict.get('href', '<nolink>')

def _tivo(api):

    soup = api.response_soup()
    t = soup.findAll('dd', {'id': 'Marketing, Sales, Product Management'})
    
    links = t[0].findAll('a')

    print "Tivo"
    print "------\n"

    for link in links:

        linkdict = dict((x, y) for x, y in link.attrs)
        print link.findAll(text=True)[0]
        print "http://hire.jobvite.com/CompanyJobs/Careers.aspx?page=Job%%20Description&j=%s" % linkdict.get('href', '<nolink>').split("'")[-2]

def _mozilla(api):
    soup = api.response_soup()
    t = soup.findAll(text='Product Management') #td', {'class': 'iCIMS_JobsTableField_2'})
    print t

    print "Mozilla"
    print "------\n"

    #for link in t[1::2]:
    #    linkdict = dict((x, y) for x, y in link.attrs)
    #    print linkdict.get('title', '<notitle>')
    #    print linkdict.get('href', '<nolink>')

def run(opts):
    p = parallel()
    api1 = html(parallel=p, debug=opts.debug)
    api1.execute('http://jobs.intuit.com/search/advanced-search/ASCategory/Product%20Management/ASPostedDate/-1/ASCountry/-1/ASState/California/ASCity/-1/ASLocation/-1/ASCompanyName/-1/ASCustom1/-1/ASCustom2/-1/ASCustom3/-1/ASCustom4/-1/ASCustom5/-1/ASIsRadius/false/ASCityStateZipcode/-1/ASDistance/-1/ASLatitude/-1/ASLongitude/-1/ASDistanceType/-1')
    api2 = html(parallel=p, debug=opts.debug)
    api2.execute('https://highvolsubs-amazon.icims.com/jobs/search?ss=1&searchKeyword=&searchCategory=30651')
    api3 = html(parallel=p, debug=opts.debug)
    api3.execute('http://hire.jobvite.com/CompanyJobs/Careers.aspx?c=qMW9Vfww')
    api4 = html(parallel=p, debug=opts.debug)
    api4.execute('http://careers.mozilla.org/en-US/')
    p.wait()

    if p.error():
        raise(p.error())

    _intuit(api1)
    _amazon(api2)
    _tivo(api3)
    #_mozilla(api4)

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)

