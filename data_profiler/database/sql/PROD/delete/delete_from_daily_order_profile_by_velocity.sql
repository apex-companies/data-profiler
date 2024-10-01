DELETE FROM [OutputTables_Prod].[DailyOrderProfileByVelocity]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');