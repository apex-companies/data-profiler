SELECT ons.[OrderNumber]
    ,o.[Date]
    ,im.[SKU]
    ,o.[Quantity]
FROM [OutputTables_Prod].[ItemMaster] im 
    INNER JOIN [OutputTables_Prod].[OutboundData] o 
    ON o.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
    INNER JOIN [OutputTables_Prod].[ProjectNumber_OrderNumber] ons 
    ON o.[ProjectNumber_OrderNumber] = ons.[ProjectNumber_OrderNumber]
WHERE im.ProjectNumber = ?