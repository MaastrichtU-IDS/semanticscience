<?php

class SGD_DOMAINS {

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
		$domain_ns = array (
			"ProfileScan" => "profilescan",
			"superfamily" => "superfamily",
			"PatternScan" => "patternscan",
			"BlastProDom" => "blastprodom",
			"FPrintScan" => "fprintscan",
			"Gene3D" => "gene3d",
			"Seg" => "seg",
			"HMMSmart" => "hmmsmart",
			"HMMPanther" => "hmmpanther",
			"HMMPfam" => "hmmpfam",
			"HMMPIR" => "hmmpir",
			"HMMTigr" => "hmmtigr"
		);
		
		
		require ('../include.php');
		$buf = N3NSHeader($nslist);

		while($l = fgets($this->_in,2048)) {
			$a = explode("\t",trim($l));

			$id = $a[0];
			$uid = '<http://bio2rdf.org/sgd:'.$id.'>';
			
			$domain = $domain_ns[$a[3]].":".$a[4];
			$udomain = '<http://bio2rdf.org/'.$domain.'>';

			$did   = "did/$id/$a[4]";
			$udid = '<http://bio2rdf.org/sgd:'.$did.'>';
			
			$buf .= "$uid $ss:encodes $udid .".PHP_EOL;	
			$buf .= "$udid a $udomain .".PHP_EOL;
			$buf .= "$udid $rdfs:label \"$domain domain encoded by [$sgd:$id]\" .".PHP_EOL;
			$buf .= "$udid a $ss:Domain .".PHP_EOL;

			$da = "da/$id/$a[4]/$a[6]/$a[7]";
			$uda = '<http://bio2rdf.org/sgd:'.$da.'>';
			
			$buf .= "$uda $rdfs:label \"domain alignment between $sgd:$id and $domain [$sgd:$da]\" .".PHP_EOL;
			$buf .= "$uda a $ss:DomainAlignment .".PHP_EOL;
			$buf .= "$uda $ss:query $uid .".PHP_EOL;
			$buf .= "$uda $ss:target $udomain .".PHP_EOL;
			$buf .= "$uda $ss:query_start \"$a[6]\" .".PHP_EOL;
			$buf .= "$uda $ss:query_stop \"$a[7]\" .".PHP_EOL;
			$buf .= "$uda $ss:evalue \"$a[8]\" .".PHP_EOL;
			$buf .= "$udid $ss:evidence $uda .".PHP_EOL;
			$buf .= "$uda $ss:is_evidence_for $udid .".PHP_EOL;
//echo $buf;exit;
		}
		fwrite($this->_out, $buf);
		
		return 0;
	}

};

?>
