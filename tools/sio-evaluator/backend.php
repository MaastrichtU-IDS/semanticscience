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
 *  get next term (userid) {returns obj->{userid, qname, type, string}}
 *  get annotation (qname) {return obj->{userid,qname,type,string}}
 *  get subclass axiom (qname)  {return obj->{userid,qname,type,string} }
 *  store result ($result->{userid,type,qname,yes|no|idk,comment}}
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
	* Construct a SioEvaluator object given an ip
	* @param $anIp the ip of the client (the userid)
	* @param $loadDb set to true for populating the db for the first time
	*
	*/
	public function __construct($aUserId, $loadDb = false){
		
		//create a connection to the database 
		$this->conn = new mysqli($this->host, $this->user, $this->pass, $this->db);
		//create the sio_classes array
		$sio_classes = $this->retrieveSIOClasses();
		//check if the DB's tables have been created and populated
		if($loadDb){
			
			// empty the database and create tables from scratch
			//$this->emptyTable("qname2annotation");
			//$this->emptyTable("qname2axiom");
			$this->emptyTable("qname2label");
			//$this->populateQname2Annotation();
			//$this->populateQname2Axiom();
			$this->populateQname2Label();
			//populate qname2annotation and qname2axiom
			//$this->populate();
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
	* This method returns either an annotation or a subclassaxiom for a user identified
	* by $aUserid (their IP). First it will attempt to return an annotation or subclass axioms
	* that have been annotated between 1 and 5 times, if none are found then a random one will be 
	* returned
	* @param $aUserId the IP of the annotator
	* @return returns obj->{userid, qname, type, string}
	*/
	public function getNextTerm($aUserId){
		//first pick a random number between 1 (subclassaxiom) and 2 (annotation)
		//find a term that has been annotated between 1 and 5 times by users other than auserid
		//if none found get a random one
		//$rm = new stdClass();
		//$rm->type = "annotation";
		//$rm->term_id = "SIO_000001";
	}

	/**
	* Get the dc:description for a SIO Class ( using its QNamei.e.: SIO:000000) for 
	* a given IP. 
	*
	* 
	* @param 
	* @return {return obj->{userid,qname,type,string}}
	*/
	public function getAnnotation($aQname){
		//SELECT  qa.annotation FROM qname2annotation qa WHERE qa.qname = "SIO:000395"
		$qry = "SELECT  qa.annotation FROM qname2annotation qa WHERE qa.qname = '".$aQname."'";
		echo "\n".$qry."\n";
		if($result = $this->getConn()->query($qry)){
			while($row = $result->fetch_assoc()){
				print_r($row);
			}
		}else{
			printf("Error: %s\n", $this->getConn()->error);
			exit;
		}

	}


	//populate qname2annotation and qname2axiom
	/*private function populate(){
		//get the list of classes
		$sio_classes = $this->retrieveSIOClasses();
		echo "loading tables qname2annoation and qname2axiom...";
		foreach ($sio_classes as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$anAnnotation = $this->retriveClassAnnotation($aClassUri);
			$axioms = $this->retrieveClassAxioms($aClassUri);
			$label = $this->retrieveClassLabel($aClassUri);
			//insert into the table
			$qry = "INSERT INTO qname2annotation VALUES ('".$aQname."','".str_replace("'", "", $anAnnotation)."')";
			
			if(!$this->getConn()->query($qry)){
				printf("Error: %s\n", $this->getConn()->error);
				exit;
			}

			foreach ($axioms as $anAxiom) {
				$qry2 = "INSERT INTO qname2axiom VALUES ('".$aQname."','". str_replace("'", "", $anAxiom)."')";
				if(!$this->getConn()->query($qry2)){
					printf("Error: %s\n", $this->getConn()->error);
					exit;
				}
			}
		}
		echo " done! \n";
	}*/

	private function populateQname2Label(){
		$sc = $this->getSioClasses();
		echo "loading table qname2axiom ... ";
		foreach ($sc as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$label = $this->retrieveClassLabel($aClassUri);
			$qry = "INSERT INTO qname2label VALUES('".$aQname."','".str_replace("'", "", $label)."')";
			if(!$this->getConn()->query($qry)){
				printf("Error: %s\n", $this->getConn()->error);
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
				$qry2 = "INSERT INTO qname2axiom VALUES ('".$aQname."','". str_replace("'", "", $anAxiom)."')";
				if(!$this->getConn()->query($qry2)){
					printf("Error: %s\n", $this->getConn()->error);
					exit;
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
				printf("Error: %s\n", $this->getConn()->error);
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
			printf("Error: %s\n", $this->getConn()->error);
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

}//class


/**********/
/* RUNNER */
/**********/
//currently running for tests
$p = new SioEvaluator(1234,$loadDb = true);


?>
