DELETE od
FROM [OutputTables_Dev].[OrderDetails] od
    INNER JOIN [OutputTables_Dev].[ItemMaster] im
    ON od.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
WHERE im.[ProjectNumber] = ?;