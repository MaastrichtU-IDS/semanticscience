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
	
	
	// MI:0314 - Complex
	// 
	$z = 0;
	fgets($infp);
	while($l = fgets($infp)) {
		$a = explode("\t",trim($l));
		
		$type = $a[11]=="NA"?"ss:Complex":$a[11];
		
		$ids = explode("|",$a[13]);
		$iid = $ids[0];

		$buf .= "$iid dc:identifier \"$iid\".".PHP_EOL;
		$rel = $a[20];
		if($rel == 'Y') {
			$homodimer = true;
			// homodimer 
			$buf .= "$iid a ss:SelfInteraction.".PHP_EOL;
		} else if($rel == 'C') {
			// complex
			$buf .= "$iid a ss:Complex.".PHP_EOL;
		} else {
			$buf .= "$iid a ss:Interaction.".PHP_EOL;
		}

		BreakName($a[17], &$ns1, &$id1, &$label1);
		BreakName($a[18], &$ns2, &$id2, &$label2);
		
	
		BreakName($a[11],  &$ns4, &$itypeid, &$itlabel);
		$itype = 'interaction';
		if($ns4 != '' && $itypeid != 'NA') {
			$buf .= "$iid rdf:type $ns4:$itypeid .".PHP_EOL;
			$mlabel = "$itlabel";
			$oids["$ns4:$itypeid"] = $itlabel;
		}
		
		BreakName($a[6],  &$ns3, &$mid, &$ml);
		$mlabel = '';
		if($mid != '0000') {
			$buf .= "$iid bio2rdf:method $ns3:$mid .".PHP_EOL;
			$mlabel = "identified by $ml";
			$oids["$ns3:$mid"] = $ml;
		}
		
		$buf .= "$iid rdfs:label \"$label1-$label2 $itype between $a[2] and $a[3] $mlabel [$iid]\".".PHP_EOL;
		foreach($ids AS $idstring) {
			$buf .= "$iid owl:sameAs $idstring .".PHP_EOL;
		}
		
		$buf .= "$iid bio2rdf:component $a[0].".PHP_EOL;
		
		$buf .= "$a[0] bio2rdf:interactsWith $a[1].".PHP_EOL;
		BreakName($type,$ns,$id,$label);
		$buf .= "$iid a $ns:$id.".PHP_EOL;
		
		$c = explode("|",$a[2]);
		foreach($c as $lid) {
			BreakName($lid,$ns,$id,$label);
			if(isset($nsmap[$ns])) $ns = $nsmap[$ns];
			$buf .= "$a[0] owl:sameAs $ns:$id.".PHP_EOL;
		}
		if($a[9] != 'NA') $buf .= "$a[0] bio2rdf:organism ".str_replace("taxid","taxon",$a[9]).".".PHP_EOL;
		if(!$homodimer) {
			$buf .= "$iid bio2rdf:component $a[1].".PHP_EOL;
			$c = explode("|",$a[3]);
			foreach($c as $lid) {
				BreakName($lid,$ns,$id,$label);
				if(isset($nsmap[$ns])) $ns = $nsmap[$ns];
				$buf .= "$a[1] owl:sameAs $ns:$id.".PHP_EOL;
			}
			if($a[10] != 'NA') $buf .= "$a[1] bio2rdf:organism ".str_replace("taxid","taxon",$a[10]).".".PHP_EOL;
		}
		
		// ref
		$pubs = explode("|",$a[8]);
		foreach($pubs AS $pub) {
			$b = explode(":",$pub);
			if(!is_numeric($b[1]) || $b[1] == "-1") continue;
			$buf .= "$iid bio2rdf:article $b[0]:$b[1].".PHP_EOL;
		}
		
		$dbs = explode("|",$a[12]);
		foreach($dbs AS $db) {
			BreakName($db,$ns,$id,$label);
			$buf .= "$iid bio2rdf:provenance $ns:$id.".PHP_EOL;
			$oids["$ns:$id"] = $label;
		}
	
		
		
		//if($z++ == 6) {echo $buf;echo TriplesFromLabel($oids);exit;}
	}
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