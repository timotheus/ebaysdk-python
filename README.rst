Welcome to the python ebaysdk
=============================

This SDK is a programmatic interface into the eBay APIs. It simplifies development and cuts development time by standardizing calls, response processing, error handling, and debugging across the Finding, Shopping, Merchandising & Trading APIs. 

Quick Example::

    from ebaysdk.finding import Connection
    try:
        api = Connection(appid='YOUR_APPID_HERE')
        api.execute('findItemsAdvanced', {'keywords': 'shoes'})        

        print api.response_dict()
    except ConnectionError as e:
        raise e

Getting Started
---------------

SDK Classes

* `Trading API Class`_ - secure, authenticated access to private eBay data.
* `Finding API Class`_ - access eBay's next generation search capabilities.
* `Shopping API Class`_ - performance-optimized, lightweight APIs for accessing public eBay data.
* `Merchandising API Class`_ - find items and products on eBay that provide good value or are otherwise popular with eBay buyers.
* `HTML Class`_ - generic back-end class the enbles and standardized way to make API calls.
* `Parallel Class`_ - SDK support for concurrent API calls.

SDK Configuration

* `YAML Configuration`_ 
* `Understanding eBay Credentials`_


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
.. _HTML Class: https://github.com/timotheus/ebaysdk-python/wiki/HTML-Class
.. _Parallel Class: https://github.com/timotheus/ebaysdk-python/wiki/Parallel-Class
.. _eBay Developer Forums: https://www.x.com/developers/ebay/forums
.. _Github issue tracking: https://github.com/timotheus/ebaysdk-python/issues


