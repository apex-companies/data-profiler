DELETE FROM [OutputTables_Dev].[InboundDetails]
WHERE ProjectNumber_SKU like CONCAT(?, '%');