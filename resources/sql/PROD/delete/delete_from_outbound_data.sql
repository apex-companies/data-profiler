DELETE FROM [OutputTables_Prod].[OutboundData]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');