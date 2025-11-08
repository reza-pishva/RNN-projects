<?php
// اتصال به SQL Server با Windows Authentication
$serverName = "10WKS-PISHVA";
$connectionOptions = [
    "Database" => "PEGAH",
    "Authentication" => SQLSRV_AUTH_INTEGRATED
];

$conn = sqlsrv_connect($serverName, $connectionOptions);

if (!$conn) {
    die(print_r(sqlsrv_errors(), true));
}

// لیست AssetID ها
$assetIDs = [8341, 8342, 8343, 8344, 8346, 9286, 9287];

// آرایه برای نگهداری مقادیر
$values = [];

foreach ($assetIDs as $id) {
    $sql = "
        SELECT TOP 1 [Value]
        FROM [PEGAH].[PDA].[Periodic_Values]
        WHERE [AssetID] = ?
        ORDER BY [DateTime] DESC
    ";

    $params = [$id];
    $stmt = sqlsrv_query($conn, $sql, $params);

    if ($stmt && sqlsrv_fetch($stmt)) {
        $value = sqlsrv_get_field($stmt, 0);
        $values["AssetID_$id"] = $value;
    } else {
        $values["AssetID_$id"] = null;
    }
}

// نمایش متغیرها
foreach ($values as $key => $val) {
    echo "$key = $val\n";
}

// بستن اتصال
sqlsrv_close($conn);
?>
