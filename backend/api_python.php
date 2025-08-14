<?php // TODO - not sure if it works, needs testing

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

// MySQL настройки
$host = 'localhost';
$username = 'kvbbgcom_jarvis_hub';
$password = 'kv0889909595';
$dbname = 'kvbbgcom_jarvis_hub';

$mysqli = new mysqli($host, $user, $pass, $db);
if ($mysqli->connect_error) {
    http_response_code(500);
    echo json_encode(["status"=>"error","message"=>$mysqli->connect_error]);
    exit;
}
$mysqli->set_charset("utf8mb4");

$input = json_decode(file_get_contents("php://input"), true);
$action = $input["action"] ?? null;

function safe_col($s) { return preg_match('/^[A-Za-z0-9_]+$/', $s); }
function now_utc() { return gmdate("Y-m-d H:i:s"); }

// Списък таблици и ключови колони:
$PK = [
  "Devices"    => ["DeviceMAC"],
  "DeviceType" => ["TypeID"],
  "Relay"      => ["DeviceMACID","TimeOfRecord"],
  "DHT"        => ["DeviceMACID","TimeOfRecord"],
  "RGB"        => ["DeviceMACID","TimeOfRecord"],
  "IR"         => ["DeviceMACID","TimeOfRecord"],
  "Accounts"   => ["Type"]
];

if ($action === "pull_changes") {
    $table   = $input["table"] ?? "";
    $since   = $input["since"] ?? "1970-01-01 00:00:00";
    if (!$table || !isset($PK[$table]) || !safe_col($table)) {
        echo json_encode(["status"=>"error","message"=>"invalid table"]);
        exit;
    }
    // Връщаме всичко, което е по-ново от 'since' (вкл. Deleted=1 – за да се приложи soft delete)
    $stmt = $mysqli->prepare("SELECT * FROM `$table` WHERE UpdatedAt > ? ORDER BY UpdatedAt ASC");
    $stmt->bind_param("s", $since);
    $stmt->execute();
    $res = $stmt->get_result();
    $rows = [];
    while ($row = $res->fetch_assoc()) { $rows[] = $row; }
    echo json_encode(["status"=>"success","table"=>$table,"count"=>count($rows),"rows"=>$rows]);
    exit;
}

if ($action === "push_changes") {
    $table   = $input["table"] ?? "";
    $records = $input["records"] ?? [];
    if (!$table || !isset($PK[$table]) || !safe_col($table) || !is_array($records)) {
        echo json_encode(["status"=>"error","message"=>"invalid push payload"]);
        exit;
    }
    // За всяка колона в първия запис изграждаме INSERT ... ON DUPLICATE KEY UPDATE
    $count = 0;
    foreach ($records as $row) {
        if (!is_array($row)) continue;
        // гарантираме UpdatedAt
        if (!isset($row["UpdatedAt"]) || !$row["UpdatedAt"]) {
            $row["UpdatedAt"] = now_utc();
        }
        // ключови колони трябва да присъстват
        $all_pk_present = true;
        foreach ($PK[$table] as $k) { if (!array_key_exists($k, $row)) { $all_pk_present = false; break; } }
        if (!$all_pk_present) continue;

        // build columns
        $cols = array_keys($row);
        $placeholders = implode(",", array_fill(0, count($cols), "?"));
        $colnames = "`" . implode("`,`", $cols) . "`";
        $types = str_repeat("s", count($cols)); // всичко като string за простота

        // ON DUPLICATE: само ако входният UpdatedAt е по-нов
        // Трик: правим UPDATE така, че да се обнови само когато VALUES(UpdatedAt) > target.UpdatedAt
        $updates = [];
        foreach ($cols as $c) {
            if (in_array($c, $PK[$table])) continue; // не обновяваме PK
            $updates[] = "`$c`=IF(VALUES(UpdatedAt) > `UpdatedAt`, VALUES(`$c`), `$c`)";
        }
        $upd_sql = implode(",", $updates);

        $sql = "INSERT INTO `$table` ($colnames) VALUES ($placeholders)
                ON DUPLICATE KEY UPDATE $upd_sql";

        $stmt = $mysqli->prepare($sql);
        $vals = array_values($row);
        $stmt->bind_param($types, ...$vals);
        $ok = $stmt->execute();
        if ($ok) $count++;
    }
    echo json_encode(["status"=>"success","table"=>$table,"upserted"=>$count]);
    exit;
}

echo json_encode(["status"=>"error","message"=>"unknown action"]);

