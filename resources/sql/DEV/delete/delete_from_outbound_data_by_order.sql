DELETE FROM [OutputTables_Dev].[OutboundDataByOrder]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');