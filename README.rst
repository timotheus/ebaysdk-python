Welcome to the python ebaysdk
=============================

This SDK is a programmatic interface into the eBay APIs. It simplifies development and cuts development time by standardizing calls, response processing, error handling, and debugging across the Finding, Shopping, Merchandising & Trading APIs. 

Quick Example::

    import datetime
    from lxml.etree import _Element
    from ebaysdk.finding import Connection

    try:
        api = Connection(appid='YOUR_APPID_HERE')
        response = api.execute('findItemsAdvanced', {'keywords': 'legos'})        

        assert(response.reply.ack == 'Success')  
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)
  
        item = response.reply.searchResult.item[0]
        assert(type(item.listingInfo.endTime) == datetime.datetime)
        assert(type(response.dict()) == dict)
        assert(type(response.dom() == _Element))

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


Migrating from v1 to v2
-----------------------

For a complete guide on migrating from ebaysdk v1 to v2 and see an overview of the additional features in v2 please read the `v1 to v2 guide`_


Getting Started
---------------

1) SDK Classes

* `Trading API Class`_ - secure, authenticated access to private eBay data.
* `Finding API Class`_ - access eBay's next generation search capabilities.
* `Shopping API Class`_ - performance-optimized, lightweight APIs for accessing public eBay data.
* `Merchandising API Class`_ - find items and products on eBay that provide good value or are otherwise popular with eBay buyers.
* `HTTP Class`_ - generic back-end class the enbles and standardized way to make API calls.
* `Parallel Class`_ - SDK support for concurrent API calls.

2) SDK Configuration

* `YAML Configuration`_ 
* `Understanding eBay Credentials`_

3) Sample code can be found in the `samples directory`_.

4) Understanding the `Request Dictionary`_.

Support
-------

For developer support regarding the SDK code base please use this project's `Github issue tracking`_.

For developer support regarding the eBay APIs please use the `eBay Developer Forums`_.

Install
-------

Installation instructions for *nix and windows can be found in the `INSTALL file`_.

License
-------

`COMMON DEVELOPMENT AND DISTRIBUTION LICENSE`_ Version 1.0 (CDDL-1.0)


.. _INSTALL file: https://github.com/timotheus/ebaysdk-python/blob/master/INSTALL
.. _COMMON DEVELOPMENT AND DISTRIBUTION LICENSE: http://opensource.org/licenses/CDDL-1.0
.. _Understanding eBay Credentials: https://github.com/timotheus/ebaysdk-python/wiki/eBay-Credentials
.. _eBay Developer Site: http://developer.ebay.com/
.. _YAML Configuration: https://github.com/timotheus/ebaysdk-python/wiki/YAML-Configuration
.. _Trading API Class: https://github.com/timotheus/ebaysdk-python/wiki/Trading-API-Class
.. _Finding API Class: https://github.com/timotheus/ebaysdk-python/wiki/Finding-API-Class
.. _Shopping API Class: https://github.com/timotheus/ebaysdk-python/wiki/Shopping-API-Class
.. _Merchandising API Class: https://github.com/timotheus/ebaysdk-python/wiki/Merchandising-API-Class
.. _HTTP Class: https://github.com/timotheus/ebaysdk-python/wiki/HTTP-Class
.. _Parallel Class: https://github.com/timotheus/ebaysdk-python/wiki/Parallel-Class
.. _eBay Developer Forums: https://go.developer.ebay.com/developers/ebay/forums-support/support
.. _Github issue tracking: https://github.com/timotheus/ebaysdk-python/issues
.. _v1 to v2 guide: https://github.com/timotheus/ebaysdk-python/wiki/Migrating-from-v1-to-v2 
.. _samples directory: https://github.com/timotheus/ebaysdk-python/tree/master/samples
.. _Request Dictionary: https://github.com/timotheus/ebaysdk-python/wiki/Request-Dictionary
