<?php
/**
Copyright (C) 2012 Michel Dumontier and Jose Cruz-Toledo

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/**
 * class;
 * functions 
 *  get next term (user id) {returns termid}
 *  get annotation (term id) {return obj->{id,termid,type,string}}
 *  get subclass axiom (term id)  {return obj->{id,termid,type,string} }
 *  store result ($result->{id,termid,yes|no|idk,comment}}
*/

class SEBackend{
	/**
	* Database credentials
	*/
	private $host = "134.117.108.159";
	private $user = "sio-evaluator";
	private $pass = "sio-evaluator-secret";
	private $db = "sio-evaluator";
	private $conn = null;

	public function __construct(){
		//create a connection to the database 
		$conn = $this->createConnection(
			$this->getHost(), 
			$this->getUser(), 
			$this->getPass(), 
			$this->getDatabase()
		);
		//check if the DB's tables have been created and populated
		if($this->isDbPopulated() == false){
			// empty the database and create tables from scratch

		}
	}

	/** 
	* Create a connection to the sio-evaluator database.
	* If cannot create one, program fails and exits
	*/
	private function createConnection($h, $u, $p, $db){
		$rm = mysqli_connect($h, $u, $p, $db);
		//check conn
		if(mysqli_connect_errno($rm)){
			echo "Failed to connect to Database: ". mysqli_connect_error();
			exit;
		}
		return $rm;
	}

	private function getDirectParentOf($aQname){

	}

	private function getAnnotaitonFor($aQname){

	}

	private function getDescendantsOf($aQname){
		
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


}//class


/**********/
/* RUNNER */
/**********/
$p = new SEBackend();


?>