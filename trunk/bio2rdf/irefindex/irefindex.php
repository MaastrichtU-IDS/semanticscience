<?php
require('../include.php');

$infile  = "562.mitab.10172008.txt";
$indir = "/data/irefindex/";
$outdir = "/data/irefindex/n3/";
$outfile = "irefindex.n3";

$infp = fopen($indir.$infile,"r");
if(!$infp) {trigger_error("Unable to open ".$outdir.$infile);exit;}

$outfp = fopen($outdir.$outfile,"w");
if(!$outfp) {trigger_error("Unable to open ".$outdir.$outfile);exit;}

irefindex($infp,$outfp);

	
/** 
(0)uidA 	uidB	altA	altB	aliasA	
(5)aliasB  method	author	pmids	taxai
(10)taxb 	interactionType	sourcedb	interactionIdentifiers	confidence
(15)entrezGeneA 	entrezGeneB	atype	btype	rigid	
(20)edgetype 	numParticipants
*/
function irefindex($infp, $outfp)
{
	include ('../include.php');
	$buf = N3NSHeader($nslist);
	$oids = '';
		
	$nsmap = array(
		'emb' => 'embl',
		'gb' => 'ncbi',
		'taxid' => 'taxon',
		'uniprotkb' => 'uniprot',
		'entrezgene/locuslink' => 'geneid',
		'dbj' => 'ddbj',
		'kegg:ecj' => 'kegg'
	);
	

	$z = 0;
	$liid = ''; // last interaction id
	fgets($infp);
	while($l = fgets($infp)) {
		$a = explode("\t",trim($l));
		
		$ids = explode("|",$a[13]);
		$iid = $ids[0]; // the irefindex indentifier
		$buf .= "$iid dc:identifier \"$iid\".".PHP_EOL;
		if(!$liid) $liid = $iid; // first setting
		// process the other ids
		array_shift($ids);
		foreach($ids AS $id) {
			BreakName($id, &$id_ns, &$id, &$id_label);
			$buf .= "$iid owl:sameAs $id_ns:$id .".PHP_EOL;
		}
			
		// MI-specified interaction type
		BreakName($a[11], &$it_ns, &$it_id, &$it_label);
		if($it_ns != '' && $it_id != 'NA') {
			$buf .= "$iid a $it_ns:$it_id .".PHP_EOL;
			$oids["$it_ns:$it_id"] = $it_label; // keep a list of MI entities to generate labels
		}
		
		// MI-specified method
		BreakName($a[6],  &$m_ns, &$m_id, &$m_label);
		if($mid != '0000') {
			$buf .= "$iid bio2rdf:method $m_ns:$m_id .".PHP_EOL;
			if($m_label == '-1') $m_label = 'by unspecified method';
			else {
				$oids["$m_ns:$m_id"] = $m_label;
				$m_label = "identified by $m_label"; // for label generation
			}
		}
		
		// Participants
		for($i=0;$i<2;$i++) { // the irefindex participant ids are at elements 0 and 1 of the array
			$pid = $i+2; // the other ids for the irefindex are at elements 2 and 3 of the array
			$other_ids = explode("|",$a[$pid]);
			foreach($other_ids as $oid) {
				BreakName($oid,$oid_ns,$oid_id,$oid_label);
				if(isset($nsmap[$oid_ns])) $oid_ns = $nsmap[$oid_ns]; // check to see whether we're mapping the namespace
				$buf .= "$a[$i] owl:sameAs $oid_ns:$oid_id.".PHP_EOL;
			}
			// organism
			if($a[9] != 'NA') $buf .= "$a[$i] bio2rdf:organism ".str_replace("taxid","taxon",$a[9]).".".PHP_EOL;
		}
		// Participant types
		BreakName($a[17], &$i1_type_ns, &$i1_type_id, &$i1_type_label);
		BreakName($a[18], &$i2_type_ns, &$i2_type_id, &$i2_type_label);
		$buf .= "$a[0] a $i1_type_ns:$i1_type_id .".PHP_EOL;
		$buf .= "$a[1] a $i2_type_ns:$i2_type_id .".PHP_EOL;
		$oids["$i1_type_ns:$i1_type_id"] = $i1_type_label;
		$oids["$i2_type_ns:$i2_type_id"] = $i2_type_label;
		

		// relate the interaction to the participants, complex to the parts
		$label = '';
		$rel = $a[20];
		$num = $a[21];
		if($rel == 'C') {
			// add the the part
			$buf .= "$iid ss:hasProperPart $a[1].".PHP_EOL;	
			$complexes [$iid][] = $a[1]; // keep this list to generate the labels at the end;		
			$type = 'Complex';
			$label = "$num component complex $m_label";
		} else {
			if($rel == 'Y') {
				if(!$it_label) $it_label = 'Interaction';
				if($num == 1) {
					$type = 'SelfInteraction';
					$label = "$m_label Interaction of $a[2] with itself";
					$buf .= "$iid ss:hasAgent $a[0].".PHP_EOL;
					// interacts with itself
				} else {
					$type = 'HomoInteraction';
					$label = "$it_label between two molecules of $a[2] $m_label";
					$buf .= "$iid ss:hasParticipant $a[0].".PHP_EOL;
					// has exactly 2 of this type
					/* @todo
					<rdf:type>
						<owl:Restriction>
							<owl:onProperty rdf:resource="&ontology;hasPart"/>
							<owl:onClass rdf:resource="&ontology;Protein"/>
							<owl:qualifiedCardinality rdf:datatype="&xsd;nonNegativeInteger">2</owl:qualifiedCardinality>
						</owl:Restriction>
					</rdf:type>
					*/					
				}
			} else if($rel == 'X') {
				$type = 'HeteroInteraction';
				$buf .= "$iid ss:hasParticipant $a[0].".PHP_EOL;
				$buf .= "$iid ss:hasParticipant $a[1].".PHP_EOL;
				$label = "$i1_type_label-$i2_type_label $it_label between $a[0] and $a[1] $m_label";
			} else {
				trigger_error("Unhandled type of interaction $rel");
				exit;
			}
		}
		$buf .= "$iid a ss:$type .".PHP_EOL;
		$buf .= "$iid irefindex:number_of_interactors \"$num\".".PHP_EOL;
		if($label) $buf .= "$iid rdfs:label \"$label [$iid]\".".PHP_EOL;
	
		
		// article
		$pubs = explode("|",$a[8]);
		foreach($pubs AS $pub) {
			$b = explode(":",$pub);
			if(!is_numeric($b[1]) || $b[1] == "-1") continue;
			$buf .= "$iid bio2rdf:article $b[0]:$b[1].".PHP_EOL;
		}
		
		// provenance
		$dbs = explode("|",$a[12]);
		foreach($dbs AS $db) {
			BreakName($db,$ns,$id,$label);
			$buf .= "$iid bio2rdf:provenance $ns:$id.".PHP_EOL;
			$oids["$ns:$id"] = $label;
		}
		
		// confidence
		$confidences = explode("|",$a[14]);
		foreach($confidences AS $c) {
			// label:score
			BreakName($c,&$label,&$score, &$nothing);
			$buf .= "$iid irefindex:$label \"$score\".".PHP_EOL;
		}
		
		$liid = $iid;
	}

	//echo $buf;echo TriplesFromLabel($oids);exit;
			
	
	fwrite($outfp,$buf);
	fwrite($outfp,TriplesFromLabel($oids));
	return 0;
}


// a name of the ns:id(label)
function BreakName($name, &$ns, &$id, &$label)
{
	preg_match("/(.*):(.*)/",$name,$matches);
	$ns = strtolower($matches[1]);
	$id = $matches[2];
	preg_match("/(.*)\((.*)\)/",$matches[2],$m);
	if(count($m)) {
		$id = $m[1];
		$label = $m[2];
	}
}
function TriplesFromLabel($list)
{
	$buf = '';
	foreach($list AS $id => $label) {
		$buf .= "$id rdfs:label \"$label [$id]\".".PHP_EOL;;
	}
	return $buf;

}
?>