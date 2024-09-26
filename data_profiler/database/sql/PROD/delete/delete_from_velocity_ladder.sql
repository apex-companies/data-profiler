DELETE FROM [OutputTables_Prod].[VelocityLadder]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');