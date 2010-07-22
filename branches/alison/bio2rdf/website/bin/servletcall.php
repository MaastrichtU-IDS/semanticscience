<?php

include('config.php');

$fh = null;
$o ="";

if($_GET["ns"] !== null){
	$qry = $_GET["query"];
	$ns = $_GET["ns"];	
	$fh = fopen($servlet_url.urlencode($qry)."&ns=".urlencode($ns),"r");	

} else {
	$qry = $_GET["query"];
	$fh = fopen($servlet_url.urlencode($qry),"r");
}


if($fh){
  while(!feof($fh)){
	$l = fgets($fh, 4096);
	$o .= $l;
  }//while
}//if

echo $o;

?>
