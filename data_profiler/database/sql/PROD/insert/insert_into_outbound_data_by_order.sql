INSERT INTO [OutputTables_Prod].[OutboundDataByOrder] ([Date]
      ,[Lines]
      ,[Units]
      ,[SKUs]
      ,[LinesPerOrderRange]
      ,[UnitsPerOrderRange]
      ,[Weekday]
      ,[Weekday_Idx]
      ,[ProjectNumber_OrderNumber])
VALUES (?,?,?,?,?,?,?,?,?);