DELETE FROM [OutputTables_Prod].[VelocitySummary]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');