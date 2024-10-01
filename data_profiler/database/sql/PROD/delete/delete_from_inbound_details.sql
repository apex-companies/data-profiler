DELETE FROM [OutputTables_Prod].[InboundDetails]
WHERE ProjectNumber_SKU like CONCAT(?, '%');