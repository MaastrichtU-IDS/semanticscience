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
 *  get next term (userid) {returns qname}
 *  get annotation (qname) {return obj->{userid,qname,type,string}}
 *  get subclass axiom (qname)  {return obj->{userid,qname,type,string} }
 *  store result ($result->{userid,qname,yes|no|idk,comment}}
*/


class SEBackend{
	private $host = "localhost";
	private $user = "sio-evaluator";
	private $pass = "sio-evaluator-secret";
	private $db = "sio-evaluator";
	private $conn = null;
	private $sio_location = "/home/jose/Documents/ontologies/sio/sio.owl";

	public function __construct($loadDb = false){
		
		//create a connection to the database 
		$this->conn = new mysqli($this->host, $this->user, $this->pass, $this->db);
		//check if the DB's tables have been created and populated
		if($loadDb){

			// empty the database and create tables from scratch

			//empty qname2Annotation
			$this->emptyTable("qname2annotation");
			//populate the qname2annotation table
			$this->populateQname2Annotation();
			echo $this->makeQNameFromUri('http://semanticscience.org/resource/SIO_000006');


			$axioms = $this->retrieveClassAxioms('http://semanticscience.org/resource/SIO_000006');
			print_r($axioms);

		}
		//create a userid
	}

	public function __destruct(){
		$this->conn->close();
	}

	

	private function getClassAxiomsOf($aQname){

	}

	/**
	* Get the dc:description for a SIO Class using its QName (i.e.: SIO:000000)
	*
	*return obj->{userid,qname,type,string}
	* @param 
	* @return $obj->{}
	*/
	public function getAnnotation($aQname){
		//SELECT  qa.annotation FROM qname2annotation qa WHERE qa.qname = "SIO:000395"


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


	//populate the qname2annotation table
	private function populateQname2Annotation(){
		//get the list of classes
		$sio_classes = $this->retrieveSIOClasses();
		echo "loading table qname2annotation...";
		foreach ($sio_classes as $aClassUri) {
			$aQname = $this->makeQNameFromUri($aClassUri);
			$anAnnotation = $this->retriveClassAnnotation($aClassUri);
			//insert into the table
			$qry = "INSERT INTO qname2annotation VALUES ('".$aQname."','".$anAnnotation."')";
			if(!$this->getConn()->query($qry)){
				printf("Error: %s\n", $this->getConn()->error);
				exit;
			}

		}
		echo " done! \n";
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

	/**
	* return the class axioms for a given class URI in manchester syntax
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

}//class


/**********/
/* RUNNER */
/**********/
$p = new SEBackend($loadDb = true);


?>
