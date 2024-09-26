DELETE FROM [OutputTables_Dev].[InventoryData]
WHERE ProjectNumber_SKU like CONCAT(?, '%');