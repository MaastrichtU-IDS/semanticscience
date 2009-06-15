<?php

class SGD_GeneAssociation {

	function __construct($infile, $outfile)
	{
		$this->_in = gzopen($infile,"r");
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
		gzclose($this->_in);
		fclose($this->_out);
	}
	function Convert2RDF()
	{
		require ('../include.php');
		$buf = N3NSHeader($nslist);
		
		$goterms = array(
			"F" => array("type" => "Function", "p" => "hasFunction", "plabel" => "has function"),
			"C" => array("type" => "Location", "p" => "isLocatedIn", "plabel" => "is located in"),
			"P" => array("type" => "Process", "p" => "isParticipantIn", "plabel" => "is participant in")
		);
		
		$z = 0;
		while($l = gzgets($this->_in,2048)) {
			if($l[0] == '!') continue;
			$a = explode("\t",trim($l));

			$id = $a[1];
			$term = substr($a[4],3);
			$goi = $id."_".$term;
			$got = $goterms[$a[8]];

			$buf .= "$sgd:$id $ss:".$got['p']." $sgd:$goi .".PHP_EOL;
			$buf .= "$sgd:$goi a $go:$term .".PHP_EOL;
			$buf .= "$sgd:$goi rdfs:label \"$sgd$id ".$got['plabel']." $go:$term \" .".PHP_EOL;
			$buf .= "$go:$term rdfs:subClassOf $ss:".$got['type']." .".PHP_EOL;
			
			$goa = "goa_".($z++);
			$buf .= "$sgd:$goa a $ss:Evidence .".PHP_EOL;
			$buf .= "$sgd:$goa rdfs:label \"Evidence of ".strtolower($got['type'])." for $sgd:$id \".".PHP_EOL;
			$buf .= "$sgd:$goa $ss:evidenceFor $sgd:$goi .".PHP_EOL;
			$buf .= "$sgd:$goi $ss:hasEvidence $sgd:$goa .".PHP_EOL;

			if(isset($a[5])) {
				$b = explode("|",$a[5]);
				foreach($b as $c) {
					$d = explode(":",$c);
					if($d[0] == "pmid") {
						$buf .= "$sgd:$goa $ss:article $pubmed:$d[1] .".PHP_EOL;
					}
				}
			}
			if(isset($a[6])) {
				$buf .= "$sgd:$goa a $evd:$a[6] .".PHP_EOL;
			}
			
//			echo $buf;exit;
		}
		fwrite($this->_out, $buf);
		
		return 0;
	}

};

?>
