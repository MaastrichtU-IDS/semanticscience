<?php
/**
* Copyright (C) 2012 Michel Dumontier and Jose Cruz-Toledo
*
* Permission is hereby granted, free of charge, to any person obtaining a copy of
* this software and associated documentation files (the "Software"), to deal in
* the Software without restriction, including without limitation the rights to
* use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
* of the Software, and to permit persons to whom the Software is furnished to do
* so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*/
/*
 * class;
 * functions 
 *  getNextTerm () {returns obj->{userid, qname, type, value, label, uri}}
 *  getAnnotation (qname) {return obj->{userid,qname,type,value, label, uri}}
 *  getSubclassAxioms (qname)  {return obj->{userid,qname,type,value, label, uri} }
 *  store result ($result->{userid,type,qname,radio_opt (yes|no|idk),comment}}
*/


class SioEvaluator{
	/**
	* Database credentials
	*/
	private $host = "localhost";
	private $user = "sio-evaluator";
	private $pass = "sio-evaluator-secret";
	private $db = "sio-evaluator";
	/**
	* The connection object
	*/
	private $conn = null;
	/**
	* Location of sio.owl
	*/
	private $sio_location = "/home/jose/Documents/ontologies/sio/sio.owl";
	/**
	* The ip of the user
	*/
	private $userid = null;

	/**
	* an array with all of the SIO class URIs
	*/
	private $sio_classes = null;

	/**
	* An assoc array where the key is an integer and the value is an 
	* annotatable feature
	*/
	private $annotatable_features = array("1"=>"subclassaxioms", "2" =>"annotation");

	/**
	* Construct a SioEvaluator object given an ip
	* @param $anIp the ip of the client (the userid)
	* @param $loadDb set to true for populating the db for the first time
	*
	*/
	public function __construct($aUserId, $loadDb = false){
		
		//create a connection to the database 
		$this->conn = new mysqli($this->host, $this->user, $this->pass, $this->db);
		//create the sio_classes array
		$this->sio_classes = $this->retrieveSIOClasses();
		//check if the DB's tables have been created and populated
		if($loadDb){
			

			//TESTING ONLY 
			

			// empty the database and create tables from scratch
			//$this->emptyTable("qname2annotation");
			//$this->emptyTable("qname2axiom");
			//$this->emptyTable("qname2label");
			$this->emptyTable("annotation_annotation_count");
			$this->emptyTable("axiom_annotation_count");
			//$this->populateQname2Annotation();
			//$this->populateQname2Axiom();
			//$this->populateQname2Label();
			$this->populateAnnotationAnnotationCount();
			$this->populateAxiomAnnotationCount();
		}
		if(strlen($aUserId) == 0 || $aUserId == null){
			throw new Exception("invalid user id provided! Terminating program!");
			exit;
		}
		//create a userid
		$this->userid = $aUserId;

	}

	/**
	* Close the connection !
	*/
	public function __destruct(){
		$this->conn->close();
	}	
	/**
	* Record an annotation from a user.
	* @param $aResult : An object with the following instance variables:
	* - userid : the IP of the user (or any other user-unique string) : exception is thrown if null or empty 
	* - qname : the qname of the annotation being processed.
	* - type : the type of annotation being processed. Only valid values : "annotation" or "subclassaxioms"
	*	exception thrown otherwise
	* - radio_option : radio option chosen by user. valid values: "yes" or "no" or "idk". Exception thrown otherwise
	* - comment : the comment
	* @return true if stored succesfully, false otherwise.
	*/
	public function storeResult($aResult){
		if(!is_object($aResult)){
			$msg =  "Invalid parameter! Must be an object with instance variables:"
			." userid, type, qname, radio_option, comment\n";
			throw new Exception($msg);
			exit;
		}

		if($this->isValidResult($aResult)){
			//store the result in the db
			//get the type
			$type = $aResult->type;
			if($type == "annotation"){
				//userid, qname, radio_option_selected, comment
				$q = "INSERT INTO userid2annotation VALUES ('"
					.$aResult->userid."','".$aResult->qname
					."','".$aResult->radio_option
					."','".$aResult->comment."')";
				if(!$this->getConn()->query($q)){
					printf("2341 Error: %s\n", $this->getConn()->error);
					exit;
				}
				//now update the annotation_annotation_count table
				//$q2 = "INSERT INTO annotation_annotation_count VALUES ('"
				//	.$aResult->qname."','". 

			}elseif($type == "subclassaxioms"){

			}
		}
		return false;


	}

	/**
	* This method returns either an annotation or a subclassaxiom for $this->getUserId(). 
	* First it will attempt to return an annotation or subclass axioms
	* that have been annotated between 1 and 5 times, if none are found then a random one will be 
	* returned
	* @return an object with the following instance variables:
	* - userid : the ip of the user making the request
	* - qname : the class's qname
	* - type : "annotation"|"subclassaxioms"
	* - value : the value of the annotation or sublcassaxioms array
	* - label : the rdfs:label of this class
	* - uri : the uri for this class's qname
	*/
	public function getNextTerm(){

		//first randomy pick either a subclassaxiom or an annotation
		$rand = rand(1,2);
		$feature = $this->getAnnotatableFeatures()[$rand];
		if($feature == "subclassaxioms"){
			//find a term that has been annotated between 1 and 5 times by users other than $auserid
			//SELECT DISTINCT a.qname FROM userid2annotation a INNER JOIN  annotation_annotation_count b ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2annotation WHERE userid2annotation.userid = '1345234' ) AND (b.count < 6 && b.count>0)
			$q = "SELECT DISTINCT a.qname FROM userid2axioms a INNER JOIN  axiom_annotation_count b"
				." ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2axioms WHERE userid2axioms.userid = '".
				$this->getUserId()."' ) AND (b.count < 6 && b.count>0)";
			if($r = $this->getConn()->query($q)){
				$row_count = $r->num_rows;
				//if more than one result is found return one at random
				if($row_count >0){
					$random = rand(1, $row_count);
					$counter = 1;
					while($row = $r->fetch_assoc()){
						if($counter == $random){
							return($this->getSubclassAxioms($row['qname']));
						}
						$counter++;
					}
				}else{
					$aRandUri_key = array_rand($this->getSioClasses());
					$aQname = $this->makeQNameFromUri($this->getSioClasses()[$aRandUri_key]);
					return($this->getSubclassAxioms($aQname));
				}
				$r->close();
			}
		}elseif($feature == "annotation"){
			//find a term that has been annotated between 1 and 5 times by users other than $auserid
			$q = "SELECT DISTINCT a.qname FROM userid2annotation a INNER JOIN  annotation_annotation_count b"
				." ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2annotation WHERE userid2annotation.userid = '".
				$this->getUserId()."' ) AND (b.count < 6 && b.count>0)";
			if($r = $this->getConn()->query($q)){
				$row_count = $r->num_rows;
				//if more than one result is found return one at random
				if($row_count > 0){
					$random = rand(1, $row_count);
					$counter = 1;	
					while($row = $r->fetch_assoc()){
						if($counter == $random){
							return($this->getAnnotation($row['qname']));		
						}
						$counter++;
					}//while
				}else{
					
					$aRandUri_key = array_rand($this->getSioClasses());
					$aQname = $this->makeQNameFromUri($this->getSioClasses()[$aRandUri_key]);
					return($this->getAnnotation($aQname));
				}
				$r->close();
			}//if
		}//elseif
		
	}

	/**
	* Get the dc:description for a SIO Class ( using its QNamei.e.: SIO:000000) for 
	* a given qname
	*
	* @param a valid sio Qname
	* @return an object with the following instance variables:
	* - qname : the class's qname
	* - type : "annotation"
	* - value : the value of the annotation
	* - label : the rdfs:label of this class
	* - uri : the uri for this class
	* if no annotation is found null is returned
	*/
	public function getAnnotation($aQname){
		$qry = "SELECT  qa.annotation FROM qname2annotation qa WHERE qa.qname = '".$aQname."'";
		if($result = $this->getConn()->query($qry)){
			while($row = $result->fetch_assoc()){
				$rm = new stdClass();
				$rm->qname = $aQname;
				$rm->type = "annotation";
				$rm->value = $row['annotation'];
				$rm->label = $this->getLabelFromQname($aQname);
				$rm->uri = $this->makeUriFromQname($aQname);
				return $rm;
			}
		}else{
			printf("234 Error: %s\n", $this->getConn()->error);
			exit;
		}
		return null;
	}

	/**
	* Get all of the subclass axioms that describe the class
	* that corresponds to the given qname
	* @param a valid sio Qname
	* @return an object with the following instance variables:
	* - qname : the class's qname
	* - type : "annotation"
	* - value : an array of strings with the class's axioms
	* - label : the rdfs:label of this class
	* - uri : the uri for this class
	* if no axioms are found null is returned
	*/
	public function getSubclassAxioms($aQname){
		//
		$q = "select qa.axiom from qname2axiom qa  where qname = '".$aQname."'";
		if($result = $this->getConn()->query($q)){
			$axioms_arr = array();
			while($row = $result->fetch_assoc()){
				$axioms_arr[] = $row['axiom'];
			}	
			if(count($axioms_arr)>0){
				$rm = new stdClass();
				$rm->qname = $aQname;
				$rm->type = "subclassaxioms";
				$rm->value = $axioms_arr;
				$rm->label = $this->getLabelFromQname($aQname);
				$rm->uri = $this->makeUriFromQname($aQname);
				return $rm;
			}
		}else{
			printf("34543 Error: %s\n", $this->getConn()->error);
			exit;
		}
		return null;
	}

	/**
	* Retrieve a Qname's rdfs:label from qname2label
	* @param $aQname a valid Qname (eg: SIO:000395)
	* @return the qname's label null if none is found
	*/
	public function getLabelFromQname($aQname){
		$qry = "SELECT qa.label FROM qname2label qa WHERE qa.qname = '".$aQname."'";
		if($r = $this->getConn()->query($qry)){
			while($row = $r->fetch_assoc()){
				return $row['label'];
			}
		}else{
			printf("1234 Error: %s\n", $this->getConn()->error);
			exit;
		}
		return null;

	}

	/**
	* Verifies if parameter is an object with the following vars
	* - userid : the IP of the user (or any other user-unique string) : exception is thrown if null or empty 
	* - qname : the qname of the annotation being processed.
	* - type : the type of annotation being processed. Only valid values : "annotation" or "subclassaxioms"
	*	exception thrown otherwise
	* - radio_option : radio option chosen by user. valid values: "yes" or "no" or "idk". Exception thrown otherwise
	* - comment : the comment
	* @param the object to be processed
	* @return true if valid, false otherwise
	*/
	private function isValidResult($aResult){
		$r = true;
		if(is_object($aResult)){
			
			$qname = $aResult->qname;
			$aType = $aResult->type;
			$aRadioOption = $aResult->radio_option;
			$aComment = $aResult->comment;
			$fault_count = 0;
			if(!isset($aResult->userid) || strlen($aResult->userid)==0){
				$fault_count++;
			}
			if(!isset($aResult->qname)){
				throw new Exception("qname not provided!\n");
				$fault_count++;
			}else{
				//check if valid qname
				preg_match("/^SIO\:\d+$/", $aResult->qname, $m);
				if(count($m) == 0){
					throw new Exception("Invalid qname provided. Please follow the pattern SIO:000000!\n");
					$fault_count ++;
				}
			}
			if(!isset($aResult->type)){
				throw new Exception("type not provided".PHP_EOL);
				$fault_count++;
			}else{
				preg_match("/^(annotation|subclassaxioms)$/", $aResult->type, $m);
				if(count($m) ==0){
					throw new Exception("Invalid type provided. Valid type values: annotation or sublcassaxioms\n");
					$fault_count ++;
				}
			}
			if(!isset($aResult->radio_option)){
				throw new Exception("radio_option not provided".PHP_EOL);
				$fault_count++;
			}else{
				preg_match("/^(yes|no|idk)$/", $aResult->radio_option, $m);
				if(count($m) ==0){
					throw new Exception("Invalid radio_option provided. Valid radio_option values: yes, no or idk\n");
					$fault_count ++;
				}
			}
			if(!isset($aResult->comment)){
				throw new Exception("comment not set. If none provided by user please provide an empty string");
				$fault_count ++;
			}

			if($fault_count == 0){
				return true;
			}else{
				return false;
			}
		}
		return false;
	}
	private function populateQname2Label(){
		$sc = $this->getSioClasses();
		echo "loading table qname2label ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$label = $this->retrieveClassLabel($aClassUri);
			$qry = "INSERT INTO qname2label VALUES('".$aQname."','".str_replace("'", "", $label)."')";
			if(!$this->getConn()->query($qry)){
				printf("4309 Error: %s\n", $this->getConn()->error);
				exit;
			}
		}
		echo "done!\n";
	}

	//initializie annotation_annotation_count table
	private function populateAnnotationAnnotationCount(){
		$sc = $this->getSioClasses();
		echo "initializing table anntation_annotation_count ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$qry = "INSERT INTO annotation_annotation_count VALUES('".$aQname."','0')";
			if(!$this->getConn()->query($qry)){
				printf("43092 Error: %s\n", $this->getConn()->error);
				exit;
			}
		}
		echo "done!\n";
	}

	//initializie axiom_annotation_count table
	private function populateAxiomAnnotationCount(){
		$sc = $this->getSioClasses();
		echo "initializing table axiom_annotation_count ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$qry = "INSERT INTO axiom_annotation_count VALUES('".$aQname."','0')";
			if(!$this->getConn()->query($qry)){
				printf("434409 Error: %s\n", $this->getConn()->error);
				exit;
			}
		}
		echo "done!\n";
	}
	private function populateQname2Axiom(){
		$sc = $this->getSioClasses();
		echo "loading table qname2axiom ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$axioms = $this->retrieveClassAxioms($aClassUri);
			foreach ($axioms as $anAxiom) {
				//ignore the axioms that start with "Class ="
				$q = strstr($anAxiom, "Class =");
				if(strlen($q) == 0){
					$qry2 = "INSERT INTO qname2axiom VALUES ('".$aQname."','". str_replace("'", "", $anAxiom)."')";
					if(!$this->getConn()->query($qry2)){
						printf("2341 Error: %s\n", $this->getConn()->error);
						exit;
					}
				}
			}
		}
		echo "done!\n";
	}

	private function populateQname2Annotation(){
		$sc = $this->getSioClasses();
		echo "loading table qname2annotation ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$anAnnotation = $this->retriveClassAnnotation($aClassUri);
			//insert into the table
			$qry = "INSERT INTO qname2annotation VALUES ('".$aQname."','".str_replace("'", "", $anAnnotation)."')";
			if(!$this->getConn()->query($qry)){
				printf("2345213 Error: %s\n", $this->getConn()->error);
				exit;
			}
		}
		echo "done!\n";
	}



	/**
	* Empties a table from the database
	*/
	private function emptyTable($aTableName){
		$qry = "TRUNCATE TABLE ".$aTableName."";
		if(!$this->getConn()->query($qry)){
			printf("093 Error: %s\n", $this->getConn()->error);
			exit;
		}
	}

	/**
	* Create and return an array of SIO class URIs
	*/
	private function retrieveSIOClasses(){
		//owltools /home/jose/owl/sio.owl --list-classes
		$r = shell_exec("owltools ".$this->sio_location." --list-classes") or die( "Could not run owltools!");
		$rm = array();
		$lines = explode("\n", $r);
		foreach ($lines as $aLine) {
			preg_match("/^<(http:\/\/.*)>$/", $aLine, $matches);
			if(count($matches)){
				$aUri = trim($matches[1]);
				$rm[] = $aUri;
			}
		}
		return $rm;
	}

	/**
	* return the dc:description for the given URI
	* @param $someClassUri a of a SIO class 
	*/
	public function retriveClassAnnotation($someClassUri){
		//owltools /home/jose/owl/sio.owl --reasoner hermit --sparql-dl "SELECT * WHERE{ Annotation( <http://semanticscience.org/resource/SIO_000006>, <http://purl.org/dc/terms/description>, ?d) }"
		preg_match("/^http:\/\/.*$/", $someClassUri, $matches);
		if(count($matches)){
			$result = shell_exec(
				"owltools ".$this->sio_location.
				" --sparql-dl \"SELECT * WHERE {Annotation(<".
				$matches[0].">, <http://purl.org/dc/terms/description>, ?d) }\""
			) or die ("Could not run owltools!\n");
			$lines = explode("\n", $result);
			foreach ($lines as $aLine) {
				//[0]  ?d=
				preg_match("/^\[0\]\s+\?d=\"(.*)\"/", $aLine, $m);
				if(count($m)){
					$r = $m[1];
					if(count($r)){
						return $r;
					}
				}
			}
		}else{
			return null;
		}
	}//retrieveClassAnnotation
	
	public function retrieveClassLabel($someClassUri){
		preg_match("/^http:\/\/.*$/", $someClassUri, $matches);
		if(count($matches)){
			//owltools /home/jose/Documents/ontologies/sio/sio.owl --reasoner hermit --sparql-dl "SELECT * WHERE{ Annotation( <http://semanticscience.org/resource/SIO_000006>, <http://www.w3.org/2000/01/rdf-schema#label>, ?d) }"
			$result = shell_exec(
				"owltools ".$this->sio_location.
				" --sparql-dl \"SELECT * WHERE {Annotation(<".
				$matches[0].">, <http://www.w3.org/2000/01/rdf-schema#label>, ?d) }\""
			) or die ("Could not run owltools!\n");
			$lines = explode("\n", $result);
			foreach($lines as $aLine){
				preg_match("/^\[0\]\s+\?d=\"(.*)\"/", $aLine, $m);
				if(count($m)){
					$r = $m[1];
					if(count($r)){
						return $r;
					}
				}
			}
		}else{
			return null;
		}
	}


	/**
	* return an array with the class axioms for a given class URI in manchester syntax
	*/
	public function retrieveClassAxioms($someClassUri){
		$rm = array();
		//owltools ~/Documents/ontologies/sio/sio.owl --reasoner hermit --pretty-printer-settings -m --hide-ids --list-class-axioms 'http://semanticscience.org/resource/SIO_000006'
		preg_match("/^http:\/\/.*$/", $someClassUri, $matches);
		if(count($matches)){
			$result = shell_exec("owltools ".$this->sio_location." --reasoner hermit"
					." --pretty-printer-settings -m --hide-ids"
					." --list-class-axioms '".$matches[0]."'"
				) or die("Could not run owltools! \n");
			$lines = explode("\n", $result);
			foreach($lines as $aLine){
				preg_match("/^[^\d+\-\d+\-\d+].+/", $aLine, $m);
				if(count($m)){
					$rm[] = trim($m[0]);
				}
			}
			return $rm;
		}else{
			return null;
		}
	}



	/**
	* For 'http://semanticscience.org/resource/SIO_000006' the qname is SIO:000006
	*/
	public function makeQNameFromUri($aUri){
		$s = substr($aUri,  strrpos($aUri, "/")+1);
		return str_replace("_", ":", $s);
	}

	public function makeUriFromQname($aQname){
		//http://semanticscience.org/resource/
		$s = str_replace(":", "_", $aQname);
		return "http://semanticscience.org/resource/".$s;
	}


	private function getHost(){
		return $this->host;
	}
	private function getUser(){
		return $this->user;
	}
	private function getDatabase(){
		return $this->db;
	}
	private function getPass(){
		return $this->pass;
	}
	private function getConn(){
		return $this->conn;
	}
	public function getUserId(){
		return $this->userid;
	}
	public function getSioClasses(){
		return $this->sio_classes;
	}
	public function getAnnotatableFeatures(){
		return $this->annotatable_features;
	}
}//class


/**********/
/* RUNNER */
/**********/
//currently running for tests
$p = new SioEvaluator('1234',$loadDb = true);


?>
