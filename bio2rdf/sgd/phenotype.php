<?php

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
	
/*
0) Feature Name (Mandatory)     		-The feature name of the gene
1) Feature Type (Mandatory)     		-The feature type of the gene	
2) Gene Name (Optional) 			-The standard name of the gene
3) SGDID (Mandatory)    			-The SGDID of the gene
4) Reference (SGD_REF Required, PMID optional)  -PMID: #### SGD_REF: #### (separated by pipe)(one reference per row)
5) Experiment Type (Mandatory)     		-The method used to detect and analyze the phenotype
6) Mutant Type (Mandatory)      		-Description of the impact of the mutation on activity of the gene product
7) Allele (Optional)    			-Allele name and description, if applicable
8) Strain Background (Optional) 		-Genetic background in which the phenotype was analyzed
9) Phenotype (Mandatory)       		-The feature observed and the direction of change relative to wild type
10) Chemical (Optional) 			-Any chemicals relevant to the phenotype
11) Condition (Optional)        		-Condition under which the phenotype was observed
12) Details (Optional)  			-Details about the phenotype
13) Reporter (Optional) 			-The protein(s) or RNA(s) used in an experiment to track a process 

AUT6	not physically mapped	AUT6	S000029048	PMID: 8663607|SGD_REF: S000057871	classical genetics	reduction of function		Other	autophagy: absent		nitrogen starvation + 1 mM PMSF	autophagosomes not observed	
	*/
	function Convert2RDF()
	{
		require ('../../lib/php/oboparser_lib.php');
		
		/** get the ontology terms **/
		$file = "/data/obo/yeast_phenotype_v1.15.obo";
		$in = fopen($file, "r");
		if($in === FALSE) {
			trigger_error("Unable to open $file");
			exit;
		}
		$terms = OBOParser($in);
		fclose($in);
		
		BuildNamespaceSearchList($terms,$searchlist);
				
		
		require ('../include.php');
		$buf = N3NSHeader($nslist);
		$buf .= "@prefix apo: <http://bio2rdf.org/apo:>.".PHP_EOL;
		
		while($l = fgets($this->_in,96000)) {
			if(trim($l) == '') continue;
			
			$a = explode("\t",trim($l));
			
					
			$eid =  md5($a[3].$a[5].$a[6].$a[9]);
			
			$label = "$a[0] - $a[5] experiment with $a[6] resulting in phenotype of $a[9]";
			$buf .= "$sgd:$eid $rdfs:label \"$label [$sgd:$eid]\" .".PHP_EOL;
			$buf .= "$sgd:$eid a $sgd:PhenotypeExperiment .".PHP_EOL;
			
			$buf .= "$sgd:$eid $bio2rdf:gene $sgd:$a[3].".PHP_EOL;
			
			// reference
			// PMID: 12140549|SGD_REF: S000071347
			$b = explode("|",$a[4]);
			foreach($b AS $c) {
				$d = explode(" ",$c);
				if($d[0] == "PMID:") $ns = "pmid";
				else $ns = "sgd";
				$buf .= "$sgd:$eid $bio2rdf:article $ns:$d[1].".PHP_EOL;
			}
			
			// experiment type [5]
			preg_match("/(.*) \((.*)\)/",$a[5],$m);
			if(count($m)) {
				$label = $m[1];
				$details = $m[2];
				$buf .= "$sgd:$eid $sgd:experiment_comment \"$details\".".PHP_EOL;
			} else {
				$label = $a[5];
			}
			$id = array_search($label, $searchlist['experiment_type']);	
			if($id !== FALSE) 
				$buf .= "$sgd:$eid $sgd:experiment_type ".strtolower($id).".".PHP_EOL;
		
			// mutant type [6]
			$id = array_search($a[6], $searchlist['mutant_type']);
			if($id !== FALSE) 
				$buf .= "$sgd:$eid $sgd:mutant_type ".strtolower($id).".".PHP_EOL;
			
			// phenotype  [9]
			// presented as observable: qualifier
			$b = explode(": ",$a[9]);
			$id = array_search($b[0], $searchlist['observable']);
			if($id !== FALSE) 
				$buf .= "$sgd:$eid $sgd:observable ".strtolower($id).".".PHP_EOL;
			
			$id = array_search($b[1], $searchlist['qualifier']);
			if($id !== FALSE) 
				$buf .= "$sgd:$eid $sgd:qualifier ".strtolower($id).".".PHP_EOL;
			
/*
7) Allele (Optional)    			-Allele name and description, if applicable
8) Strain Background (Optional) 		-Genetic background in which the phenotype was analyzed
10) Chemical (Optional) 			-Any chemicals relevant to the phenotype
11) Condition (Optional)        		-Condition under which the phenotype was observed
12) Details (Optional)  			-Details about the phenotype
13) Reporter (Optional) 			-The protein(s) or RNA(s) used in an experiment to track a process 
*/

			if($a[7] != '') $buf .= "$sgd:$eid $sgd:allele \"$a[7]\".".PHP_EOL;
			if($a[8] != '') $buf .= "$sgd:$eid $sgd:background \"$a[8]\".".PHP_EOL;
			if($a[10] != '') $buf .= "$sgd:$eid $sgd:chemical \"$a[10]\".".PHP_EOL;
			if($a[11] != '') $buf .= "$sgd:$eid $sgd:condition \"$a[11]\".".PHP_EOL;
			if($a[12] != '') $buf .= "$sgd:$eid $sgd:details \"$a[12]\".".PHP_EOL;
			//if($a[13] != '') $buf .= "$sgd:$eid $sgd:reporter \"$a[13]\".".PHP_EOL;
			
			/*
			if(count($m)) echo $buf;
			$buf = '';
			*/
			
		}		
		fwrite($this->_out, $buf);
		return 0;
	}
};

?>