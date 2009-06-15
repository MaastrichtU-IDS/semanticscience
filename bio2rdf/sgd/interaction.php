<?php

class SGD_interaction_data {

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
interactions_data.tab

Contains interaction data incorporated into SGD from BioGRID (http://www.thebiogrid.org/).  Tab-separated columns are:

1) Feature Name (Bait) (Required)       	- The feature name of the gene used as the bait
2) Standard Gene Name (Bait) (Optional) 	- The standard gene name of the gene used as the bait
3) Feature Name (Hit) (Required)        	- The feature name of the gene that interacts with the bait
4) Standard Gene Name (Hit) (Optional)  	- The standard gene name of the gene that interacts with the bait
5) Experiment Type (Required)   		- A description of the experimental used to identify the interaction
6) Genetic or Physical Interaction (Required)   - Indicates whether the experimental method is a genetic or physical interaction
7) Source (Required)    			- Lists the database source for the interaction
8) Manually curated or High-throughput (Required)	- Lists whether the interaction was manually curated from a publication or added as part of a high-throughput dataset
9) Notes (Optional)     			- Free text field that contains additional information about the interaction
10) Phenotype (Optional)        		- Contains the phenotype of the interaction
11) Reference (Required)        		- Lists the identifiers for the reference as an SGDID (SGD_REF:) or a PubMed ID (PMID:)
12) Citation (Required) 			- Lists the citation for the reference
*/
	function Convert2RDF()
	{
		require ('../include.php');
		$buf = N3NSHeader($nslist);
		
		$z = 0;
		while($l = fgets($this->_in,2048)) {
			list($id1,$id1name, $id2, $id2name, $experiment_type, $method, $src, $htpORman, $notes, $phenotype, $ref, $cit) = explode("\t",trim($l));;
			
			$id = md5($id1.$id2.$method.$cit);
			$buf .= "$sgd:$id a $sgd:Interaction.".PHP_EOL;
			$buf .= "$sgd:$id $dc:identifier \"$id\".".PHP_EOL;
			$buf .= "$sgd:$id $rdfs:label \"$htpORman ".substr($method,0,-1)." between $id1 and $id2 [$sgd:$id]\".".PHP_EOL;
			
			$id1 = str_replace(array("(",")"), array("",""), $id1);
			$id2 = str_replace(array("(",")"), array("",""), $id2);
			
			$buf .= "$sgd:$id $sgd:bait $sgd:$id1 .".PHP_EOL;
			$buf .= "$sgd:$id $sgd:hit $sgd:$id2 .".PHP_EOL;
			
			$exp = $this->GetExperimentType($experiment_type);
			$eid = $id."exp";
			$buf .= "$sgd:$id $sgd:experiment $sgd:$eid .".PHP_EOL;
			$buf .= "$sgd:$eid a $exp .".PHP_EOL;
			
			$buf .= "$sgd:$id a $sgd:".($method=="genetic interactions"?"GeneticInteraction":"PhysicalInteraction")." .".PHP_EOL;
			if($phenotype) $buf .= "$sgd:$id $sgd:phenotype \"$phenotype\" .".PHP_EOL;
			if($htpORman)  $buf .= "$sgd:$id a $sgd:".($htpORman=="manually curated"?"ManuallyCuratedInteraction":"HighThroughputInteraction")." .".PHP_EOL;
			$b = explode("|",$ref);
			foreach($b AS $c) {
				$d = explode(":",$c);
				if($d[0]=="PMID") $buf .= "$sgd:$id $sgd:article $pubmed:$d[1] .".PHP_EOL;
			}
			
			$buf .= "$sgd:$id1 $sgd:interactsWith $sgd:$id2 .".PHP_EOL;
			$buf .= "$sgd:$id2 $sgd:interactsWith $sgd:$id1 .".PHP_EOL;
			
			if(defined('DEBUG')) {echo $buf;break;}
		}
		fwrite($this->_out, $buf);
		
		return 0;
	}
	function GetExperimentType($index) {
	$interaction_type = array(
		'Synthetic Lethality' => 'SyntheticLethality',
		'Affinity Capture-MS' => 'AffinityCapture-MS',
		'Affinity Capture-Western' => 'AffinityCapture-Western',
		'Affinity Capture-RNA' => 'AffinityCapture-RNA',
		'Dosage Rescue' => 'DosageRescue',
		'Dosage Lethality' => 'DosageLethality',
		'Dosage Growth Defect' => 'DosageGrowthDefect',
		'Reconstituted Complex' => 'ReconstitutedComplex',
		'Synthetic Growth Defect' => 'SyntheticGrowthDefect',
		'Synthetic Rescue' => 'SyntheticRescue',
		'Two-hybrid' => 'TwoHybrid',
		'Epistatic MiniArray Profile' => 'EpistaticMiniArrayProfile',
		'Biochemical Activity' => 'BiochemicalActivity',

		'Far Western' => 'FarWestern',
		'FRET' => 'FRET',
		'Protein-peptide' => 'ProteinPeptideInteractionExperiment',
		'Protein-RNA' => 'ProteinRNAInteractionExperiment',
		'Co-crystal Structure' => 'Co-crystallography',
		'Co-localization' => 'Co-localization',
		'Co-purification' => 'Co-purification',
		'Co-fractionation' => 'Co-fractionation',
		'Phenotypic Enhancement' => 'PhenotypicEnhancement',
		'Phenotypic Suppression' => 'PhenotypicSuppression'
	);
	return $interaction_type[$index];
}
};

?>