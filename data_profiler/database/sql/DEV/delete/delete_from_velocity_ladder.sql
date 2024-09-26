DELETE FROM [OutputTables_Dev].[VelocityLadder]
WHERE ProjectNumber_Velocity like CONCAT(?, '%');