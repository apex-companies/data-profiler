DELETE FROM [OutputTables_Dev].[VelocityByMonth]
WHERE ProjectNumber_SKU like CONCAT(?, '%');