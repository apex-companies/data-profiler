SELECT i.[Period]
    ,im.[SKU]
    ,im.[UnitOfMeasure]
    ,i.[Quantity] 
FROM [OutputTables_Dev].[InventoryData] i
    INNER JOIN [OutputTables_Dev].[ItemMaster] im 
    ON i.[ProjectNumber_SKU] = im.[ProjectNumber_SKU]
WHERE im.[ProjectNumber] = ?