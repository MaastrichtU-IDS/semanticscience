<?php

include('config.php');

$fh = null;
$o ="";

if($_GET["ns"] !== null){
	$qry = $_GET["query"];
	$ns = $_GET["ns"];	
	$fh = fopen($servlet_url.$qry."&ns=".$ns,"r");	
} else {
	$qry = $_GET["query"];
	$fh = fopen($servlet_url.$qry,"r");
}

if($fh){
	while(!feof($fh)){
		$l = fgets($fh, 4096);
		$o .= $l;
		}
}
echo $o;
?>
