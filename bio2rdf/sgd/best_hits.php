<?php

class SGD_BESTHITS {

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
		
		while($l = fgets($this->_in,2048)) {
			$a = explode("\t",trim($l));
			
			$id1 = $a[0];
			$id2 = $a[7];
			preg_match("/\:|\(|\)|\'/",$id2,$matches);
			if(count($matches)) continue;
			$id = "aln/$id1/$id2";
			$uid = "$sgd:$id";
		
			$buf .= "$uid $rdfs:label \"BLAST alignment between $id1 and $id2 [$sgd:$id]\" .".PHP_EOL;
			$buf .= "$uid a $sgd_resource:BLASTAlignment.".PHP_EOL;
			$buf .= "$uid $sgd_resource:query $sgd:$id1 .".PHP_EOL;
			$buf .= "$uid $sgd_resource:target $sgd:$id2 .".PHP_EOL;
			$buf .= "$uid $sgd_resource:query_start \"$a[1]\" .".PHP_EOL;
			$buf .= "$uid $sgd_resource:query_stop \"$a[2]\" .".PHP_EOL;
			$buf .= "$uid $sgd_resource:target_start \"$a[3]\" .".PHP_EOL;
			$buf .= "$uid $sgd_resource:target_stop \"$a[4]\" .".PHP_EOL;
			$buf .= "$uid $sgd_resource:percent_aligned \"$a[5]\" .".PHP_EOL;
			$buf .= "$uid $sgd_resource:score \"$a[6]\" .".PHP_EOL;
			$buf .= "$sgd:$id2 $ss:SIO_010079 $taxon:".$a[8]." .".PHP_EOL;
			//echo $buf;exit;
			
		}
		fwrite($this->_out, $buf);
		
		return 0;
	}

};

?>
