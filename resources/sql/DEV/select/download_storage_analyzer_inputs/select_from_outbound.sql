SELECT oh.[OrderNumber]
    ,oh.[Date]
    ,im.[SKU]
    ,od.[Quantity]
FROM [OutputTables_Dev].[ItemMaster] im 
    INNER JOIN [OutputTables_Dev].[OrderDetails] od 
        ON im.[ProjectNumber_SKU] = od.[ProjectNumber_SKU]
    INNER JOIN [OutputTables_Dev].[OrderHeader] oh 
        ON od.[ProjectNumber_OrderNumber] = oh.[ProjectNumber_OrderNumber]
WHERE im.ProjectNumber = ?