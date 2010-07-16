<?php

/**
 * This script reads the user's input from the bio2rdf site and returns
 * an xml document corresponding to a search of a lucene index of all of Bio2RDF
 * */

if(count($_POST) == 1){
	if(isset($_POST["sS"]) && strlen($_POST["sS"]) > 1){
		$sstr = htmlentities($_POST["sS"]);
		//execute non-namespace restricted search
		$cmd = "java -jar SearchBio2rdf.jar -query \"$sstr\"";
		$results = trim(shell_exec($cmd));
		echo $results;
	}//if
}elseif(count($_POST) == 2){
	if((isset($_POST["sS"]) && strlen($_POST["sS"]) > 1) && (isset($_POST["ns"]) && strlen($_POST["ns"]) > 1)){
		$sstr = htmlentities($_POST["sS"]);
		$sns = htmlentities($_POST["ns"]);
		//execute namespace restricted search
		$cmd = "java -jar SearchBio2rdf.jar -ns $sns -query \"$sstr\"";
		$results = trim(shell_exec($cmd));
		echo $results;
	}//if
}else{
	return false;
	exit;	
}


?>
