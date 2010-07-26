<?php

/**
 * FUNCTION CALLS
 **/
$xmlstr = getString("aptamerdb.xml");
$sxml = simplexml_load_string(utf8_encode($xmlstr));
$pArr = processEllingtonXML($sxml);
createTabdelimited($pArr,"output.csv");

/**
 * FUNCTIONS
 **/

function createTabdelimited($anArr, $filename){
	$fh = fopen($filename, "w");
	$buf =""; //a line in the tab delimited file
	foreach($anArr as $id=>$data){
		$sequences = array();
		$row = array(
			"id" => "",
			"type"=>"",
			"ligandtype"=>"",
			"ligand"=> "",
			"pmid" =>"",
			"url"=>"",
			"template"=> ""
			);
		$row["id"] = $id;
		foreach($data as $k=>$v){
			if(isset($row[$k])){
				$row[$k] = $v;
			}else{
				$pattern = "/sequence_\d+/";
				preg_match($pattern, $k, $matches);
				if(count($matches)){
					$sequences[]=$v;
				}	
			}
		}
		$result = array_merge($row, $sequences);
		foreach($result as $r => $v){
			$buf .= $v."\t";
		}
		$buf .= "\n";
	}	
	fwrite($fh, $buf);
}

function processEllingtonXML($anXml){
	/**
	 * return an array with the attributes of each record
	 **/
	$returnMe = array();
	
	foreach($anXml as $anEntry){
		//first get the id
		$id = (string)$anEntry->attributes()->id;
		//check if the id exists
		if(!strlen($id)){
			echo "error";
			exit;
		}
		
		//get the template sequence
		$template = (string) $anEntry->experiment->template->attributes()->value;
		$returnMe[$id]["template"] = $template;
		
		//get the aptamer sequences
		$seqCount = 1;
		foreach($anEntry->experiment->sequence as $a){
			$sequence = (string)$a->attributes()->value;
			if(strlen($sequence)){
				$returnMe[$id]["sequence_".$seqCount] =  $sequence;
				$seqCount ++;
			}
		}
				
		foreach($anEntry[0]->attributes() as $a=>$b){
			if($a=="ixd"){
				$returnMe[$id]["id"] = (string)$b;
			} elseif($a=="url"){
				$returnMe[$id]["url"] = (string)$b;
			} elseif($a == "type"){
				$returnMe[$id]["type"] = (string)$b;
			} elseif($a == "ligandtype"){
				$returnMe[$id]["ligandtype"] = (string)$b;
			} elseif($a == "ligand"){
				$returnMe[$id]["ligand"] = (string)$b;
			} elseif($a == "pmid"){
				$returnMe[$id]["pmid"] = "http://www.ncbi.nlm.nih.gov/pubmed/".(string)$b;
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
