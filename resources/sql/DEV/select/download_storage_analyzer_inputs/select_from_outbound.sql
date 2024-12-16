SELECT ons.[OrderNumber]
    ,o.[Date]
    ,im.[SKU]
    ,o.[Quantity]
FROM [OutputTables_Dev].[ItemMaster] im 
    INNER JOIN [OutputTables_Dev].[OutboundData] o 
    ON o.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
    INNER JOIN [OutputTables_Dev].[ProjectNumber_OrderNumber] ons 
    ON o.[ProjectNumber_OrderNumber] = ons.[ProjectNumber_OrderNumber]
WHERE im.ProjectNumber = ?