from ebaysdk.utils import xml2dict

xml = """<?xml version="1.0" encoding="utf-8"?>
<VerifyAddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>ABC...123</eBayAuthToken>
  </RequesterCredentials>
  <ErrorLanguage>en_US</ErrorLanguage>
  <WarningLevel>High</WarningLevel>
  <Item>
    <Title>Harry Potter and the Philosopher's Stone</Title>
    <Description>
      This is the first book in the Harry Potter series. In excellent condition!
    </Description>
    <PrimaryCategory>
      <CategoryID>377</CategoryID>
    </PrimaryCategory>
    <StartPrice>1.0</StartPrice>
    <CategoryMappingAllowed>true</CategoryMappingAllowed>
    <Country>US</Country>
    <Currency>USD</Currency>
    <DispatchTimeMax>3</DispatchTimeMax>
    <ListingDuration>Days_7</ListingDuration>
    <ListingType>Chinese</ListingType>
    <PaymentMethods>PayPal</PaymentMethods>
    <PayPalEmailAddress>magicalbookseller@yahoo.com</PayPalEmailAddress>
    <PictureDetails>
      <PictureURL>http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007</PictureURL>
    </PictureDetails>
    <PostalCode>95125</PostalCode>
    <Quantity>1</Quantity>
    <ReturnPolicy>
      <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
      <RefundOption>MoneyBack</RefundOption>
      <ReturnsWithinOption>Days_30</ReturnsWithinOption>
      <Description>If you are not satisfied, return the book for refund.</Description>
      <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
    </ReturnPolicy>
    <ShippingDetails>
      <ShippingType>Flat</ShippingType>
      <ShippingServiceOptions>
        <ShippingServicePriority>1</ShippingServicePriority>
        <ShippingService>USPSMedia</ShippingService>
        <ShippingServiceCost>2.50</ShippingServiceCost>
      </ShippingServiceOptions>
    </ShippingDetails>
    <Site>US</Site>
  </Item>
</VerifyAddItemRequest>
"""

data = {
    "Item": {
        "Title": "Harry Potter and the Philosopher's Stone",
        "Description": "This is the first book in the Harry Potter series. In excellent condition!",
        "PrimaryCategory": { "CategoryID": "377" },
        "StartPrice": "1.0",
        "CategoryMappingAllowed": "true",
        "Condition": "3000",
        "Country": "US",
        "Currency": "USD",
        "DispatchTimeMax": "3",
        "ListingDuration": "Days_7",
        "ListingType": "Chinese",
        "PaymentMethods": "PayPal",
        "PayPalEmailAddress": "magicalbookseller@yahoo.com",
        "PictureDetails": { "PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007" },
        "PostalCode": "95125",
        "Quantity": "1",
        "ReturnPolicy": {
            "ReturnsAcceptedOption": "ReturnsAccepted",
            "RefundOption": "MoneyBack",
            "ReturnsWithinOption": "Days_30",
            "Description": "If you are not satisfied, return the book for refund.",
            "ShippingCostPaidByOption": "Buyer"
        },
        "ShippingDetails": {
            "ShippingType": "Flat",
            "ShippingServiceOptions": {
                "ShippingServicePriority": "1",
                "ShippingService": "USPSMedia",
                "ShippingServiceCost": "2.50"
            }
        },
        "Site": "US"
    }
}
print "%s" % xml2dict().fromstring(xml)
