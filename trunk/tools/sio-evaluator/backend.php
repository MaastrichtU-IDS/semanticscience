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
require_once("lib/connector.php");

/**
 * class;
 * functions 
 *  get next term (user id) {returns termid}
 *  get annotation (term id) {return obj->{id,termid,type,string}}
 *  get subclass axiom (term id)  {return obj->{id,termid,type,string} }
 *  store result ($result->{id,termid,yes|no|idk,comment}}
*/

class SEBackend{
	//a connection to the db object
	private $conn = null;
	private $sio_location = "/home/jose/Documents/ontologies/sio/sio.owl";

	public function __construct(){
		//create a connection to the database 
		$this->conn = new Connector();
		//check if the DB's tables have been created and populated
		if($this->isDbPopulated() == false){
			// empty the database and create tables from scratch
			$classes = $this->retrieveSIOClasses();
			print_r($classes);

		}
	}

	

	private function getClassAxiomsOf($aQname){

	}

	private function getAnnotaitonsFor($aQname){

	}


	/**
	* Check if the database for this sio-evaluator has been populated.
	* Returns true if populated tables are found
	* false otherwise
	*/
	private function isDbPopulated(){

		//first check if database exists
		return false;
	}

	/**
	* This method populates the Sio-Evaluator database. 
	* If the database has been created it returns false, creates it otherwise
	*/
	private function populateSEDB(){
		return false;
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


	//populate qname2annotation
	private function populateQname2Annotation(){
		//get the list of classes in sio
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
	private function retriveClassAnnotation($someClassUri){
		$rm = array();
		foreach ($someClassUris as $aUri) { 
			
		}
		return $rm;
	}

}//class


/**********/
/* RUNNER */
/**********/
$p = new SEBackend();


?>
