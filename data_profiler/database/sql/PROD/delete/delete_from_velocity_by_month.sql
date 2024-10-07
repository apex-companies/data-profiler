DELETE FROM [OutputTables_Prod].[VelocityByMonth]
WHERE ProjectNumber_SKU like CONCAT(?, '%');