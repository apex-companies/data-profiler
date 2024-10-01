DELETE FROM [OutputTables_Dev].[VelocitySummary]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');