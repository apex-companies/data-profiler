DELETE FROM [OutputTables_Prod].[OrderVelocityCombinations]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');