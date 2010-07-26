<?php
$aptamerUrl = "http://mcbc.usm.edu/riboaptDB/data/aptamer.txt";
$ribozymeUrl = "http://mcbc.usm.edu/riboaptDB/data/ribozyme.txt";
$targetUrl = "http://mcbc.usm.edu/riboaptDB/data/target.txt";
$experimentUrl = "http://mcbc.usm.edu/riboaptDB/data/experiment.txt";
$publicationUrl = "http://mcbc.usm.edu/riboaptDB/data/publication.txt";


$aptStr = getUrl($aptamerUrl);
$aptArr = parseAptamers($aptStr);
$riboStr = getUrl($ribozymeUrl);
$riboArr = parseRibozymes($riboStr);
$targetStr = getUrl($targetUrl);
$targetArr = parseTargets($targetStr);
$experimentStr = getUrl($experimentUrl);
$experimentArr = parseExperiments($experimentStr);
$pubStr = getUrl($publicationUrl);
$pubArr = parsePublication($pubStr);




/**
 * FUNCTIONS
 */

function parsePublication($pubStr){
	/* Returns a key value pair array for the contents of $pubStr */
	$arrCoarse = explode("\n", $pubStr);
	//remove the first line
	$a = array_shift($arrCoarse);

	$returnMe = array();
	foreach($arrCoarse as $aLine){
		$lineArr = array();
		$lineArr = explode("\t", $aLine);
		//I WILL ONLY STORE THE PMID
		if(isset($lineArr[8])){
			if((strlen($lineArr[8])!=0)){
				$returnMe[trim($lineArr[0])]["pmid"] = trim($lineArr[8]);
			}//if
		}//if
	}//foreach
	return $returnMe;
}

function parseExperiments($experimentStr){
	/* Returns a key value pair array for the contents of $targetStr */
	$arrCoarse = explode("\n", $experimentStr);
	//remove the first line
	$a = array_shift($arrCoarse);

	$returnMe = array();
	foreach($arrCoarse as $aLine){
		$lineArr = array();
		$lineArr = explode("\t", $aLine);
		
		if((strlen($lineArr[0])!=0) &&
			(strlen($lineArr[1]) != 0)){
			$returnMe[trim($lineArr[0])]["template"] = trim($lineArr[1]);
			$returnMe[trim($lineArr[0])]["template_desc"] = trim($lineArr[2]);
			$returnMe[trim($lineArr[0])]["nucleic_type"] = trim($lineArr[3]);
			$returnMe[trim($lineArr[0])]["experimental_condition"] = trim($lineArr[4]);
			$returnMe[trim($lineArr[0])]["target_id"] = trim($lineArr[5]);
		}//if
		 
	}//foreach
	return $returnMe;
}

function parseTargets($targetStr){
	/* Returns a key value pair array for the contents of $targetStr */
	$arrCoarse = explode("\n", $targetStr);
	//remove the first line
	$a = array_shift($arrCoarse);
	
	/* traverse the array,
	 * separate the identifier 
	 * separate the target name
	 * separate the target type
	 *  */
	$returnMe = array();
	foreach($arrCoarse as $aLine){
		$lineArr = array();
		$lineArr = explode("\t", $aLine);
		if((strlen($lineArr[0])!=0) &&
			(strlen($lineArr[1]) != 0) &&
			(strlen($lineArr[2]) != 0)){
				$returnMe[trim($lineArr[0])]["target_name"] = trim($lineArr[1]);
				$returnMe[trim($lineArr[0])]["target_category"] = trim($lineArr[2]);
		}//if
	}//foreach
	return $returnMe;
}

function parseRibozymes($riboStr){
	/* Returns a key value pair array for the contents of $riboStr */
	$arrCoarse = explode("\n", $riboStr);
	//remove the first line
	$a = array_shift($arrCoarse);
	
	/* traverse the array,
	 * separate the identifier from the sequence
	 * then populate get the ribozyme type
	 * finally the returned array
	 *  */
	$returnMe = array();
	foreach($arrCoarse as $aLine){
		$lineArr = array();
		$lineArr = explode("\t", $aLine);
		if((strlen($lineArr[0])!=0) &&
			(strlen($lineArr[1]) != 0) &&
			(strlen($lineArr[2]) != 0)){
			$returnMe[trim($lineArr[0])]["type"] = trim($lineArr[1]);
			$returnMe[trim($lineArr[0])]["sequence"] = trim($lineArr[2]);
		}//if
	}//foreach
	return $returnMe;
}
 
function parseAptamers($aptStr){
	/* Returns a key value pair array for the contents of $aptStr */
	$arrCoarse = explode("\n", $aptStr);
	//remove the first line
	$a = array_shift($arrCoarse);
	/* traverse the array,
	 * separate the identifier from the sequence
	 * and then populate the returned array
	 *  */
	$returnMe = array();
	foreach ($arrCoarse as $aLine){
		$lineArr = array();
		$lineArr = explode("\t", $aLine);
		if((strlen($lineArr[0]) != 0) && (strlen($lineArr[1]) != 0)){
			$returnMe[trim($lineArr[0])] = trim($lineArr[1]);
		}
		 
	}
	return $returnMe;
} 


function getUrl($url){
	/* This function returns a string with the contents of a URL */
	$contents = "";
	$fh = fopen($url, "r");
	if($fh){
		while(!feof($fh)){
			$contents .= fgets($fh, 4096);
		}
	}
	fclose($fh);
	return $contents;
}

?>
