DELETE FROM [OutputTables_Prod].[InventoryData]
WHERE ProjectNumber_SKU like CONCAT(?, '%');