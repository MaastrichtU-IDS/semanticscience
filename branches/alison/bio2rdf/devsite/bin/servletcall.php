<?php

$fh = null;
$o ="";
$url = "http://s3.semanticscience.org:8080/searchBio2rdf/search/SearchBio2rdf?query=";

if($_GET["ns"] !== null){
	$qry = $_GET["query"];
	$ns = $_GET["ns"];	
	$fh = fopen($url.$qry."&ns=".$ns,"r");	
} else {
	$qry = $_GET["query"];
	$fh = fopen($url.$qry,"r");
}

if($fh){
	while(!feof($fh)){
		$l = fgets($fh, 4096);
		$o .= $l;
		}
}
echo $o;
?>
