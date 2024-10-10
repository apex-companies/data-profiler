DELETE FROM [OutputTables_Dev].[OutboundData]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');