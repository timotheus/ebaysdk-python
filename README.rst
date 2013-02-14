Welcome to the python ebaysdk
=============================

This SDK is a dead-simple, programatic inteface into the eBay APIs. It simplifies development and cuts development time by standerizing calls, response processing, error handling, debugging across the Finding, Shopping, Merchandising, & Trading APIs. 

In order to use eBay aspects of this utility you must first register with eBay to get your `eBay Developer Site`_ (see the ebay.yaml for a way to easily tie eBay credentials to the SDK) Finding Services.

Support ...TBD


Quick Example::

    from ebaysdk import finding

    api = finding(--appid='YOUR_APPID_HERE')
    api.execute('findItemsAdvanced', {'keywords': 'shoes'})        

    print api.response_dict()

Getting Started
---------------

`Trading Docs`_
`Finding Docs`_


.. _eBay Developer Site: http://developer.ebay.com/
.. _Trading Docs: https://github.com/timotheus/ebaysdk-python/wiki/Trading-API-Class
.. _Finding Docs: https://github.com/timotheus/ebaysdk-python/wiki/Finding-API-Class
.. _Shopping Docs: https://github.com/timotheus/ebaysdk-python/wiki/Shopping-API-Class
.. _HTML Docs: https://github.com/timotheus/ebaysdk-python/wiki/HTML-Class
.. _Parallel Docs: https://github.com/timotheus/ebaysdk-python/wiki/Parallel-Class



