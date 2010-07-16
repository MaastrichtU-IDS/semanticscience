<?php
require(dirname(__FILE__).'/../include.php');

$date = "08212009";
$date = "10272009";
$infile = "All.mitab.$date.txt";
$rfile = 'ftp://ftp.no.embnet.org/irefindex/data/current/psimi_tab/'.$file;

$indir = DATA."/irefindex/";
$outdir = DATA."/irefindex/n3/";
$outfile = "irefindex.n3.gz";

$infp = fopen($indir.$infile,"r");
if(!$infp) {trigger_error("Unable to open ".$outdir.$infile);exit;}

$outfp = gzopen($outdir.$outfile,"w");
if(!$outfp) {trigger_error("Unable to open ".$outdir.$outfile);exit;}

irefindex($infp,$outfp);

fclose($infp);
gzclose($outfp);




/** 
(0)uidA 	uidB	altA	altB	aliasA	
(5)aliasB  method	author	pmids	taxai
(10)taxb 	interactionType	sourcedb	interactionIdentifiers	confidence
(15)entrezGeneA 	entrezGeneB	atype	btype	rigid	
(20)edgetype 	numParticipants
*/
function irefindex($infp, $outfp)
{
	include (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	$oids = '';
		
	$nsmap = array(
		'emb' => 'embl',
		'gb' => 'ncbi',
		'genbank_protein_gi' => 'ncbi',
		'taxid' => 'taxon',
		'uniprotkb' => 'uniprot',
		'uniprotkb/trembl' => 'uniprot',
		'entrezgene/locuslink' => 'geneid',
		'dbj' => 'ddbj',
		'kegg:ecj' => 'kegg',
		'mppi' => 'mips',
		'swiss-prot' => 'swissprot',
		'ddbj-embl-genbank' => 'ncbi',
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
			BreakName($id, &$id_ns, &$newid, &$id_label);
			if(isset($nsmap[$id_ns])) $id_ns = $nsmap[$id_ns];
			if($newid != '-') $buf .= "$iid owl:sameAs $id_ns:$newid .".PHP_EOL;
		}
			
		// MI-specified interaction type
		unset($interaction_type_labels);
		$interaction_types = explode("|",trim($a[11]));
		foreach($interaction_types AS $interaction_type) {
			if($interaction_type == '-' || $interaction_type == '') {$interaction_type_labels[] = 'Interaction';break;}

			BreakName($interaction_type, &$it_ns, &$it_id, &$it_label);
			if($it_id == '0000') { // a hack for bad ids
				if($it_label == '-') {$interaction_type_labels[] = 'unspecified interaction type';break;} //hopefully it's the only one
				else {
					// otherwise, we should generate a new id and label
					$it_ns = 'irefindex';
					AddNewIndividual($it_ns,$it_label,&$it_id,&$oids);
					$interaction_type_labels[] = $it_label;
				}
			} else { // a real id
				$interaction_type_labels[] = $it_label;
				$oids["$it_ns:$it_id"] = $it_label; // keep a list of MI entities to generate labels
			}
			$buf .= "$iid a $it_ns:$it_id .".PHP_EOL;
		}
		$it_label = implode(", ",$interaction_type_labels);
		
		// MI-specified method(s)
		$method_labels = '';
		$methods = explode("|",trim($a[6]));
		foreach($methods AS $method) {
			if($method == '-' || $method == '') {$method_labels[] = "unspecified method";break;}

			BreakName($method,  &$m_ns, &$m_id, &$m_label);
			if($m_id == '0000') { // a hack for bad ids
				if($m_label == '-') {$method_labels[] = 'unspecified method';break;} //hopefully it's the only one
				else {
					// hack
					if($m_label[0] == '"') $m_label = substr($m_label,1,-1);
					// otherwise, we should generate a new id and label
					$m_ns = 'irefindex';
					AddNewIndividual($m_ns,$m_label,&$m_id,&$oids);
					$method_labels[] = $m_label;
				}
			} else { // a real id
				// add the id
				$oids["$m_ns:$m_id"] = $m_label;
				$method_labels[] = $m_label; 
			}
			$buf .= "$iid $bio2rdfns:method $m_ns:$m_id .".PHP_EOL;
		}
		$m_label = strtolower('identified by '.implode(", ",$method_labels));
		
		// Participants
		for($i=0;$i<2;$i++) { // the irefindex participant ids are at elements 0 and 1 of the array
			$pid = $i+2; // the other ids for the irefindex are at elements 2 and 3 of the array
			$other_ids = explode("|",$a[$pid]);
			foreach($other_ids as $oid) {
				BreakName($oid,$oid_ns,$oid_id,$oid_label);
				if(isset($nsmap[$oid_ns])) $oid_ns = $nsmap[$oid_ns]; // check to see whether we're mapping the namespace

				if(strstr($oid_ns,"kegg")) { // special case for all the derivatives
					$buf .= "$a[$i] owl:sameAs <http://bio2rdf.org/$oid>.".PHP_EOL; 
				} else if(strstr($oid_ns,"geneid")) {
					$buf .= "$a[$i] $bio2rdfns:encodedBy $oid_ns:$oid_id.".PHP_EOL;
				} else if(strstr($oid_ns,"other")) {
					// nothing to do
				} else {
					$b = explode(":",$oid_ns);
					if(count($b) == 1) 
						$buf .= "$a[$i] owl:sameAs $oid_ns:$oid_id.".PHP_EOL;
				}
			}

			$pid = $i+4; // the aliases
			$other_ids = explode("|",trim($a[$pid]));
			foreach($other_ids as $oid) {
				BreakName($oid,$oid_ns,$oid_id,$oid_label);
				if(isset($nsmap[$oid_ns])) $oid_ns = $nsmap[$oid_ns]; // check to see whether we're mapping the namespace
				if($oid_id == '') continue;

				if(strstr($oid_ns,"kegg")) { // special case for all the derivatives
					$buf .= "$a[$i] rdfs:seeAlso <http://bio2rdf.org/$oid>.".PHP_EOL; 
				} else if(strstr($oid_ns,"geneid")) {
					if(is_numeric($oid_id))
						$buf .= "$a[$i] rdfs:seeAlso $oid_ns:$oid_id.".PHP_EOL;
				} else if(strstr($oid_ns,"other")) {
					// nothing to do
				} else {
					$buf .= "$a[$i] rdfs:seeAlso $oid_ns:$oid_id.".PHP_EOL;
				}
			}


			// organism
			if($a[9+$i] != '-') $buf .= "$a[$i] $bio2rdfns:organism ".str_replace("taxid","taxon",$a[9+$i]).".".PHP_EOL;
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
			$buf .= "$iid irefindex:has_part $a[1].".PHP_EOL;	
			$complexes [$iid][] = $a[1]; // keep this list to generate the labels at the end;		
			$type = 'Complex';
			$label = "$num component complex $m_label";
		} else {
			if($rel == 'Y') {
				if($num == 1) {
					$type = 'SelfInteraction';
					$label = "$m_label interaction of $a[2] with itself";
					$buf .= "$iid irefindex:has_participant $a[0].".PHP_EOL;
					// interacts with itself
				} else {
					$type = 'HomoInteraction';
					$label = "$it_label between two molecules of $a[2] $m_label";
					$buf .= "$iid irefindex:has_participant $a[0].".PHP_EOL;		
				}
			} else if($rel == 'X') {
				$type = 'HeteroInteraction';
				$buf .= "$iid irefindex:has_participant $a[0].".PHP_EOL;
				$buf .= "$iid irefindex:has_participant $a[1].".PHP_EOL;
				$label = "$it_label between $a[0]($i1_type_label) and $a[1]($i2_type_label)  $m_label";
			} else {
				trigger_error("Unhandled type of interaction $rel");
				exit;
			}
		}
		$buf .= "$iid a irefindex:$type .".PHP_EOL;
		$buf .= "$iid irefindex:number_of_interactors \"$num\".".PHP_EOL;
		if($label) $buf .= "$iid rdfs:label \"$label [$iid]\".".PHP_EOL;
	
		
		// article
		$pubs = explode("|",$a[8]);
		foreach($pubs AS $pub) {
			$b = explode(":",$pub);
			if(!is_numeric($b[1]) || $b[1] == "-1") continue;
			$buf .= "$iid $bio2rdfns:article $b[0]:$b[1].".PHP_EOL;
		}
		
		// provenance
		$dbs = explode("|",$a[12]);
		foreach($dbs AS $db) {
			BreakName($db,$ns,$id,$label);
			$c = explode(":",$ns);
			if(count($c) > 1) { // a hack due to file error
				$ns = $c[0];
				$id = $c[1];
			}
			if($id == '0000') {
				$ns = 'irefindex';
				AddNewIndividual($ns, $label,&$id,&$oids);
			}
			if(isset($nsmap[$ns])) $ns = $nsmap[$ns];

			$buf .= "$iid irefindex:source $ns:$id.".PHP_EOL;
			$oids["$ns:$id"] = $label;
		}
		
		// confidence
		$confidences = explode("|",$a[14]);
		foreach($confidences AS $c) {
			// label:score
			BreakName($c,&$label,&$score, &$nothing);
			if($score != '-') $buf .= "$iid $irefindex:$label \"$score\".".PHP_EOL;
		}
		
		$liid = $iid;

/*		if($z++ == 100) 
			{echo $buf;echo TriplesFromLabel($oids);exit;}
*/
		gzwrite($outfp,$buf);
		$buf = '';
	}	
	
	gzwrite($outfp,$buf);
	gzwrite($outfp,TriplesFromLabel($oids));
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

function AddNewIndividual($ns,$label,&$id,&$idlist)
{
	$id = md5($label);
	$idlist["$ns:$id"] = $label;	
}
					
?>
