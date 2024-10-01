DELETE FROM [OutputTables_Prod].[OutboundDataByOrder]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');