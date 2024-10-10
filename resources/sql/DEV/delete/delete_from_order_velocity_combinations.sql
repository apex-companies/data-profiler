DELETE FROM [OutputTables_Dev].[OrderVelocityCombinations]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');