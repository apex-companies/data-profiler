--- Subwarehouse Material Flow - Pallets ----

DECLARE @ProjectNumber NVARCHAR(50) = ?,
        @UOM NVARCHAR(20) = ?,
        @DOHToStore INT = 10;

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
    FROM OutputTables_Prod.OutboundData od
        LEFT JOIN OutputTables_Prod.ItemMaster im
        ON od.ProjectNumber_SKU = im.ProjectNumber_SKU
    WHERE im.ProjectNumber = @ProjectNumber
);

DECLARE @DaysOfReceiving INT = (
    SELECT TOP (1) APPROX_COUNT_DISTINCT([ArrivalDate]) as days_of_receiving
    FROM OutputTables_Prod.InboundHeader
    WHERE ProjectNumber = @ProjectNumber
);


--- The Query ---
SELECT TOP (10) @ProjectNumber as [Project Number], im.SubWarehouse, COUNT(*) as SKUs, @UOM as [Unit of Measure], 
    @DaysOfReceiving as [Days of Receiving], ROUND(SUM(ib_by_sku.[Daily Lines]), 0) as [Daily IB Lines], ROUND(SUM(ib_by_sku.[Daily Qty]), 0) as [Daily IB Qty],
    ROUND(SUM(inv_by_sku.[Avg Inventory]), 0) as [Avg Total Inventory], 
    @DaysActive as [Days Active], ROUND(SUM(ob_by_sku.[Daily Lines]), 0) as [Daily OB Lines], ROUND(SUM(ob_by_sku.[Daily Qty]), 0) as [Daily OB Qty], 
    -- ROUND(SUM(ob_by_sku.[Daily Qty]), 0) * @DOHToStore as [DOH To Store],
    ROUND(AVG(im.PalletWidth), 2) as [Avg Pallet Width], ROUND(AVG(im.PalletLength), 2) as [Avg Pallet Length], ROUND(AVG(im.PalletHeight), 2) as [Avg Pallet Height], ROUND(AVG(im.PalletWeight), 2) as [Avg Pallet Weight],
    MAX(im.PalletWidth) as [Max Pallet Width], MAX(im.PalletLength) as [Max Pallet Length], MAX(im.PalletHeight) as [Max Pallet Height], MAX(im.PalletWeight) as [Max Pallet Weight]
FROM OutputTables_Prod.ItemMaster im
    LEFT JOIN (
        SELECT ib.ProjectNumber_SKU, ROUND(COUNT(*) / CAST(@DaysOfReceiving as Float), 2) as [Daily Lines], ROUND(SUM(ib.Quantity) / CAST(@DaysOfReceiving as Float), 2) as [Daily Qty]
        FROM OutputTables_Prod.InboundDetails ib
            LEFT JOIN OutputTables_Prod.ItemMaster im2
            ON ib.ProjectNumber_SKU = im2.ProjectNumber_SKU
        WHERE im2.ProjectNumber = @ProjectNumber and ib.UnitOfMeasure = @UOM
        GROUP BY ib.ProjectNumber_SKU
    ) ib_by_sku
    ON im.ProjectNumber_SKU = ib_by_sku.ProjectNumber_SKU
    LEFT JOIN (
        SELECT inv.ProjectNumber_SKU, ROUND(SUM(inv.Qty) / CAST(@PeriodsOfInventory as Float), 2) as [Avg Inventory]
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
        SELECT od.ProjectNumber_SKU, ROUND(COUNT(*) / CAST(@DaysActive as Float), 2) as [Daily Lines], ROUND(SUM(od.Quantity) / CAST(@DaysActive as Float), 2) as [Daily Qty]
        FROM OutputTables_Prod.OutboundData od
            LEFT JOIN OutputTables_Prod.ItemMaster im1
            ON od.ProjectNumber_SKU = im1.ProjectNumber_SKU
        WHERE im1.ProjectNumber = @ProjectNumber and od.UnitOfMeasure = @UOM
        GROUP BY od.ProjectNumber_SKU
    ) ob_by_sku
    ON im.ProjectNumber_SKU = ob_by_sku.ProjectNumber_SKU
WHERE im.ProjectNumber = @ProjectNumber
GROUP BY im.SubWarehouse