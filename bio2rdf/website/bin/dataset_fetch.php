<?php 
/*
{"sEcho": <?php echo intval($_GET['sEcho']);?>,"iTotalRecords": 1,"iTotalDisplayRecords": 1,"aaData":[["-","aaa","url","title","desc"]]}
*/
/* ARC2 static class inclusion */ 
include_once('/code/arc/ARC2.php');

/* configuration */ 
$config = array(
//'remote_store_endpoint' => 'http://localhost:8890/sparql',
 'remote_store_endpoint' => 'http://bio2rdf.semanticscience.org:8007/sparql',
);

/* instantiation */
$store = ARC2::getRemoteStore($config);


$limit = 'LIMIT 10';
$offset = 'OFFSET 0';
$orderby = 'ORDER BY asc(?x)';

/** TOTAL NUMBER OF ENTRIES */
$select = 'SELECT count(?x) AS ?counts';
$where = 'WHERE {?x a <http://bio2rdf.org/serv:Dataset>}';
$rs = $store->query("$select $where");
if ($store->getErrors()) {
 print_r($store->getErrors());
 exit;
}
$iTotalRecords = $rs['result']['rows'][0]['counts'];

/** GET RELEVANT PAGED ENTRIES **/
$select = 'SELECT ?x';
$where = 'WHERE {?x a <http://bio2rdf.org/serv:Dataset>}';
$rs = $store->query("$select $where $orderby $limit $offset ");
if ($store->getErrors()) {
 print_r($store->getErrors());
 exit;
}
$aEntries = $rs['result']['rows'];
foreach($aEntries AS $entry) {
 $list[] = '?x = <'.$entry['x'].'>';
}
$iFilteredTotal = count($list);

/** GET THE VALUES FOR THE SELECTED ENTRIES **/
$select = 'SELECT *';
$where = 'WHERE {?x ?y ?z . FILTER ('.implode(" || ",$list).') }';
$q = "$select $where";
$rs = $store->query($q);
if ($store->getErrors()) {
 print_r($store->getErrors());
 exit;
}
$r = BuildResultArray($rs['result']['rows']);
echo count($r);
$sOutput = '{';
$sOutput .= '"sEcho": '.intval($_GET['sEcho']).', ';
$sOutput .= '"iTotalRecords": '.$iTotalRecords.', ';
$sOutput .= '"iTotalDisplayRecords": '.$iFilteredTotal.', ';
$sOutput .= '"aaData": [ ';
foreach($r AS $s => $aRow) {
	$sOutput .= "[";
	$sOutput .= '"'.addslashes($aRow['http://bio2rdf.org/serv:shortname']).'",';
	$sOutput .= '"'.addslashes($aRow['http://purl.org/dc/terms/title']).'",';
	$sOutput .= '"'.addslashes($aRow['http://purl.org/dc/terms/description']).'",';
	$sOutput .= '"'.addslashes($aRow['http://xmlns.com/foaf/0.1/homepage']).'",';
	$sOutput .= '""';
	$sOutput .= "],";
}
$sOutput = substr( $sOutput, 0, -1 );
$sOutput .= '] }';

file_put_contents("t.txt", $sOutput);
echo $sOutput;


function BuildResultArray($rows)
{
 foreach($rows AS $r) {
   $a[$r['x']][$r['y']] = $r['z'];
 }
 return $a;
}
	
?>