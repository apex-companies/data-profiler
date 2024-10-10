DELETE FROM [OutputTables_Dev].[DailyOrderProfileByVelocity]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[VelocityByMonth]
WHERE ProjectNumber_SKU like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[VelocityLadder]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[VelocitySummary]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[OrderVelocityCombinations]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[OutboundDataByOrder]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[OutboundData]
WHERE ProjectNumber_OrderNumber like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[InventoryData]
WHERE ProjectNumber_SKU like CONCAT(?, '%');

DELETE FROM [OutputTables_Dev].[ProjectNumber_OrderNumber]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Dev].[ProjectNumber_Velocity]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Dev].[ItemMaster]
WHERE ProjectNumber = ?;

DELETE FROM [OutputTables_Dev].[Project]
WHERE ProjectNumber = ?;