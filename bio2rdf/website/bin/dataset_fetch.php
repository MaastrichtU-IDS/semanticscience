<?php 
/* ARC2 static class inclusion */ 
include_once('/code/arc/ARC2.php');

/* configuration */ 
$config = array(
 'remote_store_endpoint' => // 'http://localhost:8890/sparql',
							   'http://bio2rdf.semanticscience.org:8007/sparql',
);

/* instantiation */
$store = ARC2::getRemoteStore($config);

/** PARAMETERS **/
$sSearch = '';
if(isset($_GET['sSearch'])) $sSearch = trim($_GET['sSearch']);
/*if($sSearch) $search_filter = ' ?x ?p ?o . ?o <bif:contains> "'.$sSearch.'" . 
 FILTER (?p = <http://purl.org/dc/terms/title> || ?p = <http://bio2rdf.org/serv:shortname>) ';
*/
if($sSearch) {
 $a = explode(" ",trim($sSearch));
 $search_filter = ' ?x ?p ?o . ';
 foreach($a AS $term) {
   $search_filter .= ' FILTER regex(?o, "'.$term.'") . ';
 }
 $search_filter .= ' FILTER (?p = <http://purl.org/dc/terms/title> || ?p = <http://bio2rdf.org/serv:shortname>) ';
}
 
$limit = '10';
if(isset($_GET['iDisplayLength']) && is_numeric($_GET['iDisplayLength'])) $limit = trim($_GET['iDisplayLength']);
$limit = 'LIMIT '.$limit;

$offset = '0';
if(isset($_GET['iDisplayStart']) && is_numeric($_GET['iDisplayStart'])) $offset = trim($_GET['iDisplayStart']);
$offset = 'OFFSET '.$offset;

$aRow['http://bio2rdf.org/serv:shortname'];
  $row[] = '';//trim($aRow['http://xmlns.com/foaf/0.1/homepage']);
  $row[] = trim($aRow['http://purl.org/dc/terms/title']);
  $row[] = '';//$aRow['http://purl.org/dc/terms/description'];

// sorting
$cols = array(
	'',
	'http://bio2rdf.org/serv:shortname',
	'http://xmlns.com/foaf/0.1/homepage',
	'http://purl.org/dc/terms/title',
	'http://purl.org/dc/terms/description'
);

$orderby = 'ORDER BY asc(?x)';
 if(isset($_GET['sSortDir_0'])) {
   $orderby = 'ORDER BY '.$_GET['sSortDir_0'].'(?x)';
}
//JSONDebug($orderby);


/** TOTAL NUMBER OF ENTRIES */
$select = 'SELECT count(?x) AS ?counts';
$where = 'WHERE {?x a <http://bio2rdf.org/serv:Dataset>}';
$rs = $store->query("$select $where");
if ($store->getErrors()) {
 JSONDebug("1".var_dump($store->getErrors()));
 exit;
}
$iTotalRecords = $rs['result']['rows'][0]['counts'];

if($sSearch) {
 /** TOTAL NUMBER OF SEARCH-FILTERED ENTRIES **/
 $q = 'SELECT COUNT(?x) AS ?counts 
 WHERE {
  ?x a ?t . '.$search_filter.' 
  FILTER (?t = <http://bio2rdf.org/serv:Dataset>) }
  ';
 $rs = $store->query($q);
 if ($store->getErrors()) {
  echo '2:'.var_dump($store->getErrors());
  exit;
 }
 $iFilteredTotal = $rs['result']['rows'][0]['counts'];
} else $iFilteredTotal = $iTotalRecords;

/** GET RELEVANT PAGED ENTRIES **/
$select = 'SELECT DISTINCT ?x';
$where = 'WHERE {?x a <http://bio2rdf.org/serv:Dataset> ;
  <http://bio2rdf.org/serv:shortname> ?prefix . '.$search_filter.'} ';
//$orderby = "ORDER BY asc(?x)";

$q = "$select $where $orderby $limit $offset";
$rs = $store->query($q);
if ($store->getErrors()) {
 echo '3:'.var_dump($store->getErrors());
 exit;
}
$aEntries = $rs['result']['rows'];
foreach($aEntries AS $entry) {
 $list[] = '?x = <'.$entry['x'].'>';
}
$iPageTotal = count($list);


/** GET THE VALUES FOR THE SELECTED ENTRIES **/
if($iPageTotal) {
 $select = 'SELECT *';
 $where = 'WHERE {?x ?y ?z . FILTER ('.implode(" || ",$list).')} ';
// $orderby = 'ORDER BY asc(?x)';
 $q = "$select $where $orderby";
 $rs = $store->query($q);
 if ($store->getErrors()) {
  echo '4:'.var_dump($store->getErrors());
  exit;
 }
 // organize the triples
 $r = '';
 foreach($rs['result']['rows'] AS $a) {
   $r[$a['x']][$a['y']] = $a['z'];
 }
}


/** BUILD THE JSON **/
$json['sEcho'] = intval($_GET['sEcho']);
$json['iTotalRecords'] = intval($iTotalRecords);
$json['iTotalDisplayRecords'] = intval($iFilteredTotal);
if($r) {
 foreach($r AS $s => $aRow) {
  $row = '';
  $row[] = '';
  $row[] = $aRow['http://bio2rdf.org/serv:shortname'];
  $row[] = '';//trim($aRow['http://xmlns.com/foaf/0.1/homepage']);
  $row[] = trim($aRow['http://purl.org/dc/terms/title']);
  $row[] = '';//$aRow['http://purl.org/dc/terms/description'];
  $data[] = $row;
 }
} else $data = '';
$json['aaData'] = $data;
echo json_encode($json);

function JSONDebug($error)
{
$json['sEcho'] = intval($_GET['sEcho']);
$json['iTotalRecords'] = 1;
$json['iTotalDisplayRecords'] = 1;

$row[] = '';
$row[] = '';
$row[] = '';
$row[] = $error;
$row[] = '';
$data[] = $row;

$json['aaData'] = $data;
echo json_encode($json);
exit;
}
	
?>