<?php

$indir = "/opt/data/pharmgkb/tsv/";
$outdir = "/opt/data/pharmgkb/n3/";

$files = array(
	"diseases", "drugs", "genes","relationships","variantAnnotations"
	//"genes"
);




foreach($files AS $file) {
	echo "processing $indir$file.tsv...";	
	$fp = fopen($indir.$file.".tsv","r");
	if($fp === FALSE) {
		trigger_error("Unable to open ".$indir.$file."tsv"." for writing.");
		exit;
	}
	$buf = $file($fp);
	fclose($fp);
	
	
	$out = fopen($outdir.$file.".n3","w");
	if($out === FALSE) {
		trigger_error("Unable to open ".$outdir.$file.".n3"." for writing.");
		exit;
	}
	
	require_once (dirname(__FILE__).'/../../lib/php/n3.php');
	require (dirname(__FILE__).'/../../lib/php/ns.php');
	
	$head = N3NSHeader($nslist);
	fwrite($out,$head.$buf);
	
	fclose($out);
	echo "done!".PHP_EOL;
}

/*
0 PharmGKB Accession Id	
1 Entrez Id	
2 Ensembl Id	
3 UniProt Id	
4 Name	
5 Symbol	
6 Alternate Names	
7 Alternate Symbols	
8 Is Genotyped	
9 Is VIP	
10 PD	
11 PK	
12 Has Variant Annotation
*/
function genes(&$fp)
{
	$buf = '';
	fgets($fp);
	while($l = fgets($fp,10000)) {
		$a = explode("\t",trim($l));
		
		$id = "pharmgkb:$a[0]";
		$buf .= "$id rdfs:label \"$a[4] [$id]\".".PHP_EOL;
		$buf .= "$id rdfs:subClassOf pharmgkb:Gene.".PHP_EOL;
		if($a[1]) $buf .= "$id owl:sameAs geneid:$a[1].".PHP_EOL;
		if($a[2]) $buf .= "$id owl:sameAs ensembl:$a[2].".PHP_EOL;
		if($a[3]) $buf .= "$id rdfs:seeAlso uniprot:$a[3].".PHP_EOL;
		if($a[4]) $buf .= "$id pharmgkb:name \"$a[4]\".".PHP_EOL;
		if($a[5]) $buf .= "$id pharmgkb:symbol \"$a[5]\".".PHP_EOL;
		if($a[6]) {
			$b = explode('",',$a[6]);
			foreach($b as $c) {
				if($c) $buf .= "$id pharmgkb:synonym \"".addslashes(stripslashes(substr($c,1)))."\".".PHP_EOL;
			}
		}
		if($a[7]) {
			$b = explode('",',$a[7]);
			foreach($b as $c) {
				if($c) $buf .= "$id pharmgkb:alternate_symbol $c\".".PHP_EOL;
			}
		}
		
		if($a[8]) $buf .= "$id pharmgkb:is_genotyped \"$a[8]\".".PHP_EOL;
		if($a[9]) $buf .= "$id pharmgkb:is_vip \"$a[9]\".".PHP_EOL;
		if($a[10] && $a[10] != '-') $buf .= "$id pharmgkb:pd \"true\".".PHP_EOL;
		if($a[11] && $a[11] != '-') $buf .= "$id pharmgkb:pk \"true\".".PHP_EOL;
		if($a[12]) $buf .= "$id pharmgkb:variant_annotation \"$a[12]\".".PHP_EOL;
	}
	return $buf;
}

/*
PharmGKB Accession Id
Name	
Alternate Names	
Type	
DrugBank Id
*/
function drugs(&$fp)
{
	fgets($fp);
	$buf = '';
	while($l = fgets($fp,200000)) {
		$a = explode("\t",trim($l));
		$id = "pharmgkb:$a[0]";
		
		//$buf .= "$id rdfs:subClassOf pharmgkb:Drug.".PHP_EOL;
		$buf .= "$id rdfs:label \"$a[1] [$id]\".".PHP_EOL;
		if($a[2] != '') {
			$b = explode('",',$a[2]);
			foreach($b AS $c) {
				if($c != '') $buf .= "$id pharmgkb:synonym \"".str_replace('"','',$c)."\".".PHP_EOL;
			}
		}
		if($a[3]) {
			$b = explode('",',$a[3]);
			foreach($b as $c) {
				if($c) $buf .= "$id pharmgkb:drugclass \"".addslashes(str_replace('"','',$c))."\".".PHP_EOL;
			}
		}
		if($a[4]) $buf .= "$id owl:sameAs drugbank:$a[4].".PHP_EOL;
		$buf .= "$id owl:sameAs pharmgkb:".md5($a[1]).".".PHP_EOL;
	}
	return $buf;
}

/*
0 PharmGKB Accession Id	
1 Name	
2 Alternate Names
*/
function diseases(&$fp)
{
  $buf = '';
  fgets ($fp);
  while($l = fgets($fp,10000)) {
	$a = explode("\t",trim($l));
	$id = "pharmgkb:".$a[0];
	$buf .= "$id rdfs:subClassOf pharmgkb:Disease.".PHP_EOL;
	$buf .= "$id rdfs:label \"".addslashes($a[1])." [$id]\".".PHP_EOL;
	$buf .= "$id pharmgkb:name \"".addslashes($a[1])."\".".PHP_EOL;
	if($a[2] != '') {
		$names = explode('",',$a[2]);
		foreach($names AS $name) {
			if($name != '') $buf .= "$id pharmgkb:synonyms $name\".".PHP_EOL;
		}
	}
	$buf .= "$id owl:sameAs pharmgkb:".md5($a[1]).".".PHP_EOL;
  }
  return $buf;

}

/*
0 Position on hg18
1 RSID
2 Name(s)	
3 Genes
4 Feature
5 Evidence
6 Annotation	
7 Drugs	
8 Drug Classes	
9 Diseases	
10 Curation Level	
11 PharmGKB Accession ID
*/
function variantAnnotations(&$fp)
{
  $buf = '';
  fgets($fp); // first line is header
  
  $hash = ''; // md5 hash list
  while($l = fgets($fp,10000)) {
	$a = explode("\t",trim($l));
	$id = "pharmgkb:$a[11]";
	
	$buf .= "$id pharmgkb:variant dbsnp:$a[1].".PHP_EOL;
	//$buf .= "$id rdfs:label \"variant [dbsnp:$a[1]]\"".PHP_EOL;
	if($a[2] != '') $buf .= "$id pharmgkb:variant_description \"".addslashes($a[2])."\".".PHP_EOL;
	
	if($a[3] != '' && $a[3] != '-') {
		$genes = explode(", ",$a[3]);
		foreach($genes AS $gene) {
			$gene = str_replace("@","",$gene);
			$buf .= "$id pharmgkb:gene pharmgkb:$gene.".PHP_EOL;
		}
	}
	
	if($a[4] != '') {
		$features = explode(", ",$a[4]);
		array_unique($features);
		foreach($features AS $feature) {
			$z = md5($feature); if(!isset($hash[$z])) $hash[$z] = $feature;
			$buf .= "$id pharmgkb:feature pharmgkb:$z.".PHP_EOL;
		}
	}
	if($a[5] != '') {
		//PubMed ID:19060906; Web Resource:http://www.genome.gov/gwastudies/
		$evds = explode("; ",$a[5]);
		foreach($evds AS $evd) {
			$b = explode(":",$evd);
			$key = $b[0];
			array_shift($b);
			$value = implode(":",$b);
			if($key == "PubMed ID") $buf .= "$id bio2rdf:article pubmed:$value.".PHP_EOL;
			else if($key == "Web Resource") $buf .= "$id bio2rdf:url <$value>.".PHP_EOL;
			else {
				// echo "$b[0]".PHP_EOL;
			}
		}
	}
	if($a[6] != '') { //annotation
		$buf .= "$id pharmgkb:description \"".addslashes($a[6])."\".".PHP_EOL;
	}
	if($a[7] != '') { //drugs
		$drugs = explode("; ",$a[7]);
		foreach($drugs AS $drug) {
			$z = md5($drug); if(!isset($hash[$z])) $hash[$z] = $drug;
			$buf .= "$id pharmgkb:drug pharmgkb:$z.".PHP_EOL;		
		}
	}

	if($a[9] != '') {
		$diseases = explode("; ",$a[9]);
		foreach($diseases AS $disease) {
			$z = md5($disease); if(!isset($hash[$z])) $hash[$z] = $disease;
			$buf .= "$id pharmgkb:disease pharmgkb:$z.".PHP_EOL;				
		}
	}
	if($a[10] != '') {
		$buf .= "$id pharmgkb:curation_status \"$a[8]\".".PHP_EOL;
	}	
  }
  foreach($hash AS $h => $label) {
	$buf .= "pharmgkb:$h rdfs:label \"$label\".".PHP_EOL;
  }
  return $buf;
}


/*
0 PharmGKB Accession Id
1 Resource Id (PMID or URL)
2 Relationship Type (discussed, related, postiviely related, negatively related)
3 Related Genes 
4 Related Drugs
5 Related Diseases
6 Categories of Evidence
7 PharmGKB Curated
*/
function relationships(&$fp)
{
  $buf = '';
  fgets($fp); // first line is header
  
  $hash = ''; // md5 hash list
  while($l = trim(fgets($fp,10000))) {
	
	$a = explode("\t",$l);
	
	$id = "pharmgkb:".$a[0];
	if($a[1] != '' && is_numeric($a[1])) $buf .= "$id owl:sameAs pubmed:".$a[1].".".PHP_EOL;
	
	$buf .= "$id pharmgkb:relationships \"".$a[2]."\".".PHP_EOL;
	$genes = explode(";",$a[3]);
	foreach($genes AS $gene) {
		$gene = str_replace("@","",$gene);
		$buf .= "$id pharmgkb:gene pharmgkb:$gene.".PHP_EOL;
	}
	
	if($a[4] != '') {
		$drugs = explode(";",$a[4]);
		foreach($drugs AS $drug) {
			$z = md5($drug);
			if(!isset($hash[$z])) $hash[$z] = $drug;
			$buf .= "$id pharmgkb:drug pharmgkb:$z.".PHP_EOL;
		}
	}
	if($a[5] != '') {
		$diseases = explode(";",$a[5]);
		foreach($diseases AS $disease) {
			$z = md5($disease);
			if(!isset($hash[$z])) $hash[$z] = $disease;
			$buf .= "$id pharmgkb:disease pharmgkb:$z.".PHP_EOL;
		}
	}
	if($a[6] != '') {
		$associations = explode(";",$a[6]);
		foreach($associations AS $association) {
			$z = md5($association);
			if(!isset($hash[$z])) $hash[$z] = $association;
			$buf .= "$id pharmgkb:association pharmgkb:$z.".PHP_EOL;
		}
	}
	
	if($a[7] != '') {
		$buf .= "$id pharmgkb:curated \"$a[7]\".".PHP_EOL;
	}
	
  }
  
  foreach($hash AS $h => $label) {
	$buf .= "pharmgkb:$h rdfs:label \"$label\".".PHP_EOL;
  }
  return $buf;  
}

?>
