<?php
/*
1.   Primary SGDID (mandatory)
2.   Feature type (mandatory)
3.   Feature qualifier (optional)
4.   Feature name (optional)
5.   Standard gene name (optional)
6.   Alias (optional, multiples separated by |)
7.   Parent feature name (optional)
8.   Secondary SGDID (optional, multiples separated by |)
9.   Chromosome (optional)
10.  Start_coordinate (optional)
11.  Stop_coordinate (optional)
12.  Strand (optional)
13.  Genetic position (optional)
14.  Coordinate version (optional)
15.  Sequence version (optional)
16.  Description (optional)
*/
class SGD_ChromosomalFeatures {

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
			if($l[0] == '!') continue;
			$a = explode("\t",trim($l));
			
			$id = $oid = $a[0];
			$id = str_replace(array("(",")"), array("&#40;","&#41;"), $id);
				
			$buf .= "$sgd:$id $dc:identifier \"$sgd:$oid\" .".PHP_EOL;
			$buf .= "$sgd:$id $rdfs:label \"$a[1] [$sgd:$id]\" .".PHP_EOL;
			if($a[15]) $buf .= "$sgd:$id $rdfs:comment ".'"""'.$a[15].'""" .'.PHP_EOL;
			$feature_type = $this->GetFeatureType($a[1]);
			$buf .= "$sgd:$id a $ss:$feature_type. ".PHP_EOL;
			
			// feature qualifiers (uncharacterized, verified, silenced_gene, dubious)
			if($a[2]) {
				$qualifiers = explode("|",$a[2]);
				foreach($qualifiers AS $q) {
					$buf .= "$sgd:$id $sgd:status \"$q\" .".PHP_EOL;
				}		
			}
			
			// unique feature name\
			$id2 = str_replace(array("(",")"), array("&#40;","&#41;"), $a[3]);
			if($a[3]) {
				$buf .= "$sgd:$id $owl:sameAs <http://bio2rdf.org/$sgd:$id2> .".PHP_EOL;
			}
			
			// common names
			if($a[3]) $buf .= "$sgd:$id $sgd:preferredName \"$a[3]\".".PHP_EOL;
			if($a[4]) $buf .= "$sgd:$id $sgd:standardName \"$a[4]\".".PHP_EOL;
			if($a[5]) {
				$b = explode("|",$a[5]);
				foreach($b AS $name) {
					$buf .= "$sgd:$id $sgd:alias \"$name\".".PHP_EOL;
				}
			}
			// parent feature
			$parent_type = '';
			if($a[6]) {
				$parent = str_replace(array("(",")"," "), array("&#40;","&#41;","_"), $a[6]);
				
				$buf .= "$sgd:$id $ss:isProperPartOf <http://bio2rdf.org/$sgd:$parent> .".PHP_EOL;
				$other .= "$sgd:$parent $ss:hasPart $sgd:$id .".PHP_EOL;
				if(strstr($parent,"chromosome")) {
					$parent_type = 'c';
					if(!isset($chromosomes[$parent])) $chromosomes[$parent] = '';
					else {
						$other .= "$sgd:$parent a $sgd:Chromosome .".PHP_EOL;
						$other .= "$sgd:$parent $rdfs:label \"$a[6]\" .".PHP_EOL;
					}
				}
			}
			// secondary sgd id (starts with an L)
			if($a[7]) {
				if($a[3]) {
					$b = explode("|",$a[7]);
					foreach($b AS $c) {
						$buf .= "$sgd:$id $owl:sameAs $sgd:$c.".PHP_EOL;
					}
				}
			}
			// chromosome
			if($a[8] && $parent_type != 'c') {
				$chr = "chromosome_".$a[8];
				$buf .= "$sgd:$chr $ss:hasProperPart $sgd:$id .".PHP_EOL;
			}
			
			// position
			if($a[9]) {
				$loc = $id."loc";
				$buf .= "$sgd:$id $sgd:location $sgd:$loc .".PHP_EOL;
				$buf .= "$sgd:$loc $dc:identifier \"[$sgd:$loc]\" .".PHP_EOL;
				$buf .= "$sgd:$loc a $sgd:Location .".PHP_EOL;
				$buf .= "$sgd:$loc $sgd:hasStartPosition \"$a[9]\" .".PHP_EOL;
				$buf .= "$sgd:$loc $sgd:hasStopPosition \"$a[10]\" .".PHP_EOL;
				if($a[13]) {
					$b = explode("|",$a[13]);
					foreach($b AS $c) {
						$buf .= "$sgd:$loc $sgd:modified \"$c\" .".PHP_EOL;
					}
				}
			}
			// watson or crick strand of the chromosome
			if($a[11]) {
				$chr = "chromosome_".$a[8];
				$strand_type = ($a[11]=="w"?"WatsonStrand":"CrickStrand");
				$strand = $chr."_".$strand_type;
				$buf .= "$sgd:$strand $sgd:part $sgd:$id .".PHP_EOL;
				if(!isset($strands[$strand])) {
					$strands[$strand] = '';
					$other .= "$sgd:$strand a sgd:$strand_type .".PHP_EOL;
					$other .= "$sgd:$strand $rdfs:label \"$strand_type for $chr\" .".PHP_EOL;
					$other .= "$sgd:$strand $sgd:isPartOf $sgd:$chr .".PHP_EOL;
				}				
			}
			if($a[14]) {
				$b = explode("|",$a[14]);
				foreach($b AS $c) {
					$buf .= "$sgd:$id $sgd:modified \"$c\" .".PHP_EOL;
				}
			}
			
//			echo $buf;exit;
		}
		fwrite($this->_out, $buf.$other);
		
		return 0;
	}

	function GetFeatureType($feature_id)
	{
		$feature_map = array (
		'ACS' => 'ARSConsensusSequence',
		'ARS consensus sequence' => 'AutonomouslyReplicatingSequence',
		'binding_site' => 'BindingSite',
		'CDEI' => 'CentromereDNAElementI',
		'CDEII' => 'CentromereDNAElementII',
		'CDEIII' => 'CentromereDNAElementIII',
		'CDS' => 'CodingSequence',
		'centromere' => 'Centromere',
		'external_transcribed_spacer_region' => 'ExternalTranscribedSpacer',
		'internal_transcribed_spacer_region' => 'InternalTranscribedSpacer',
		'intron' => 'Intron',
		'long_terminal_repeat' => 'LongTerminalRepeat',
		'ncRNA' => 'ncRNAGene',
		'noncoding_exon' => 'NonCodingExon',
		'non_transcribed_region' => 'NonTranscribedRegion',
	//	not in systematic sequence of S288C
		'not physically mapped' => 'NotPhysicallyMappedFeature',
		'ORF' => 'OpenReadingFrame',
		'plus_1_translational_frameshift' => 'TranslationalFrameshift',
		'pseudogene' => 'PseudoGene',
		'repeat_region' => 'RepeatRegion',
		'retrotransposon' => 'Retrotransposon',
		'rRNA' => 'rRNAGene',
		'snoRNA' => 'snoRNAGene',
		'snRNA' => 'snRNAGene',
		'telomere' => 'Telomere',
		'telomeric_repeat' => 'TelomericRepeat',
		'transposable_element_gene' => 'Retrotransposon',
		'tRNA' => 'rRNAGene',
		'X_element_combinatorial_repeats' => 'XElementCombinatorialRepeat',
		'X_element_core_sequence' => 'XElementCoreSequence',
		'Y\'_element' => 'YPrimeElement'
		);

	if(isset($feature_map[$feature_id])) return $feature_map[$feature_id];
	else return "ChromosomalFeature";
}
};

?>
