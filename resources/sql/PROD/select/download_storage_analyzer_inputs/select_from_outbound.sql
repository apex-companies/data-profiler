SELECT oh.[OrderNumber]
    ,oh.[Date]
    ,im.[SKU]
    ,od.[Quantity]
FROM [OutputTables_Prod].[ItemMaster] im 
    INNER JOIN [OutputTables_Prod].[OrderDetails] od 
        ON im.[ProjectNumber_SKU] = od.[ProjectNumber_SKU]
    INNER JOIN [OutputTables_Prod].[OrderHeader] oh 
        ON od.[ProjectNumber_OrderNumber] = oh.[ProjectNumber_OrderNumber]
WHERE im.ProjectNumber = ?