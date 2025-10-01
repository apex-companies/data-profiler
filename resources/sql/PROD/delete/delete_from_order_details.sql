DELETE od
FROM [OutputTables_Prod].[OrderDetails] od
    INNER JOIN [OutputTables_Prod].[ItemMaster] im
    ON od.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
WHERE im.[ProjectNumber] = ?;