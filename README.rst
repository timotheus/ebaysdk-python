
This code is in the process of migrating from google code to github. For now, please get the lastest code from google code,

http://code.google.com/p/ebay-sdk-python/


Welcome to the ebaysdk for Python
=================================

Welcome to the eBay SDK for Python. This SDK cuts development time and simplifies tasks like error handling and enables you to make Finding, Shopping, Merchandising, and Trading API calls. In Addition, the SDK comes with RSS and HTML back-end libraries.

In order to use eBay aspects of this utility you must first register with eBay to get your `eBay Developer Site`_ (see the ebay.yaml for a way to easily tie eBay credentials to the SDK) Finding Services.

Example::

    from ebaysdk import finding, nodeText

    f = finding()
    f.execute('findItemsAdvanced', {'keywords': 'shoes'})        

    dom    = f.response_dom()
    mydict = f.response_dict()
    myobj  = f.response_obj()

    print myobj.itemSearchURL

    # process the response via DOM
    items = dom.getElementsByTagName('item')

    for item in items:
      print nodeText(item.getElementsByTagName('title')[0])

.. _eBay Developer Site: http://developer.ebay.com/



