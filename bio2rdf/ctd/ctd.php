<?php
// Parser for:
// CTD: The Comparative Toxicogenomics Database
// http://ctd.mdibl.org/
// download URI: http://ctd.mdibl.org/reports/XXXX.tsv.gz

/** Show/Set command line parameters **/
$options = array(
 "download" => "false",
 "dataset" => "*|chemicals|chem_gene_ixns|chem_disease_relations|chem_pathways|diseases|disease_pathways|gene_disease_relations|gene_pathways"
);
// show options
if($argc == 1) {echo "Usage: php $argv[0] ".PHP_EOL;foreach($options AS $key => $value) { echo " $key=$value ". PHP_EOL;}}
// set options from user input
foreach($argv AS $i=> $arg) {if($i==0) continue;$b = explode("=",$arg);if(isset($options[$b[0]])) $options[$b[0]] = $b[1];else {echo "unknown key $b[0]";exit;}}



require (dirname(__FILE__).'/../include.php');
$downloadsite = 'http://ctd.mdibl.org/reports/';
$indir = DATA.'ctd/';
$outdir = DATA.'ctd/n3/';
$infile_suffix = ".tsv.gz";
$outfile_suffix = ".n3.gz";
$allfiles = array(
 "chemicals",  // uses MESH terms
 "chem_disease_relations",
// "chem_gene_ixn_types", // curated interactions
 "chem_gene_ixns", // curated interactions
 "chem_pathways",  // 
 "diseases",   // uses MESH/OMIM
 "disease_pathways",
 "gene_disease_relations", 
 "gene_pathways",
// "genes"
);

if($options['dataset'][0] == '*') {
	$files = $allfiles;
} else {
	$files = explode("|",$options['dataset']);
}

if($options['download'] == 'true') {
 foreach($files AS $file) {
	$f = $downloadsite.'CTD_'.$file.$infile_suffix;
	$l = $indir.$file.$infile_suffix;
	echo "Downloading $f to $l\n";
	copy($f, $l);
 }
}


foreach($files AS $base) {
	$infile = $indir.$base.$infile_suffix;
	$outfile = $outdir.$base.$outfile_suffix;
	
	echo "Processing $infile ...";
	
	$infp = gzopen($infile,"r");
	if(!$infp) {trigger_error("Unable to open $infile");exit;}
	$outfp = gzopen($outfile,"w");
	if(!$outfp) {trigger_error("Unable to open $outfile");exit;}
	
	
	$fnx = "CTD_".$base;
	if(isset($fnx)) {
		if($fnx($infp,$outfp)) {
		 	trigger_error("Error in $fnx");
			 exit;
                }
	}
	echo "Converted to $outfile\n";
	
	gzclose($infp);
	gzclose($outfp);
}





/*
Fields:
0 ChemicalName
1 ChemicalID (MeSH accession identifier)
2 CasRN
3 ParentIDs (accession identifiers of the parent terms; '|'-delimited list)
4 ChemicalTreeNumbers (unique identifiers of the chemical's nodes; '|'-delimited list)
5 ParentTreeNumbers (unique identifiers of the parent nodes; '|'-delimited list)
6 Synonyms ('|'-delimited list)
*/
function CTD_chemicals($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);

	gzgets($infp);
	while($l = gzgets($infp)) {
		list($name,$mid,$casrn) = explode("\t",trim($l));
		$m=explode(":",$mid);
		$mid = $m[1];
		$name = addslashes($name);

		$buf .= "$mesh:$mid $dc:identifier \"$mesh:$mid\" .".PHP_EOL;
		$buf .= "$mesh:$mid $dc:title \"$name\" .".PHP_EOL;
		$buf .= "$mesh:$mid $rdfs:label \"$name [$mesh:$mid]\" .".PHP_EOL;  // [ns:id] title ?
		
		$buf .= "$mesh:$mid a $ctd_resource:Chemical .".PHP_EOL;
		if($casrn) $buf .= "$mesh:$mid $owl:equivalentClass $cas:$casrn .".PHP_EOL;
		
		$buf .= "$mesh:$mid $ctd_resource:in $ss:dataset/$ctd .".PHP_EOL;
	}
	gzwrite($outfp,$buf);
	return 0;
}


/* CURATED chemical-gene interactions
  0 ChemicalName
X 1 ChemicalID (MeSH accession identifier)
  2 CasRN
  3 GeneSymbol
X 4 GeneID (NCBI Gene or CTD accession identifier)
  5 Organism (scientific name)
X 6 OrganismID (NCBI Taxonomy accession identifier)
x 7 Interaction
  8 InteractionActions ('|'-delimited list)
X 9 PubmedIDs ('|'-delimited list) */ 

function CTD_chem_gene_ixns($infp, $outfp) {
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));

		$mid = $a[1];
		$gene_id = $a[4];
		$taxon_id = $a[6];
		$interaction_text = $a[7];
		$interaction_action = $a[8];
		$pubmed_ids = explode("|",$a[9]);
		foreach($pubmed_ids AS $i=> $pmid) {
			if(!is_int($pmid)) unset($pubmed_ids[$i]);
		}
		
		$uri  = "$ctd_resource:$mid$gene_id";  // should taxon be part of the ID?
		
		$buf .= "$uri $dc:identifier \"ctd_resource:$mid$gene_id\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"interaction between $a[3] (geneid:$gene_id) and $a[0] (mesh:$mid) [$ctd:$mid$gene_id]\".".PHP_EOL;
		$buf .= "$uri $rdf:type $ctd_resource:ChemicalGeneInteraction.".PHP_EOL;
		
		$buf .= "$uri $rdfs:comment \"$a[7]\".".PHP_EOL;
		$buf .= "$uri $ctd_resource:gene $ncbi_gene:$gene_id .".PHP_EOL;
		$buf .= "$uri $ctd_resource:chemical $mesh:$mid .".PHP_EOL;
		if($taxon_id) $buf .= "$uri $ctd_resource:organism $taxon:$taxon_id .".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "$uri $ctd_resource:article $pubmed:$pubmed_id .".PHP_EOL;
		if($interaction_action) $buf .= "$uri $ctd_resource:action \"$interaction_action\" .".PHP_EOL;
		//break;
	
//		echo $buf;exit;
	}
	gzwrite($outfp,$buf);
	return 0;
}



/*
X 0 ChemicalName
X 1 ChemicalID (MeSH accession identifier)
  2 CasRN
X 3 DiseaseName
X 4 DiseaseID (MeSH or OMIM accession identifier)
  5 DirectEvidence
  6 InferenceGeneSymbol
x 7 InferenceScore
X 8 OmimIDs ('|'-delimited list)
X 9 PubmedIDs ('|'-delimited list)
*/
function CTD_chem_disease_relations($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);

	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$chemical_name = $a[0];
		$chemical_id = $a[1];
		$disease_name = $a[3];
		$disease = explode(":",$a[4]);
		$disease_ns = strtolower($disease[0]);
		$disease_id = $disease[1];
				
		$uid = "$chemical_id$disease_id";
		$uri = "$ctd_resource:$uid";
		
		$buf .= "$uri $dc:identifier \"ctd_resource:$uid\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"interaction between $chemical_name ($chemical_id) and disease $disease_name ($disease_ns:$disease_id) [$uri]\".".PHP_EOL;
		$buf .= "$uri a $ctd_resource:ChemicalDiseaseInteraction .".PHP_EOL;
		$buf .= "$uri $ctd_resource:chemical $mesh:$chemical_id .".PHP_EOL;
		$buf .= "$uri $ctd_resource:disease $disease_ns:$disease_id .".PHP_EOL;
		if($a[8])  {
			$omim_ids = explode("|",strtolower($a[8]));
			foreach($omim_ids AS $omim_id)     $buf .= "$uri $ctd_resource:disease $omim:$omim_id .".PHP_EOL;
		}
		if(isset($a[9])) {
			$pubmed_ids = explode("|",$a[9]);
			foreach($pubmed_ids AS $pubmed_id) {
				if($pubmed_id) $buf .= "$uri $ctd_resource:article $pubmed:$pubmed_id .".PHP_EOL;
			}
		}
		
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  0 ChemicalName
X 1 ChemicalID (MeSH accession identifier)
  2 CasRN
  3 PathwayName
X 4 PathwayID (KEGG accession identifier)
x 5 InferenceGeneSymbol
*/
function CTD_chem_pathways($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$chemical_id = $a[1];
		ParseQNAME($a[4],$pathway_ns,$pathway_id);
		if($pathway_ns == "react") $pathway_ns = "reactome";
		
		$buf .= "$mesh:$chemical_id $ctd_resource:pathway $pathway_ns:$pathway_id .".PHP_EOL;		
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  0 DiseaseName
X 1 DiseaseID (MeSH or OMIM accession identifier)
  2 AltDiseaseIDs
  3 ParentIDs
  4 DiseaseTreeNumbers
  5 ParentTreeNumbers
  6 Synonyms
*/
function CTD_diseases($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		ParseQNAME($a[1],$disease_ns,$disease_id);

		$uid = "$disease_ns:$disease_id";
		$buf .= "$uid $rdfs:label \"$a[0] [$uid]\" .".PHP_EOL;
		$buf .= "$uid a $ctd_resource:Disease .".PHP_EOL;
		
		//echo $buf;exit;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}


/*
  DiseaseName
X DiseaseID (MeSH or OMIM accession identifier)
  PathwayName
X PathwayID (KEGG accession identifier)
  InferenceGeneSymbol
*/
function CTD_disease_pathways($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		ParseQNAME($a[1],$disease_ns,$disease_id);
		ParseQNAME($a[3],$pathway_ns,$pathway_id);
		if($pathway_ns == 'react') $pathway_ns = 'reactome';

		$buf .= "$disease_ns:$disease_id $ctd_resource:pathway $pathway_ns:$pathway_id .".PHP_EOL;
		
		// extra
		$buf .= "$disease_ns:$disease_id $dc:identifer \"$disease_ns:$disease_id\" .".PHP_EOL;
		$buf .= "$disease_ns:$disease_id $rdfs:label \"$a[0] [$disease_ns:$disease_id]\" .".PHP_EOL;
		$buf .= "$pathway_ns:$pathway_id $dc:identifer \"$pathway_ns:$pathway_id\" .".PHP_EOL;
		$buf .= "$pathway_ns:$pathway_id $rdfs:label \"$a[2] [$pathway_ns:$pathway_id]\" .".PHP_EOL;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}


/*
  0 GeneSymbol
X 1 GeneID (NCBI Gene or CTD accession identifier)
  2 DiseaseName
X 3 DiseaseID (MeSH or OMIM accession identifier)
  4 DirectEvidence
  5 InferenceChemicalName
  6 InferenceScore
X 7 OmimIDs ('|'-delimited list)
X 8 PubmedIDs ('|'-delimited list)
*/
function CTD_gene_disease_relations($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$gene_name = $a[0];
		$gene_ns = 'geneid';
		$gene_id = $a[1];
		$disease_name = $a[2];
		ParseQNAME($a[3],$disease_ns,$disease_id);
		
		$uri = "$ctd_resource:$gene_id$disease_id";
		
		$buf .= "$uri $rdf:type $ctd_resource:GeneDiseaseInteraction .".PHP_EOL;
		$buf .= "$uri $dc:identifier \"$uri\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"Gene Disease interaction between $gene_name ($gene_ns:$gene_id) and $disease_name ($disease_ns:$disease_id) [$uri]\".".PHP_EOL;
		$buf .= "$uri $ctd_resource:gene $gene_ns:$gene_id .".PHP_EOL;
		$buf .= "$uri $ctd_resource:disease $disease_ns:$disease_id .".PHP_EOL;
		if($a[7]) {
			$omim_ids = explode("|",$a[7]);			
			foreach($omim_ids AS $omim_id)    $buf .= "$uri $ctd_resource:disease $omim:$omim_id .".PHP_EOL;
		}
		if(isset($a[8])) {
			$pubmed_ids = explode("|",$a[8]);
			foreach($pubmed_ids AS $pubmed_id) {
				if(!is_numeric($pubmed_id)) continue;
				$buf .= "$uri $ctd_resource:article $pubmed:$pubmed_id .".PHP_EOL;
			}
		}
		
		//echo $buf; exit;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  0 GeneSymbol
X 1 GeneID (NCBI Gene or CTD accession identifier)
x 2 PathwayName
X 3 PathwayID (KEGG accession identifier)
*/
function CTD_gene_pathways($infp, $outfp)
{
	require (dirname(__FILE__).'/../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$gene_ns = $ncbi_gene;
		$gene_id = $a[1];
		ParseQNAME($a[3],$pathway_ns,$pathway_id);
		$kegg_id = strtolower($a[3]);
		if($pathway_ns == "react") $pathway_ns = "reactome";

		$buf .= "$gene_ns:$gene_id $ctd_resource:pathway $pathway_ns:$pathway_id .".PHP_EOL;
		
		// extra
		$buf .= "$pathway_ns:$pathway_id $dc:identifer \"$pathway_ns:$pathway_id\" .".PHP_EOL;
		$buf .= "$pathway_ns:$pathway_id $rdfs:label \"$a[2] [$pathway_ns:$pathway_id]\" .".PHP_EOL;
		$buf .= "$gene_ns:$gene_id $dc:identifer \"$gene_ns:$gene_id\" .".PHP_EOL;
		$buf .= "$gene_ns:$gene_id $rdfs:label \"gene ".addslashes($a[0])." [$gene_ns:$gene_id]\" .".PHP_EOL;

//echo $buf;exit;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}


function ParseQNAME($string,&$ns,&$id)
{
	$a = explode(":",$string);
	if(count($a) == 1) {
		$id = $string;
	} else {
		$ns = strtolower($a[0]);
		$id = $a[1];
	}
	return true;
}

?>
