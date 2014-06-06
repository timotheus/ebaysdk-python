# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os

from ebaysdk import log
from ebaysdk.connection import BaseConnection
from ebaysdk.config import Config
from ebaysdk.utils import getNodeText, dict2xml

class Connection(BaseConnection):
    """Trading API class

    API documentation:
    https://www.x.com/developers/ebay/products/trading-api

    Supported calls:
    AddItem
    ReviseItem
    GetUser
    (all others, see API docs)

    Doctests:
    >>> import datetime
    >>> t = Connection(config_file=os.environ.get('EBAY_YAML'))
    >>> response = t.execute('GetCharities', {'CharityID': 3897})
    >>> charity_name = ''
    >>> if len( t.response.dom().xpath('//Name') ) > 0:
    ...   charity_name = t.response.dom().xpath('//Name')[0].text
    >>> print(charity_name)
    Sunshine Kids Foundation
    >>> isinstance(response.reply.Timestamp, datetime.datetime)
    True
    >>> print(t.error())
    None
    >>> t2 = Connection(errors=False, debug=False, config_file=os.environ.get('EBAY_YAML'))
    >>> response = t2.execute('VerifyAddItem', {})
    >>> print(t2.response_codes())
    [10009]
    """

    def __init__(self, **kwargs):
        """Trading class constructor.

        Keyword arguments:
        domain        -- API endpoint (default: api.ebay.com)
        config_file   -- YAML defaults (default: ebay.yaml)
        debug         -- debugging enabled (default: False)
        warnings      -- warnings enabled (default: False)
        uri           -- API endpoint uri (default: /ws/api.dll)
        appid         -- eBay application id
        devid         -- eBay developer id
        certid        -- eBay cert id
        token         -- eBay application/user token
        siteid        -- eBay country site id (default: 0 (US))
        compatibility -- version number (default: 648)
        https         -- execute of https (default: True)
        proxy_host    -- proxy hostname
        proxy_port    -- proxy port number
        timeout       -- HTTP request timeout (default: 20)
        parallel      -- ebaysdk parallel object
        response_encoding -- API encoding (default: XML)
        request_encoding  -- API encoding (default: XML)
        """
        super(Connection, self).__init__(method='POST', **kwargs)

        self.config=Config(domain=kwargs.get('domain', 'api.ebay.com'),
                           connection_kwargs=kwargs,
                           config_file=kwargs.get('config_file', 'ebay.yaml'))


        # override yaml defaults with args sent to the constructor
        self.config.set('domain', kwargs.get('domain', 'api.ebay.com'))
        self.config.set('uri', '/ws/api.dll')
        self.config.set('warnings', True)
        self.config.set('errors', True)
        self.config.set('https', True)
        self.config.set('siteid', 0)
        self.config.set('response_encoding', 'XML')
        self.config.set('request_encoding', 'XML')
        self.config.set('proxy_host', None)
        self.config.set('proxy_port', None)
        self.config.set('token', None)
        self.config.set('iaf_token', None)
        self.config.set('appid', None)
        self.config.set('devid', None)
        self.config.set('certid', None)
        self.config.set('compatibility', '837')
        self.config.set('doc_url', 'http://developer.ebay.com/devzone/xml/docs/reference/ebay/index.html')

        self.datetime_nodes = [
            'shippingtime',
            'starttime',
            'endtime',
            'scheduletime',
            'createdtime',
            'hardexpirationtime',
            'invoicedate',
            'begindate',
            'enddate',
            'startcreationtime',
            'endcreationtime',
            'endtimefrom',
            'endtimeto',
            'updatetime',
            'lastupdatetime',
            'lastmodifiedtime',
            'modtimefrom',
            'modtimeto',
            'createtimefrom',
            'createtimeto',
            'starttimefrom',
            'starttimeto',
            'timeto',
            'paymenttimefrom',
            'paymenttimeto',
            'inventorycountlastcalculateddate',
            'registrationdate',
            'timefrom',
            'timestamp',
            'messagecreationtime',
            'resolutiontime',
            'date',
            'bankmodifydate',
            'creditcardexpiration',
            'creditcardmodifydate',
            'lastpaymentdate',
            'submittedtime',
            'announcementstarttime',
            'eventtime',
            'periodicstartdate',
            'modtime',
            'expirationtime',
            'creationtime',
            'lastusedtime',
            'disputecreatedtime',
            'disputemodifiedtime',
            'externaltransactiontime',
            'commenttime',
            'lastbidtime',
            'time',
            'creationdate',
            'lastmodifieddate',
            'receivedate',
            'expirationdate',
            'resolutiondate',
            'lastreaddate',
            'userforwarddate',
            'itemendtime',
            'userresponsedate',
            'nextretrytime',
            'deliverytime',
            'timebid',
            'paidtime',
            'shippedtime',
            'expectedreleasedate',
            'paymenttime',
            'promotionalsalestarttime',
            'promotionalsaleendtime',
            'refundtime',
            'refundrequestedtime',
            'refundcompletiontime',
            'estimatedrefundcompletiontime',
            'lastemailsenttime',
            'sellerinvoicetime',
            'estimateddeliverydate',
            'printedtime',
            'deliverydate',
            'refundgrantedtime',
            'scheduleddeliverytimemin',
            'scheduleddeliverytimemax',
            'actualdeliverytime',
            'usebydate',
            'lastopenedtime',
            'returndate',
            'revocationtime',
            'lasttimemodified',
            'createddate',
            'invoicesenttime',
            'acceptedtime',
            'sellerebaypaymentprocessenabletime',
            'useridlastchanged',
            'actionrequiredby',
        ]

        self.base_list_nodes = [
            'getmymessagesresponse.abstractrequesttype.detaillevel',
            'getaccountresponse.abstractrequesttype.outputselector',
            'getadformatleadsresponse.abstractrequesttype.outputselector',
            'getallbiddersresponse.abstractrequesttype.outputselector',
            'getbestoffersresponse.abstractrequesttype.outputselector',
            'getbidderlistresponse.abstractrequesttype.outputselector',
            'getcategoriesresponse.abstractrequesttype.outputselector',
            'getcategoryfeaturesresponse.abstractrequesttype.outputselector',
            'getcategorylistingsresponse.abstractrequesttype.outputselector',
            'getcrosspromotionsresponse.abstractrequesttype.outputselector',
            'getfeedbackresponse.abstractrequesttype.outputselector',
            'gethighbiddersresponse.abstractrequesttype.outputselector',
            'getitemresponse.abstractrequesttype.outputselector',
            'getitemsawaitingfeedbackresponse.abstractrequesttype.outputselector',
            'getitemshippingresponse.abstractrequesttype.outputselector',
            'getitemtransactionsresponse.abstractrequesttype.outputselector',
            'getmembermessagesresponse.abstractrequesttype.outputselector',
            'getmyebaybuyingresponse.abstractrequesttype.outputselector',
            'getmyebaysellingresponse.abstractrequesttype.outputselector',
            'getmymessagesresponse.abstractrequesttype.outputselector',
            'getnotificationpreferencesresponse.abstractrequesttype.outputselector',
            'getordersresponse.abstractrequesttype.outputselector',
            'getordertransactionsresponse.abstractrequesttype.outputselector',
            'getproductsresponse.abstractrequesttype.outputselector',
            'getsearchresultsresponse.abstractrequesttype.outputselector',
            'getsellereventsresponse.abstractrequesttype.outputselector',
            'getsellerlistresponse.abstractrequesttype.outputselector',
            'getsellerpaymentsresponse.abstractrequesttype.outputselector',
            'getsellertransactionsresponse.abstractrequesttype.outputselector',
            'getmessagepreferencesresponse.asqpreferencestype.subject',
            'getaccountresponse.accountentriestype.accountentry',
            'getaccountresponse.accountsummarytype.additionalaccount',
            'additemresponse.additemresponsecontainertype.discountreason',
            'additemsresponse.additemresponsecontainertype.discountreason',
            'setnotificationpreferencesresponse.applicationdeliverypreferencestype.deliveryurldetails',
            'additemresponse.attributearraytype.attribute',
            'additemsresponse.attributearraytype.attribute',
            'verifyadditemresponse.attributearraytype.attribute',
            'additemresponse.attributetype.value',
            'additemsresponse.attributetype.value',
            'addsellingmanagertemplateresponse.attributetype.value',
            'addliveauctionitemresponse.attributetype.value',
            'getitemrecommendationsresponse.attributetype.value',
            'verifyadditemresponse.attributetype.value',
            'addfixedpriceitemresponse.attributetype.value',
            'relistfixedpriceitemresponse.attributetype.value',
            'revisefixedpriceitemresponse.attributetype.value',
            'getfeedbackresponse.averageratingdetailarraytype.averageratingdetails',
            'getfeedbackresponse.averageratingsummarytype.averageratingdetails',
            'respondtobestofferresponse.bestofferarraytype.bestoffer',
            'getliveauctionbiddersresponse.bidderdetailarraytype.bidderdetail',
            'getallbiddersresponse.biddingsummarytype.itembiddetails',
            'getsellerdashboardresponse.buyersatisfactiondashboardtype.alert',
            'getshippingdiscountprofilesresponse.calculatedshippingdiscounttype.discountprofile',
            'getcategoriesresponse.categoryarraytype.category',
            'getcategoryfeaturesresponse.categoryfeaturetype.listingduration',
            'getcategoryfeaturesresponse.categoryfeaturetype.paymentmethod',
            'getcategoriesresponse.categorytype.categoryparentid',
            'getsuggestedcategoriesresponse.categorytype.categoryparentname',
            'getcategory2csresponse.categorytype.productfinderids',
            'getcategory2csresponse.categorytype.characteristicssets',
            'getproductfamilymembersresponse.characteristicssettype.characteristics',
            'getproductsearchpageresponse.characteristicssettype.characteristics',
            'getproductsearchresultsresponse.characteristicssettype.characteristics',
            'getuserresponse.charityaffiliationdetailstype.charityaffiliationdetail',
            'getbidderlistresponse.charityaffiliationstype.charityid',
            'setcharitiesresponse.charityinfotype.nonprofitaddress',
            'setcharitiesresponse.charityinfotype.nonprofitsocialaddress',
            'getcategoryfeaturesresponse.conditionvaluestype.condition',
            'getbidderlistresponse.crosspromotionstype.promoteditem',
            'getuserdisputesresponse.disputearraytype.dispute',
            'getuserdisputesresponse.disputetype.disputeresolution',
            'getdisputeresponse.disputetype.disputemessage',
            'setsellingmanagerfeedbackoptionsresponse.feedbackcommentarraytype.storedcommenttext',
            'getfeedbackresponse.feedbackdetailarraytype.feedbackdetail',
            'getfeedbackresponse.feedbackperiodarraytype.feedbackperiod',
            'addfixedpriceitemresponse.feestype.fee',
            'additemresponse.feestype.fee',
            'additemsresponse.feestype.fee',
            'addliveauctionitemresponse.feestype.fee',
            'relistfixedpriceitemresponse.feestype.fee',
            'relistitemresponse.feestype.fee',
            'revisefixedpriceitemresponse.feestype.fee',
            'reviseitemresponse.feestype.fee',
            'reviseliveauctionitemresponse.feestype.fee',
            'verifyaddfixedpriceitemresponse.feestype.fee',
            'verifyadditemresponse.feestype.fee',
            'reviseinventorystatusresponse.feestype.fee',
            'verifyrelistitemresponse.feestype.fee',
            'getshippingdiscountprofilesresponse.flatshippingdiscounttype.discountprofile',
            'getitemrecommendationsresponse.getrecommendationsrequestcontainertype.recommendationengine',
            'getitemrecommendationsresponse.getrecommendationsrequestcontainertype.deletedfield',
            'getuserresponse.integratedmerchantcreditcardinfotype.supportedsite',
            'sendinvoiceresponse.internationalshippingserviceoptionstype.shiptolocation',
            'reviseinventorystatusresponse.inventoryfeestype.fee',
            'getbidderlistresponse.itemarraytype.item',
            'getbestoffersresponse.itembestoffersarraytype.itembestoffers',
            'addfixedpriceitemresponse.itemcompatibilitylisttype.compatibility',
            'additemresponse.itemcompatibilitylisttype.compatibility',
            'additemfromsellingmanagertemplateresponse.itemcompatibilitylisttype.compatibility',
            'additemsresponse.itemcompatibilitylisttype.compatibility',
            'addsellingmanagertemplateresponse.itemcompatibilitylisttype.compatibility',
            'relistfixedpriceitemresponse.itemcompatibilitylisttype.compatibility',
            'relistitemresponse.itemcompatibilitylisttype.compatibility',
            'revisefixedpriceitemresponse.itemcompatibilitylisttype.compatibility',
            'reviseitemresponse.itemcompatibilitylisttype.compatibility',
            'revisesellingmanagertemplateresponse.itemcompatibilitylisttype.compatibility',
            'verifyaddfixedpriceitemresponse.itemcompatibilitylisttype.compatibility',
            'verifyadditemresponse.itemcompatibilitylisttype.compatibility',
            'verifyrelistitemresponse.itemcompatibilitylisttype.compatibility',
            'addfixedpriceitemresponse.itemcompatibilitytype.namevaluelist',
            'additemresponse.itemcompatibilitytype.namevaluelist',
            'additemfromsellingmanagertemplateresponse.itemcompatibilitytype.namevaluelist',
            'additemsresponse.itemcompatibilitytype.namevaluelist',
            'addsellingmanagertemplateresponse.itemcompatibilitytype.namevaluelist',
            'relistfixedpriceitemresponse.itemcompatibilitytype.namevaluelist',
            'relistitemresponse.itemcompatibilitytype.namevaluelist',
            'revisefixedpriceitemresponse.itemcompatibilitytype.namevaluelist',
            'reviseitemresponse.itemcompatibilitytype.namevaluelist',
            'revisesellingmanagertemplateresponse.itemcompatibilitytype.namevaluelist',
            'verifyadditemresponse.itemcompatibilitytype.namevaluelist',
            'verifyrelistitemresponse.itemcompatibilitytype.namevaluelist',
            'getpromotionalsaledetailsresponse.itemidarraytype.itemid',
            'leavefeedbackresponse.itemratingdetailarraytype.itemratingdetails',
            'getordertransactionsresponse.itemtransactionidarraytype.itemtransactionid',
            'addfixedpriceitemresponse.itemtype.giftservices',
            'additemresponse.itemtype.giftservices',
            'additemsresponse.itemtype.giftservices',
            'addsellingmanagertemplateresponse.itemtype.giftservices',
            'getitemrecommendationsresponse.itemtype.giftservices',
            'relistfixedpriceitemresponse.itemtype.giftservices',
            'relistitemresponse.itemtype.giftservices',
            'revisefixedpriceitemresponse.itemtype.giftservices',
            'reviseitemresponse.itemtype.giftservices',
            'revisesellingmanagertemplateresponse.itemtype.giftservices',
            'verifyadditemresponse.itemtype.giftservices',
            'verifyrelistitemresponse.itemtype.giftservices',
            'addfixedpriceitemresponse.itemtype.listingenhancement',
            'additemresponse.itemtype.listingenhancement',
            'additemsresponse.itemtype.listingenhancement',
            'addsellingmanagertemplateresponse.itemtype.listingenhancement',
            'getitemrecommendationsresponse.itemtype.listingenhancement',
            'relistfixedpriceitemresponse.itemtype.listingenhancement',
            'relistitemresponse.itemtype.listingenhancement',
            'revisefixedpriceitemresponse.itemtype.listingenhancement',
            'reviseitemresponse.itemtype.listingenhancement',
            'revisesellingmanagertemplateresponse.itemtype.listingenhancement',
            'verifyadditemresponse.itemtype.listingenhancement',
            'verifyrelistitemresponse.itemtype.listingenhancement',
            'addfixedpriceitemresponse.itemtype.paymentmethods',
            'additemresponse.itemtype.paymentmethods',
            'additemfromsellingmanagertemplateresponse.itemtype.paymentmethods',
            'additemsresponse.itemtype.paymentmethods',
            'addsellingmanagertemplateresponse.itemtype.paymentmethods',
            'relistfixedpriceitemresponse.itemtype.paymentmethods',
            'relistitemresponse.itemtype.paymentmethods',
            'revisefixedpriceitemresponse.itemtype.paymentmethods',
            'reviseitemresponse.itemtype.paymentmethods',
            'verifyadditemresponse.itemtype.paymentmethods',
            'verifyrelistitemresponse.itemtype.paymentmethods',
            'addfixedpriceitemresponse.itemtype.shiptolocations',
            'additemresponse.itemtype.shiptolocations',
            'additemsresponse.itemtype.shiptolocations',
            'addsellingmanagertemplateresponse.itemtype.shiptolocations',
            'getitemrecommendationsresponse.itemtype.shiptolocations',
            'relistfixedpriceitemresponse.itemtype.shiptolocations',
            'relistitemresponse.itemtype.shiptolocations',
            'revisefixedpriceitemresponse.itemtype.shiptolocations',
            'reviseitemresponse.itemtype.shiptolocations',
            'revisesellingmanagertemplateresponse.itemtype.shiptolocations',
            'verifyadditemresponse.itemtype.shiptolocations',
            'verifyrelistitemresponse.itemtype.shiptolocations',
            'addfixedpriceitemresponse.itemtype.skypecontactoption',
            'additemresponse.itemtype.skypecontactoption',
            'additemsresponse.itemtype.skypecontactoption',
            'addsellingmanagertemplateresponse.itemtype.skypecontactoption',
            'relistfixedpriceitemresponse.itemtype.skypecontactoption',
            'relistitemresponse.itemtype.skypecontactoption',
            'revisefixedpriceitemresponse.itemtype.skypecontactoption',
            'reviseitemresponse.itemtype.skypecontactoption',
            'revisesellingmanagertemplateresponse.itemtype.skypecontactoption',
            'verifyadditemresponse.itemtype.skypecontactoption',
            'verifyrelistitemresponse.itemtype.skypecontactoption',
            'addfixedpriceitemresponse.itemtype.crossbordertrade',
            'additemresponse.itemtype.crossbordertrade',
            'additemsresponse.itemtype.crossbordertrade',
            'addsellingmanagertemplateresponse.itemtype.crossbordertrade',
            'relistfixedpriceitemresponse.itemtype.crossbordertrade',
            'relistitemresponse.itemtype.crossbordertrade',
            'revisefixedpriceitemresponse.itemtype.crossbordertrade',
            'reviseitemresponse.itemtype.crossbordertrade',
            'revisesellingmanagertemplateresponse.itemtype.crossbordertrade',
            'verifyadditemresponse.itemtype.crossbordertrade',
            'verifyrelistitemresponse.itemtype.crossbordertrade',
            'getitemresponse.itemtype.paymentallowedsite',
            'getsellingmanagertemplatesresponse.itemtype.paymentallowedsite',
            'getcategoryfeaturesresponse.listingdurationdefinitiontype.duration',
            'getcategoryfeaturesresponse.listingdurationdefinitionstype.listingduration',
            'getcategoryfeaturesresponse.listingenhancementdurationreferencetype.duration',
            'addfixedpriceitemresponse.listingrecommendationtype.value',
            'additemresponse.listingrecommendationtype.value',
            'additemsresponse.listingrecommendationtype.value',
            'relistfixedpriceitemresponse.listingrecommendationtype.value',
            'relistitemresponse.listingrecommendationtype.value',
            'revisefixedpriceitemresponse.listingrecommendationtype.value',
            'reviseitemresponse.listingrecommendationtype.value',
            'verifyadditemresponse.listingrecommendationtype.value',
            'verifyaddfixedpriceitemresponse.listingrecommendationtype.value',
            'verifyrelistitemresponse.listingrecommendationtype.value',
            'addfixedpriceitemresponse.listingrecommendationstype.recommendation',
            'additemresponse.listingrecommendationstype.recommendation',
            'additemsresponse.listingrecommendationstype.recommendation',
            'relistfixedpriceitemresponse.listingrecommendationstype.recommendation',
            'relistitemresponse.listingrecommendationstype.recommendation',
            'revisefixedpriceitemresponse.listingrecommendationstype.recommendation',
            'reviseitemresponse.listingrecommendationstype.recommendation',
            'verifyadditemresponse.listingrecommendationstype.recommendation',
            'verifyaddfixedpriceitemresponse.listingrecommendationstype.recommendation',
            'verifyrelistitemresponse.listingrecommendationstype.recommendation',
            'getitemrecommendationsresponse.listingtiparraytype.listingtip',
            'getnotificationsusageresponse.markupmarkdownhistorytype.markupmarkdownevent',
            'getebaydetailsresponse.maximumbuyerpolicyviolationsdetailstype.policyviolationduration',
            'getebaydetailsresponse.maximumitemrequirementsdetailstype.maximumitemcount',
            'getebaydetailsresponse.maximumitemrequirementsdetailstype.minimumfeedbackscore',
            'getebaydetailsresponse.maximumunpaiditemstrikescountdetailstype.count',
            'getebaydetailsresponse.maximumunpaiditemstrikesinfodetailstype.maximumunpaiditemstrikesduration',
            'getadformatleadsresponse.membermessageexchangearraytype.membermessageexchange',
            'getadformatleadsresponse.membermessageexchangetype.response',
            'getmembermessagesresponse.membermessageexchangetype.messagemedia',
            'addmembermessageaaqtopartnerresponse.membermessagetype.recipientid',
            'addmembermessagertqresponse.membermessagetype.recipientid',
            'addmembermessagesaaqtobidderresponse.membermessagetype.recipientid',
            'addmembermessageaaqtopartnerresponse.membermessagetype.messagemedia',
            'addmembermessagertqresponse.membermessagetype.messagemedia',
            'addmembermessagecemresponse.membermessagetype.messagemedia',
            'addmembermessageaaqtosellerresponse.membermessagetype.messagemedia',
            'getebaydetailsresponse.minimumfeedbackscoredetailstype.feedbackscore',
            'relistfixedpriceitemresponse.modifynamearraytype.modifyname',
            'revisefixedpriceitemresponse.modifynamearraytype.modifyname',
            'getmymessagesresponse.mymessagesexternalmessageidarraytype.externalmessageid',
            'getmymessagesresponse.mymessagesmessagearraytype.message',
            'deletemymessagesresponse.mymessagesmessageidarraytype.messageid',
            'getmymessagesresponse.mymessagesmessagetype.messagemedia',
            'getmymessagesresponse.mymessagessummarytype.foldersummary',
            'getmyebaybuyingresponse.myebayfavoritesearchlisttype.favoritesearch',
            'getmyebaybuyingresponse.myebayfavoritesearchtype.searchflag',
            'getmyebaybuyingresponse.myebayfavoritesearchtype.sellerid',
            'getmyebaybuyingresponse.myebayfavoritesearchtype.selleridexclude',
            'getmyebaybuyingresponse.myebayfavoritesellerlisttype.favoriteseller',
            'getcategoryspecificsresponse.namerecommendationtype.valuerecommendation',
            'getitemrecommendationsresponse.namerecommendationtype.valuerecommendation',
            'addfixedpriceitemresponse.namevaluelistarraytype.namevaluelist',
            'additemresponse.namevaluelistarraytype.namevaluelist',
            'additemsresponse.namevaluelistarraytype.namevaluelist',
            'addsellingmanagertemplateresponse.namevaluelistarraytype.namevaluelist',
            'addliveauctionitemresponse.namevaluelistarraytype.namevaluelist',
            'relistfixedpriceitemresponse.namevaluelistarraytype.namevaluelist',
            'relistitemresponse.namevaluelistarraytype.namevaluelist',
            'revisefixedpriceitemresponse.namevaluelistarraytype.namevaluelist',
            'reviseitemresponse.namevaluelistarraytype.namevaluelist',
            'revisesellingmanagertemplateresponse.namevaluelistarraytype.namevaluelist',
            'reviseliveauctionitemresponse.namevaluelistarraytype.namevaluelist',
            'verifyaddfixedpriceitemresponse.namevaluelistarraytype.namevaluelist',
            'verifyadditemresponse.namevaluelistarraytype.namevaluelist',
            'verifyrelistitemresponse.namevaluelistarraytype.namevaluelist',
            'additemresponse.namevaluelisttype.value',
            'additemfromsellingmanagertemplateresponse.namevaluelisttype.value',
            'additemsresponse.namevaluelisttype.value',
            'addsellingmanagertemplateresponse.namevaluelisttype.value',
            'addliveauctionitemresponse.namevaluelisttype.value',
            'relistitemresponse.namevaluelisttype.value',
            'reviseitemresponse.namevaluelisttype.value',
            'revisesellingmanagertemplateresponse.namevaluelisttype.value',
            'reviseliveauctionitemresponse.namevaluelisttype.value',
            'verifyadditemresponse.namevaluelisttype.value',
            'verifyrelistitemresponse.namevaluelisttype.value',
            'getnotificationsusageresponse.notificationdetailsarraytype.notificationdetails',
            'setnotificationpreferencesresponse.notificationenablearraytype.notificationenable',
            'setnotificationpreferencesresponse.notificationuserdatatype.summaryschedule',
            'getebaydetailsresponse.numberofpolicyviolationsdetailstype.count',
            'getallbiddersresponse.offerarraytype.offer',
            'gethighbiddersresponse.offerarraytype.offer',
            'getordersresponse.orderarraytype.order',
            'getordersresponse.orderidarraytype.orderid',
            'getmyebaybuyingresponse.ordertransactionarraytype.ordertransaction',
            'addorderresponse.ordertype.paymentmethods',
            'getordertransactionsresponse.ordertype.externaltransaction',
            'getordersresponse.ordertype.externaltransaction',
            'getordersresponse.paymentinformationcodetype.payment',
            'getordersresponse.paymentinformationtype.payment',
            'getordersresponse.paymenttransactioncodetype.paymentreferenceid',
            'getordersresponse.paymenttransactiontype.paymentreferenceid',
            'getsellerdashboardresponse.performancedashboardtype.site',
            'getordersresponse.pickupdetailstype.pickupoptions',
            'additemresponse.picturedetailstype.pictureurl',
            'additemsresponse.picturedetailstype.pictureurl',
            'addsellingmanagertemplateresponse.picturedetailstype.pictureurl',
            'getitemrecommendationsresponse.picturedetailstype.pictureurl',
            'relistitemresponse.picturedetailstype.pictureurl',
            'reviseitemresponse.picturedetailstype.pictureurl',
            'revisesellingmanagertemplateresponse.picturedetailstype.pictureurl',
            'verifyadditemresponse.picturedetailstype.pictureurl',
            'verifyrelistitemresponse.picturedetailstype.pictureurl',
            'getitemresponse.picturedetailstype.externalpictureurl',
            'addfixedpriceitemresponse.picturestype.variationspecificpictureset',
            'verifyaddfixedpriceitemresponse.picturestype.variationspecificpictureset',
            'relistfixedpriceitemresponse.picturestype.variationspecificpictureset',
            'revisefixedpriceitemresponse.picturestype.variationspecificpictureset',
            'getsellerdashboardresponse.powersellerdashboardtype.alert',
            'getbidderlistresponse.productlistingdetailstype.copyright',
            'getitemrecommendationsresponse.productrecommendationstype.product',
            'addfixedpriceitemresponse.productsuggestionstype.productsuggestion',
            'additemresponse.productsuggestionstype.productsuggestion',
            'relistfixedpriceitemresponse.productsuggestionstype.productsuggestion',
            'relistitemresponse.productsuggestionstype.productsuggestion',
            'revisefixedpriceitemresponse.productsuggestionstype.productsuggestion',
            'reviseitemresponse.productsuggestionstype.productsuggestion',
            'verifyadditemresponse.productsuggestionstype.productsuggestion',
            'verifyrelistitemresponse.productsuggestionstype.productsuggestion',
            'getpromotionalsaledetailsresponse.promotionalsalearraytype.promotionalsale',
            'addfixedpriceitemresponse.recommendationtype.recommendedvalue',
            'additemresponse.recommendationtype.recommendedvalue',
            'additemsresponse.recommendationtype.recommendedvalue',
            'relistfixedpriceitemresponse.recommendationtype.recommendedvalue',
            'relistitemresponse.recommendationtype.recommendedvalue',
            'revisefixedpriceitemresponse.recommendationtype.recommendedvalue',
            'reviseitemresponse.recommendationtype.recommendedvalue',
            'verifyadditemresponse.recommendationtype.recommendedvalue',
            'verifyaddfixedpriceitemresponse.recommendationtype.recommendedvalue',
            'verifyrelistitemresponse.recommendationtype.recommendedvalue',
            'getcategoryspecificsresponse.recommendationvalidationrulestype.relationship',
            'getitemrecommendationsresponse.recommendationvalidationrulestype.relationship',
            'getcategoryspecificsresponse.recommendationstype.namerecommendation',
            'getitemrecommendationsresponse.recommendationstype.namerecommendation',
            'getuserresponse.recoupmentpolicyconsenttype.site',
            'getordersresponse.refundarraytype.refund',
            'getordersresponse.refundfundingsourcearraytype.refundfundingsource',
            'getitemtransactionsresponse.refundfundingsourcearraytype.refundfundingsource',
            'getordertransactionsresponse.refundfundingsourcearraytype.refundfundingsource',
            'getsellertransactionsresponse.refundfundingsourcearraytype.refundfundingsource',
            'getordersresponse.refundinformationtype.refund',
            'getordersresponse.refundlinearraytype.refundline',
            'getitemtransactionsresponse.refundlinearraytype.refundline',
            'getordertransactionsresponse.refundlinearraytype.refundline',
            'getsellertransactionsresponse.refundlinearraytype.refundline',
            'getordersresponse.refundtransactionarraytype.refundtransaction',
            'getitemtransactionsresponse.refundtransactionarraytype.refundtransaction',
            'getordertransactionsresponse.refundtransactionarraytype.refundtransaction',
            'getsellertransactionsresponse.refundtransactionarraytype.refundtransaction',
            'getordersresponse.requiredselleractionarraytype.requiredselleraction',
            'getebaydetailsresponse.returnpolicydetailstype.refund',
            'getebaydetailsresponse.returnpolicydetailstype.returnswithin',
            'getebaydetailsresponse.returnpolicydetailstype.returnsaccepted',
            'getebaydetailsresponse.returnpolicydetailstype.warrantyoffered',
            'getebaydetailsresponse.returnpolicydetailstype.warrantytype',
            'getebaydetailsresponse.returnpolicydetailstype.warrantyduration',
            'getebaydetailsresponse.returnpolicydetailstype.shippingcostpaidby',
            'getebaydetailsresponse.returnpolicydetailstype.restockingfeevalue',
            'getsellertransactionsresponse.skuarraytype.sku',
            'getsellerlistresponse.skuarraytype.sku',
            'getsellerdashboardresponse.selleraccountdashboardtype.alert',
            'getitemtransactionsresponse.sellerdiscountstype.sellerdiscount',
            'getordersresponse.sellerdiscountstype.sellerdiscount',
            'getordertransactionsresponse.sellerdiscountstype.sellerdiscount',
            'getsellertransactionsresponse.sellerdiscountstype.sellerdiscount',
            'getuserpreferencesresponse.sellerexcludeshiptolocationpreferencestype.excludeshiptolocation',
            'getuserpreferencesresponse.sellerfavoriteitempreferencestype.favoriteitemid',
            'getfeedbackresponse.sellerratingsummaryarraytype.averageratingsummary',
            'getbidderlistresponse.sellerebaypaymentprocessconsentcodetype.useragreementinfo',
            'getsellingmanagertemplateautomationruleresponse.sellingmanagerautolistaccordingtoscheduletype.dayofweek',
            'getsellingmanagerinventoryfolderresponse.sellingmanagerfolderdetailstype.childfolder',
            'revisesellingmanagerinventoryfolderresponse.sellingmanagerfolderdetailstype.childfolder',
            'getsellingmanagersalerecordresponse.sellingmanagersoldordertype.sellingmanagersoldtransaction',
            'getsellingmanagersoldlistingsresponse.sellingmanagersoldordertype.sellingmanagersoldtransaction',
            'getsellingmanagersalerecordresponse.sellingmanagersoldordertype.vatrate',
            'getsellingmanagersoldlistingsresponse.sellingmanagersoldtransactiontype.listedon',
            'getsellingmanagertemplatesresponse.sellingmanagertemplatedetailsarraytype.sellingmanagertemplatedetails',
            'completesaleresponse.shipmentlineitemtype.lineitem',
            'addshipmentresponse.shipmentlineitemtype.lineitem',
            'reviseshipmentresponse.shipmentlineitemtype.lineitem',
            'revisesellingmanagersalerecordresponse.shipmentlineitemtype.lineitem',
            'setshipmenttrackinginforesponse.shipmentlineitemtype.lineitem',
            'completesaleresponse.shipmenttype.shipmenttrackingdetails',
            'getitemresponse.shippingdetailstype.shippingserviceoptions',
            'getsellingmanagertemplatesresponse.shippingdetailstype.shippingserviceoptions',
            'addfixedpriceitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'additemresponse.shippingdetailstype.internationalshippingserviceoption',
            'additemsresponse.shippingdetailstype.internationalshippingserviceoption',
            'addsellingmanagertemplateresponse.shippingdetailstype.internationalshippingserviceoption',
            'addorderresponse.shippingdetailstype.internationalshippingserviceoption',
            'getitemrecommendationsresponse.shippingdetailstype.internationalshippingserviceoption',
            'relistfixedpriceitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'relistitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'revisefixedpriceitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'reviseitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'revisesellingmanagertemplateresponse.shippingdetailstype.internationalshippingserviceoption',
            'verifyadditemresponse.shippingdetailstype.internationalshippingserviceoption',
            'verifyrelistitemresponse.shippingdetailstype.internationalshippingserviceoption',
            'getsellerlistresponse.shippingdetailstype.excludeshiptolocation',
            'getitemtransactionsresponse.shippingdetailstype.shipmenttrackingdetails',
            'getsellertransactionsresponse.shippingdetailstype.shipmenttrackingdetails',
            'getshippingdiscountprofilesresponse.shippinginsurancetype.flatrateinsurancerangecost',
            'addfixedpriceitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'additemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'additemsresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'verifyadditemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'verifyaddfixedpriceitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'verifyrelistitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'relistfixedpriceitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'relistitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'revisefixedpriceitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'reviseitemresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'addsellingmanagertemplateresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'revisesellingmanagertemplateresponse.shippingservicecostoverridelisttype.shippingservicecostoverride',
            'getebaydetailsresponse.shippingservicedetailstype.servicetype',
            'getebaydetailsresponse.shippingservicedetailstype.shippingpackage',
            'getebaydetailsresponse.shippingservicedetailstype.shippingcarrier',
            'getebaydetailsresponse.shippingservicedetailstype.deprecationdetails',
            'getebaydetailsresponse.shippingservicedetailstype.shippingservicepackagedetails',
            'getordersresponse.shippingserviceoptionstype.shippingpackageinfo',
            'getcategoryfeaturesresponse.sitedefaultstype.listingduration',
            'getcategoryfeaturesresponse.sitedefaultstype.paymentmethod',
            'uploadsitehostedpicturesresponse.sitehostedpicturedetailstype.picturesetmember',
            'getcategory2csresponse.sitewidecharacteristicstype.excludecategoryid',
            'getstoreoptionsresponse.storecolorschemearraytype.colorscheme',
            'getstoreresponse.storecustomcategoryarraytype.customcategory',
            'getstoreresponse.storecustomcategorytype.childcategory',
            'setstorecategoriesresponse.storecustomcategorytype.childcategory',
            'setstoreresponse.storecustomlistingheadertype.linktoinclude',
            'getstorecustompageresponse.storecustompagearraytype.custompage',
            'getstoreoptionsresponse.storelogoarraytype.logo',
            'getcategoryfeaturesresponse.storeownerextendedlistingdurationstype.duration',
            'getstoreoptionsresponse.storesubscriptionarraytype.subscription',
            'getstoreoptionsresponse.storethemearraytype.theme',
            'getsuggestedcategoriesresponse.suggestedcategoryarraytype.suggestedcategory',
            'getuserpreferencesresponse.supportedsellerprofilestype.supportedsellerprofile',
            'settaxtableresponse.taxtabletype.taxjurisdiction',
            'getitemtransactionsresponse.taxestype.taxdetails',
            'getordersresponse.taxestype.taxdetails',
            'getordertransactionsresponse.taxestype.taxdetails',
            'getsellertransactionsresponse.taxestype.taxdetails',
            'getdescriptiontemplatesresponse.themegrouptype.themeid',
            'getuserresponse.topratedsellerdetailstype.topratedprogram',
            'getordersresponse.transactionarraytype.transaction',
            'getitemtransactionsresponse.transactiontype.externaltransaction',
            'getsellertransactionsresponse.transactiontype.externaltransaction',
            'getebaydetailsresponse.unitofmeasurementdetailstype.unitofmeasurement',
            'getebaydetailsresponse.unitofmeasurementtype.alternatetext',
            'getuserpreferencesresponse.unpaiditemassistancepreferencestype.excludeduser',
            'getsellerlistresponse.useridarraytype.userid',
            'getuserresponse.usertype.usersubscription',
            'getuserresponse.usertype.skypeid',
            'addfixedpriceitemresponse.variationspecificpicturesettype.pictureurl',
            'revisefixedpriceitemresponse.variationspecificpicturesettype.pictureurl',
            'relistfixedpriceitemresponse.variationspecificpicturesettype.pictureurl',
            'verifyaddfixedpriceitemresponse.variationspecificpicturesettype.pictureurl',
            'getitemresponse.variationspecificpicturesettype.externalpictureurl',
            'getitemsresponse.variationspecificpicturesettype.externalpictureurl',
            'addfixedpriceitemresponse.variationstype.variation',
            'revisefixedpriceitemresponse.variationstype.variation',
            'relistfixedpriceitemresponse.variationstype.variation',
            'verifyaddfixedpriceitemresponse.variationstype.variation',
            'addfixedpriceitemresponse.variationstype.pictures',
            'revisefixedpriceitemresponse.variationstype.pictures',
            'relistfixedpriceitemresponse.variationstype.pictures',
            'verifyaddfixedpriceitemresponse.variationstype.pictures',
            'getveroreasoncodedetailsresponse.veroreasoncodedetailstype.verositedetail',
            'veroreportitemsresponse.veroreportitemtype.region',
            'veroreportitemsresponse.veroreportitemtype.country',
            'veroreportitemsresponse.veroreportitemstype.reportitem',
            'getveroreportstatusresponse.veroreporteditemdetailstype.reporteditem',
            'getveroreasoncodedetailsresponse.verositedetailtype.reasoncodedetail',
            'getebaydetailsresponse.verifieduserrequirementsdetailstype.feedbackscore',
            'getwantitnowsearchresultsresponse.wantitnowpostarraytype.wantitnowpost',
        ]

    def build_request_headers(self, verb):
        headers = {
            "X-EBAY-API-COMPATIBILITY-LEVEL": self.config.get('compatibility', ''),
            "X-EBAY-API-DEV-NAME": self.config.get('devid', ''),
            "X-EBAY-API-APP-NAME": self.config.get('appid', ''),
            "X-EBAY-API-CERT-NAME": self.config.get('certid', ''),
            "X-EBAY-API-SITEID": self.config.get('siteid', ''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "Content-Type": "text/xml"
        }
        if self.config.get('iaf_token', None):
            headers["X-EBAY-API-IAF-TOKEN"] = self.config.get('iaf_token')

        return headers

    def build_request_data(self, verb, data, verb_attrs):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        if not self.config.get('iaf_token', None):
            xml += "<RequesterCredentials>"
            if self.config.get('token', None):
                xml += "<eBayAuthToken>%s</eBayAuthToken>" % self.config.get('token')
            elif self.config.get('username', None):
                xml += "<Username>%s</Username>" % self.config.get('username', '')
                if self.config.get('password', None):
                    xml += "<Password>%s</Password>" % self.config.get('password', '')
            xml += "</RequesterCredentials>"
        xml += dict2xml(data)
        xml += "</" + self.verb + "Request>"
        return xml

    def warnings(self):
        warning_string = ""

        if len(self._resp_body_warnings) > 0:
            warning_string = "%s: %s" \
                % (self.verb, ", ".join(self._resp_body_warnings))

        return warning_string

    def _get_resp_body_errors(self):
        """Parses the response content to pull errors.

        Child classes should override this method based on what the errors in the
        XML response body look like. They can choose to look at the 'ack',
        'Errors', 'errorMessage' or whatever other fields the service returns.
        the implementation below is the original code that was part of error()
        """

        if self._resp_body_errors and len(self._resp_body_errors) > 0:
            return self._resp_body_errors

        errors = []
        warnings = []
        resp_codes = []

        if self.verb is None:
            return errors

        dom = self.response.dom()
        if dom is None:
            return errors

        for e in dom.findall('Errors'):
            eSeverity = None
            eClass = None
            eShortMsg = None
            eLongMsg = None
            eCode = None

            try:
                eSeverity = e.findall('SeverityCode')[0].text
            except IndexError:
                pass

            try:
                eClass = e.findall('ErrorClassification')[0].text
            except IndexError:
                pass

            try:
                eCode = e.findall('ErrorCode')[0].text
            except IndexError:
                pass

            try:
                eShortMsg = e.findall('ShortMessage')[0].text
            except IndexError:
                pass

            try:
                eLongMsg = e.findall('LongMessage')[0].text
            except IndexError:
                pass

            try:
                eCode = e.findall('ErrorCode')[0].text
                if int(eCode) not in resp_codes:
                    resp_codes.append(int(eCode))    
            except IndexError:
                pass

            msg = "Class: %s, Severity: %s, Code: %s, %s%s" \
                % (eClass, eSeverity, eCode, eShortMsg, eLongMsg)

            if eSeverity == 'Warning':
                warnings.append(msg)
            else:
                errors.append(msg)

        self._resp_body_warnings = warnings
        self._resp_body_errors = errors
        self._resp_codes = resp_codes

        if self.config.get('warnings') and len(warnings) > 0:
            log.warn("%s: %s\n\n" % (self.verb, "\n".join(warnings)))

        if self.response.reply.Ack == 'Failure':
            if self.config.get('errors'):
                log.error("%s: %s\n\n" % (self.verb, "\n".join(errors)))
            
            return errors

        return []
