<?php
require_once("include.php");

class SGD_Phenotype {

	function __construct($infile, $outfile)
	{
		$this->_in = fopen($infile,"r");
		if(!isset($this->_in)) {
			trigger_error("Unable to open $infile");
			return 1;
		}
		$this->_out = fopen($outfile,"w");
		if(!isset($this->_out)) {
			trigger_error("Unable to open $outfile");
			return 1;
		}
		
	}
	function __destruct()
	{
		fclose($this->_in);
		fclose($this->_out);
	}
	function Convert2RDF()
	{
		require ('../include.php');
		$buf = N3NSHeader($nslist);
		
		$z = 0;
		$buf = '';
		while($l = fgets($this->_in,96000)) {
			$a = explode("\t",trim($l));
			$id = $a[3];
			
			$buf .= "$sgd:$id a $sgd:Phenotype .".PHP_EOL;
			$buf .= "$sgd:$id $rdfs:label \"$b[0]\" .".PHP_EOL;
			/* UNFINISHED
			$b = explode("/|",$a[1]);
			foreach($b AS $c) {
				$d = explode("/",$c);
				$buf .= "$sgd:$id $ss:hasProperPart $sgd:$d[3] .".PHP_EOL;
			}
			*/
		}
		fwrite($this->_out, $buf);
		
		return 0;
	}

};

?>