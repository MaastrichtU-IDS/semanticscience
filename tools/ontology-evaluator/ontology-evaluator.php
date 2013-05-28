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


class OntologyEvaluator{
	/**
	* Database credentials
	*/
	private $host = "localhost";
	private $user = "onto-evaluator";
	private $pass = "onto-evaluator-secret";
	private $db = "ontology-evaluator";
	/**
	* The connection object
	*/
	private $conn = null;
	/**
	* The base uri of the ontology
	*/
	private $ontology_base_uri = null;
	/**
	* a path to the an owl ontology file
	*/ 
	private $ontology_file_path = null;
	/**
	* The ip of the user
	*/
	private $userid = null;

	/**
	* an array with every class URIs
	*/
	private $ontology_classes = null;

	/**
	* An assoc array where the key is an integer and the value is an 
	* annotatable feature
	*/
	private $annotatable_features = array("1"=>"subclassaxioms", "2" =>"annotation");

	/**
	* Construct a SioEvaluator object given an ip
	* @param aUserId the ip of the client (the userid)
	* @param anOwlFilePath a path to the owl file
	* @param anOntologyBaseUri the base uri of the ontology, this string 
	* 		 uniquely identifies this ontology
	* @param testing set to true for testing
	*
	*/
	public function __construct($aUserId, $anOwlFilePath, $anOntologyBaseUri, $testing = false){
		//check parameters
		if($this->checkConstructorParams($aUserId, $anOwlFilePath,$anOntologyBaseUri, $testing)){
			//set the userid
			$this->userid = $aUserId;
			//set the file path
			$this->ontology_file_path = $anOwlFilePath;
			//set the base uri
			$this->ontology_base_uri = $anOntologyBaseUri;
			//set the ontology URI from where the ontology document will be downloaded
			$this->ontology_base_uri = $anOntologyBaseUri;
			//create a connection to the database 
			$this->conn = new mysqli($this->host, $this->user, $this->pass, $this->db);
			//create the sio_classes array
			$this->ontology_classes = $this->retrieveOntologyClasses();
		}
		
		if($testing){
			//TESTING ONLY 
			
			// empty the database and create tables from scratch
		
			$this->emptyTable("qname2annotation");
			$this->emptyTable("qname2axiom");
			$this->emptyTable("qname2label");
			$this->emptyTable("annotation_annotation_count");
			$this->emptyTable("axiom_annotation_count");
			$this->emptyTable("userid2annotation");
			$this->emptyTable("userid2axioms");
			$this->populateQname2Annotation();
			$this->populateQname2Axiom();
			$this->populateQname2Label();
			$this->populateAnnotationAnnotationCount();
			$this->populateAxiomAnnotationCount();
				/*
		}
	}

	/**
	* Close the connection !
	*/
	public function __destruct(){
		$this->conn->close();
	}	

	private function checkConstructorParams($aUserId, $anOwlFilePath, $anOntologyBaseUri, $testing){
		$fc = 0;
		if(strlen($aUserId) == 0 || $aUserId == null){
			throw new Exception("invalid user id provided! Terminating program!");
			$fc++;
		}
		if(strlen($anOntologyBaseUri) == 0 || $anOntologyBaseUri == null){
			throw new Exception("invalid ontology base uri provided! Terminating program!");
			$fc++;
		}
		if(strlen($anOwlFilePath) == 0 || $anOwlFilePath == null){
			throw new Exception("invalid file path provided!");
			$fc++;
		}
		if(!is_bool($testing)){
			throw new Exception("invalid testing flag provided");
			$fc++;
		}
		if($fc == 0){
			return true;
		}
		return false;
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
					printf("23481 Error: %s\n", $this->getConn()->error);
					exit;
				}
				//now update the annotation_annotation_count table
				$q2 = "UPDATE annotation_annotation_count SET count=count+1 WHERE qname='".$aResult->qname."'";
				if(!$this->getConn()->query($q2)){
					printf("2348981 Error: %s\n", $this->getConn()->error);
					exit;
				}
				return true;
			}elseif($type == "subclassaxioms"){
				//userid, qname, radio_option_selected, comment
				$q = "INSERT INTO userid2axioms VALUES ('"
					.$aResult->userid."','".$aResult->qname
					."','".$aResult->radio_option
					."','".$aResult->comment."')";
				if(!$this->getConn()->query($q)){
					printf("23431 Error: %s\n", $this->getConn()->error);
					exit;
				}
				//now update the annotation_annotation_count table
				$q2 = "UPDATE axiom_annotation_count SET count=count+1 WHERE qname='".$aResult->qname."'";
				if(!$this->getConn()->query($q2)){
					printf("234421 Error: %s\n", $this->getConn()->error);
					exit;
				}
				return true;
			}
		}
		return false;
	}

	/**
	* This method returns either an annotation or a subclassaxiom for $this->getUserId(). 
	* First it will attempt to return an annotation or subclass axioms
	* that have been annotated between 1 and 5 times by users other than $this->getUserId()
	* , if none are found then a random one will be returned
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
		$feature_ar = $this->getAnnotatableFeatures();
		$feature = $feature_ar[$rand];
		if($feature == "subclassaxioms"){
			//find a term that has been annotated between 1 and 5 times by users other than $auserid
			//SELECT DISTINCT a.qname FROM userid2annotation a INNER JOIN  annotation_annotation_count b ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2annotation WHERE userid2annotation.userid = '1345234' ) AND (b.count < 6 && b.count>0)
			$q = "SELECT DISTINCT a.qname FROM userid2axioms a INNER JOIN  axiom_annotation_count b"
				." ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2axioms WHERE userid2axioms.userid = '".
				$this->getUserId()."' AND userid2axioms.qname=a.qname) AND (b.count < 6 AND b.count>0)";
			
			if($r = $this->getConn()->query($q)){
				$row_count = $r->num_rows;
				//if more than one result is found return one at random
				if($row_count >0){
					$random = rand(1, $row_count);
					$counter = 1;
					while($row = $r->fetch_assoc()){
						if($counter == $random){
							return($this->getSubclassAxioms($this->ontology_base_uri, $row['qname']));
						}
						$counter++;
					}
				}else{
					$sc = $this->getOntologyClasses();
					$aRandUri_key = array_rand($sc);
					$aQname = $this->makeQNameFromUri($sc[$aRandUri_key]);
					return($this->getSubclassAxioms($aQname));
				}
				$r->close();
			}
		}elseif($feature == "annotation"){
			//find a term that has been annotated between 1 and 5 times by users other than $auserid
			$q = "SELECT DISTINCT a.qname FROM userid2annotation a INNER JOIN  annotation_annotation_count b"
				." ON a.qname=b.qname WHERE NOT EXISTS (SELECT * FROM userid2annotation WHERE userid2annotation.userid = '".
				$this->getUserId()."' AND userid2annotation.qname=a.qname) AND (b.count < 6 AND b.count>0)";
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
					$aRandUri_key = array_rand($this->getOntologyClasses());
					$sc = $this->getOntologyClasses();
					$aQname = $this->makeQNameFromUri($sc[$aRandUri_key]);
					return($this->getAnnotation($aQname));
				}
				$r->close();
			}//if
		}//elseif
	}//getNextTerm

	/**
	* Get the dc:description for a  Class. If dc:description is not used null is returned
	*
	* @param $anOntologyUrl the url of the ontology where this qname came from
	* @param $aQname a Qname 
	* @return an object with the following instance variables:
	* - qname : the class's qname
	* - type : "annotation"
	* - value : the value of the annotation
	* - label : the rdfs:label of this class
	* - uri : the uri for this class
	* if no annotation is found null is returned
	*/
	public function getAnnotation($anOntologyBaseUri, $aQname){
		$qry = "SELECT  qa.annotation FROM qname2annotation qa WHERE qa.ontologyBaseUri = '"
			.$anOntologyBaseUri."' AND qa.qname = '".$aQname."'";
		if($result = $this->getConn()->query($qry)){
			while($row = $result->fetch_assoc()){
				$rm = new stdClass();
				$rm->qname = $aQname;
				$rm->type = "annotation";
				$rm->value = $row['annotation'];
				$rm->label = $this->getLabelFromQname($aQname);
				$rm->ontology_base_uri = $anOntologyBaseUri;
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
	public function getSubclassAxioms($anOntologyBaseUri, $aQname){
		//
		$q = "SELECT qa.axiom FROM qname2axiom qa  WHERE qa.ontologyBaseUri ='"
			.$anOntologyBaseUri."' qa.qname = '".$aQname."'";
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
				$rm->ontology_base_uri = $anOntologyBaseUri;
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
	public function isValidResult($aResult){
		$r = true;
		if(is_object($aResult)){
			$fault_count = 0;
			if(!isset($aResult->userid)){
				throw new Exception ("userid not provided\n");
				$fault_count++;
			}
			if(!isset($aResult->qname)){
				throw new Exception("qname not provided!\n");
				$fault_count++;
			}
			if(!isset($aResult->ontology_url)){
				throw new Exception("ontology_url not provided!".PHP_EOL);
				$fault_count++;
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
		$sc = $this->getOntologyClasses();
		echo "loading table qname2label ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$label = $this->retrieveClassLabel($aClassUri);
			$qry = "INSERT INTO qname2label VALUES('".$this->ontology_base_uri."','".$aQname."','".str_replace("'", "", $label)."')";
			if(!$this->getConn()->query($qry)){
				printf("4309 Error: %s\n", $this->getConn()->error);
				exit;
			}
		}
		echo "done!\n";
	}

	//initializie annotation_annotation_count table
	private function populateAnnotationAnnotationCount(){
		$sc = $this->getOntologyClasses();
		echo "initializing table anntation_annotation_count ... ";
		$q = "SELECT a.qname FROM qname2annotation a WHERE a.ontologyBaseUri='".$this->ontology_base_uri."'";
		if($result = $this->getConn()->query($q)){
			while($row = $result->fetch_assoc()){
				$qry = "INSERT INTO annotation_annotation_count VALUES('".$row['qname']."','0')";
				if(!$this->getConn()->query($qry)){
					printf("43092 Error: %s\n", $this->getConn()->error);
					exit;
				}//if
			}//while
			$result->free();
		}//if
		echo "done!\n";
	}

	//initializie axiom_annotation_count table
	private function populateAxiomAnnotationCount(){
		$sc = $this->getOntologyClasses();
		echo "initializing table axiom_annotation_count ... ";
		$q = "SELECT a.qname FROM qname2annotation a WHERE a.ontologyBaseUri ='".$this->ontology_base_uri."'";
		if($result = $this->getConn()->query($q)){
			while($row = $result->fetch_assoc()){
				$qry = "INSERT INTO axiom_annotation_count VALUES('".$row['qname']."','0')";
				if(!$this->getConn()->query($qry)){
					printf("43092 Error: %s\n", $this->getConn()->error);
					exit;
				}//if
			}
			$result->free();
		}
		echo "done!\n";
	}
	private function populateQname2Axiom(){
		$sc = $this->getOntologyClasses();
		echo "loading table qname2axiom ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$axioms = $this->retrieveClassAxioms($aClassUri);
			foreach ($axioms as $anAxiom) {
				//ignore the axioms that start with "Class ="
				$q = strstr($anAxiom, "Class =");
				if(strlen($q) == 0){
					$qry2 = "INSERT INTO qname2axiom VALUES ('".$this->ontology_base_uri."','".$aQname."','". str_replace("'", "", $anAxiom)."')";
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
		$sc = $this->getOntologyClasses();
		echo "loading table qname2annotation ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$anAnnotation = $this->retriveClassAnnotation($aClassUri);
			//insert into the table
			$qry = "INSERT INTO qname2annotation VALUES ('".$this->ontology_base_uri."','".$aQname."','".str_replace("'", "", $anAnnotation)."')";
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
	* Create and return an array containing every class' URIs
	*/
	private function retrieveOntologyClasses(){
		//owltools /home/jose/owl/sio.owl --list-classes
		$r = shell_exec("owltools ".$this->ontology_file_path." --list-classes") or die( "Could not run owltools! 234");
		$rm = array();
		$lines = explode("\n", $r);
		foreach ($lines as $aLine) {
			preg_match("/^<(http:\/\/.*)>$/", $aLine, $matches);
			if(count($matches)){
				$aUri = trim($matches[1]);
				$rm[] = $aUri;
			}
		}
		if(count($rm)== 0){
			throw new Exception("No classes found!");
			exit();
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
				"owltools ".$this->ontology_file_path.
				" --sparql-dl \"SELECT * WHERE {Annotation(<".
				$matches[0].">, <http://purl.org/dc/terms/description>, ?d) }\""
			) or die ("Could not run owltools!543\n");
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
				"owltools ".$this->ontology_file_path.
				" --sparql-dl \"SELECT * WHERE {Annotation(<".
				$matches[0].">, <http://www.w3.org/2000/01/rdf-schema#label>, ?d) }\""
			) or die ("Could not run owltools!2342342\n");
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
			$result = shell_exec("owltools ".$this->ontology_file_path." --reasoner hermit"
					." --pretty-printer-settings -m --hide-ids"
					." --list-class-axioms '".$matches[0]."'"
				) or die("Could not run owltools! 092384\n");
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
	* returns the string that is after the last '/' of the URI so for 
	* 'http://semanticscience.org/resource/SIO_000006' this would return SIO_000006
	*/
	public function makeQNameFromUri($aUri){
		$a = strrpos($aUri, "/");
		$b = strrpos($aUri, "#");
		$s = substr($aUri,  max($a,$b)+1);
		return $s;
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
	public function getOntologyClasses(){
		return $this->ontology_classes;
	}
	public function getAnnotatableFeatures(){
		return $this->annotatable_features;
	}
}//class

/****/
/* TESTING */
//load sio
$p = new OntologyEvaluator("123.123.123.123", "/home/jose/Documents/ontologies/sio/sio.owl", "http://semanticscience.org/ontology/sio.owl", true);
//load bfo
$q = new OntologyEvaluator("234.234.234.234", "/home/jose/Documents/ontologies/bfo/bfo-1.1.owl", "http://www.ifomis.org/bfo/1.1", true);

?>
