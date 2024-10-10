DELETE FROM [OutputTables_Prod].[DailyOrderProfileByVelocity]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[VelocityByMonth]
WHERE ProjectNumber_SKU like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[VelocityLadder]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[VelocitySummary]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[OrderVelocityCombinations]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[OutboundDataByOrder]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[OutboundData]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[InventoryData]
WHERE ProjectNumber_SKU like CONCAT(?, '%');

DELETE FROM [OutputTables_Prod].[ProjectNumber_OrderNumber]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Prod].[ProjectNumber_Velocity]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Prod].[ItemMaster]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Prod].[Project]
WHERE ProjectNumber = ?;