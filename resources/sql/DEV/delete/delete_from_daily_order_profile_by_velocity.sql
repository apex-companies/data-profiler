DELETE FROM [OutputTables_Dev].[DailyOrderProfileByVelocity]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');