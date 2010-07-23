<?php

/**
 * FUNCTION CALLS
 **/
$xmlstr = getString("aptamerdb.xml");
$sxml = simplexml_load_string(utf8_encode($xmlstr));
$pArr = processEllingtonXML($sxml);
print_r($pArr);

/**
 * FUNCTIONS
 **/

function processEllingtonXML($anXml){
	/**
	 * return an array with the attributes of each record
	 **/
	$returnMe = array();
	foreach($anXml as $anEntry){
		foreach($entry[0]->attributes() as $a=>$b){
			if($a=="id"){
				$returnMe["id"] = $b;
			} elseif($a=="url"){
				$returnMe["url"] = $b;
			}
		}
	}
	return $returnMe;
}

function getString($filepath){
	$buf = "";
	$fh  = fopen($filepath, "r") or die("Could not open file");
	if($fh){
		while(!feof($fh)){
			$buf .= fgets($fh, 4096);
		}
	}
	fclose($fh);
	return $buf;
}
?>
