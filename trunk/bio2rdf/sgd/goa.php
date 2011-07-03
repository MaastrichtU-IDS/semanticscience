<?php

class SGD_GOA {

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

			$id = $a[1]."gp";

			$term = substr($a[4],3);
			$goi = $id."_".$term;
			$got = $goterms[$a[8]];

			$buf .= "$sgd:$id $ss:".$got['p']." $sgd:$goi .".PHP_EOL;
			$buf .= "$sgd:$goi a $go:$term .".PHP_EOL;
			$buf .= "$sgd:$goi rdfs:label \"$sgd$id ".$got['plabel']." $go:$term \" .".PHP_EOL;
			$buf .= "$go:$term rdfs:subClassOf $ss:".$got['type']." .".PHP_EOL;
			
			$goa = "goa_".($z++);
			$buf .= "$sgd:$goa rdfs:label \"Evidence of ".strtolower($got['type'])." for $sgd:$id \".".PHP_EOL;
			$buf .= "$sgd:$goa $ss:evidence_for $sgd:$goi .".PHP_EOL;
			$buf .= "$sgd:$goi $ss:has_evidence $sgd:$goa .".PHP_EOL;

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
				$code = MapECO($a[6]);
				if($code) $buf .= "$sgd:$goa a $eco:$code .".PHP_EOL;
				else echo "No mapping for $a[6]".PHP_EOL;
			}
			
//			echo $buf;exit;
		}
		fwrite($this->_out, $buf);
	print_r($evd);	
		return 0;
	}

};


function MapECO($eco)
{
 $c = array(
"ISS" => "0000027", 
"IGI" => "0000011",
"IMP" => "0000015",
"IDA" => "0000002",
"IEA" => "00000067",
"TAS" => "0000033",
"RCA" => "0000053",
"ISA" => "00000057",
"IEP" => "0000008",
"ND" => "0000035",
"IC" => "0000001",
"IPI" => "0000021",
"NAS" =>"0000034",
"ISM" => "00000063",
"ISO" =>"00000060",
);
  if(isset($c[$eco])) return $c[$eco];
  else return NULL;
}

?>
