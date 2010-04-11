<?php

if($argc < 3){
	die("Usage: getPDBByMolType.php <-protein Y|N> <-dna Y|N> <-rna Y|N> <-hybrid Y|N>\n");
}//if
else{
	if($argv[1] == "-protein" && $argv[3] == "-dna" && $argv[5] =="-rna" && $argv[7] == "-hybrid"){
		$optionArr["containsProtein"] = $argv[2];
		$optionArr["containsDna"] = $argv[4];
		$optionArr["containsRna"] = $argv[6];
		$optionArr["containsHybrid"] =$argv[8];
		require_once("MyXmlWriter.php");
		$qArr = makeQueryArr($optionArr);
		$xmlQuery = writeXMLQuery($qArr);
		$url = "http://www.rcsb.org/pdb/rest/search";
		$response = executeQuery($xmlQuery, $url);
		$rArr = explode("\n", trim($response));
		
		print_r($rArr);
	}else{
		die("Usage: getPDBByMolType.php <-protein Y|N> <-dna Y|N> <-rna Y|N> <-hybrid Y|N>\n");	
	}//else

}//else


function executeQuery($aQry, $url){
	$ch = curl_init();    // initialize curl handle
	curl_setopt($ch, CURLOPT_URL,$url); // set url to post to
	curl_setopt($ch, CURLOPT_RETURNTRANSFER,1); // return into a variable
	curl_setopt($ch, CURLOPT_TIMEOUT, 4); // times out after 4s
	curl_setopt($ch, CURLOPT_POSTFIELDS, $aQry); // add POST fields
	$result = curl_exec($ch); // run the whole process
	return $result;
}//executeQuery

function writeXMLQuery($qArr){
        $xml = new MyXmlWriter();
        $xml->push('orgPdbQuery');
        foreach($qArr as $a){
                $xml->element($a[0], $a[1]);
        }//foreach      
        $xml->pop();
        return $xml->getXml();
}//writeXML


function makeQueryArr($arr){
//This function makes the query array that is ready for writeXMl
	$returnMe = array(
        	array("queryType", "org.pdb.query.simple.ChainTypeQuery"),
        	array("containsProtein","-"),
        	array("containsDna","-"),
        	array("containsRna", "-"),
        	array("containsHybrid","-"),
	);

	foreach($arr as $k=>$v){
		if($k == "containsProtein"){
			$returnMe[1][1] = $v;
		}//if
		if($k == "containsDna"){
			$returnMe[2][1] = $v;
		}//if
		if($k == "containsRna"){
			$returnMe[3][1] = $v;
		}//if
		if($k == "containsHybrid"){
			$returnMe[4][1] = $v;
		}//if
	}//foreach
	return $returnMe;
}//makeQueryArr

?>
