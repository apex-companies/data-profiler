---- Items Material Flow ----

-- Inputs --
DECLARE @ProjectNumber NVARCHAR(50) = ?,
        @UOM NVARCHAR(20) = ?;

-- Set some variables --
DECLARE @PeriodsOfInventory INT = (
    SELECT TOP (1) APPROX_COUNT_DISTINCT(id.Period)
    FROM OutputTables_Prod.InventoryData id
        LEFT JOIN OutputTables_Prod.ItemMaster im
        ON id.ProjectNumber_SKU = im.ProjectNumber_SKU
    WHERE im.ProjectNumber = @ProjectNumber
);

DECLARE @DaysActive INT = (
    SELECT TOP (1) APPROX_COUNT_DISTINCT([Date]) as days_active
    FROM OutputTables_Prod.OrderHeader
    WHERE ProjectNumber = @ProjectNumber
);

DECLARE @DaysOfReceiving INT = (
    SELECT TOP (1) APPROX_COUNT_DISTINCT([ArrivalDate]) as days_of_receiving
    FROM OutputTables_Prod.InboundHeader
    WHERE ProjectNumber = @ProjectNumber
);

--- The Query ---
SELECT @ProjectNumber as [Project Number], im.SKU, im.SKUDescription, im.SKUClass, im.ProductLine, im.Velocity, @UOM as [Unit of Measure], 
    @DaysOfReceiving as [Days of Receiving], ROUND(ib_by_sku.Qty / @DaysOfReceiving, 2) as [IB Qty per Day], ib_by_sku.Qty as [Total IB Qty],
    inv_by_sku.[Avg Inventory], inv_by_sku.[Max Inventory], 
    @DaysActive as [Active Days], ROUND(ob_by_sku.Qty / @DaysActive, 2) as [OB Qty per Day], ob_by_sku.Qty as [Total OB Qty]
FROM OutputTables_Prod.ItemMaster im
    LEFT JOIN (
        SELECT inv.ProjectNumber_SKU, ROUND(SUM(inv.Qty) / CAST(@PeriodsOfInventory as Float), 2) as [Avg Inventory], MAX(inv.Qty) as [Max Inventory]
        FROM (
            SELECT id.[Period], id.ProjectNumber_SKU, SUM(id.Quantity) as Qty
            FROM OutputTables_Prod.InventoryData id
            WHERE id.UnitOfMeasure = @UOM
            GROUP BY id.[Period], id.ProjectNumber_SKU
        ) inv
        GROUP BY inv.ProjectNumber_SKU
    ) inv_by_sku
    ON im.ProjectNumber_SKU = inv_by_sku.ProjectNumber_SKU
    LEFT JOIN (
        SELECT od.ProjectNumber_SKU, ROUND(SUM(od.Quantity), 2) as Qty
        FROM OutputTables_Prod.OrderDetails od
            LEFT JOIN OutputTables_Prod.OrderHeader oh
            ON od.ProjectNumber_OrderNumber = oh.ProjectNumber_OrderNumber
        WHERE oh.ProjectNumber = @ProjectNumber and od.UnitOfMeasure = @UOM
        GROUP BY od.ProjectNumber_SKU
    ) ob_by_sku
    ON im.ProjectNumber_SKU = ob_by_sku.ProjectNumber_SKU
    LEFT JOIN (
        SELECT ib.ProjectNumber_SKU, ROUND(SUM(ib.Quantity), 2) as Qty
        FROM OutputTables_Prod.InboundDetails ib
            LEFT JOIN OutputTables_Prod.ItemMaster im2
            ON ib.ProjectNumber_SKU = im2.ProjectNumber_SKU
        WHERE im2.ProjectNumber = @ProjectNumber and ib.UnitOfMeasure = @UOM
        GROUP BY ib.ProjectNumber_SKU
    ) ib_by_sku
    ON im.ProjectNumber_SKU = ib_by_sku.ProjectNumber_SKU
WHERE im.ProjectNumber = @ProjectNumber
ORDER BY [IB Qty per Day] DESC



