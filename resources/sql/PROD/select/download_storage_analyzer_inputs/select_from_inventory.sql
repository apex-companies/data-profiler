SELECT i.[Period]
    ,im.[SKU]
    ,im.[UnitOfMeasure]
    ,i.[Quantity] 
FROM [OutputTables_Prod].[InventoryData] i
    INNER JOIN [OutputTables_Prod].[ItemMaster] im 
    ON i.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
WHERE im.[ProjectNumber] = ?