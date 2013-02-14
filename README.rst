Welcome to the python ebaysdk
=============================

This SDK is a dead-simple, programatic inteface into the eBay APIs. It simplifies development and cuts development time by standerizing calls, response processing, error handling, debugging across the Finding, Shopping, Merchandising, & Trading APIs. 

Support ...TBD

Quick Example::

    from ebaysdk import finding

    api = finding(appid='YOUR_APPID_HERE')
    api.execute('findItemsAdvanced', {'keywords': 'shoes'})        

    print api.response_dict()

Getting Started
---------------

* `Trading API Class`_
* `Finding API Class`_
* `Shopping API Class`_
* `HTML Class`_
* `Parallel Class`_
* `YAML Configuration`_ 
* `Understanding eBay Credentials`_

.. _Understanding eBay Credentials: https://github.com/timotheus/ebaysdk-python/wiki/eBay-Credentials
.. _eBay Developer Site: http://developer.ebay.com/
.. _YAML Configuration: https://github.com/timotheus/ebaysdk-python/wiki/YAML-Configuration
.. _Trading API Class: https://github.com/timotheus/ebaysdk-python/wiki/Trading-API-Class
.. _Finding API Class: https://github.com/timotheus/ebaysdk-python/wiki/Finding-API-Class
.. _Shopping API Class: https://github.com/timotheus/ebaysdk-python/wiki/Shopping-API-Class
.. _HTML Class: https://github.com/timotheus/ebaysdk-python/wiki/HTML-Class
.. _Parallel Class: https://github.com/timotheus/ebaysdk-python/wiki/Parallel-Class



