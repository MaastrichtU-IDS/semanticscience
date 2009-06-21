<?php
$download = false;

// CTD: The Comparative Toxicogenomics Database
// http://ctd.mdibl.org/
// download URI: http://ctd.mdibl.org/reports/XXXX.tsv.gz
require('../include.php');

$indir = DATA.'ctd/';
$outdir = DATA.'ctd/n3/';
$infile_suffix = ".tsv.gz";
$outfile_suffix = ".n3.gz";
$files = array(
 "chemicals",  // uses MESH terms
 "chem_gene_ixns", // curated interactions
 "chem_disease_relations",
 "chem_pathways",  // 
 "diseases",   // uses MESH/OMIM
 "disease_pathways",
 "gene_disease_relations", 
 "gene_pathways" ,

);

if($download) {
 $host = 'http://ctd.mdibl.org/reports/';
 foreach($files AS $file) {
	$f = $host.'CTD_'.$file.$infile_suffix;
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
	if($fnx($infp,$outfp)) {
		trigger_error("Error in $fnx");
		exit;
	}
	echo "Converted to $outfile\n";
	
	gzclose($infp);
	gzclose($outfp);
}

/*
x ChemicalName
X CasRN
X ChemicalID (MeSH accession identifier)
*/
function CTD_chemicals($infp, $outfp)
{
	require ('../include.php');
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		list($name,$casrn,$mid) = explode("\t",trim($l));
		$name = addslashes($name);
		$buf .= "$mesh:$mid $dc:identifier \"$mesh:$mid\" .".PHP_EOL;
		$buf .= "$mesh:$mid $dc:title \"$name\" .".PHP_EOL;
		$buf .= "$mesh:$mid $rdfs:label \"$name [$mesh:$mid]\" .".PHP_EOL;  // [ns:id] title ?
		
		$buf .= "$mesh:$mid $rdfs:subClassOf $bio2rdfns:Chemical .".PHP_EOL;
		if($casrn) $buf .= "$mesh:$mid $rdfs:seeAlso $cas:$casrn .".PHP_EOL;
		
		$buf .= "$mesh:$mid $bio2rdf:in $ss:dataset/$ctd .".PHP_EOL;
		
	}
	gzwrite($outfp,$buf);
	return 0;
}


/* CURATED chemical-gene interactions
  ChemicalName
X ChemicalID (MeSH accession identifier)
  CasRN
  GeneSymbol
X GeneID (NCBI Gene or CTD accession identifier)
  Organism (scientific name)
X OrganismID (NCBI Taxonomy accession identifier)
x Interaction
X PubmedIDs ('|'-delimited list)
*/
function CTD_chem_gene_ixns($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$mid = $a[1];
		$gene_id = $a[4];
		$taxon_id = $a[6];
		$interaction_text = $a[7];
		$pubmed_ids = explode("|",$a[8]);
		
		$uri = "$ctd:$mid$gene_id";
		
		$buf .= "$uri $dc:identifier \"$ctd:$mid$gene_id\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"interaction between gene $gene_id and chemical $mid [$ctd:$mid$gene_id]\".".PHP_EOL;
		$buf .= "$uri $rdf:type $ctd:ChemicalGeneInteraction.".PHP_EOL;
		
		$buf .= "$uri $rdfs:comment \"$a[7]\".".PHP_EOL;
		$buf .= "$uri $bio2rdf:gene $ncbi_gene:$gene_id .".PHP_EOL;
		$buf .= "$uri $bio2rdf:chemical $mesh:$mid .".PHP_EOL;
		if($taxon_id) $buf .= "$uri $bio2rdf:organism $taxon:$taxon_id .".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "$uri $bio2rdf:article $pubmed:$pubmed_id .".PHP_EOL;
		//break;
		
		/*
		$buf .= "<$uri> <$rdf:type> <$ss:ChemicalGeneInteraction>.".PHP_EOL;
		$buf .= "<$uri> <$ss:hasAgent> <$gene:$gene_id>.".PHP_EOL;
		$buf .= "<$uri> <$ss:hasAgent> <$mesh:$cid>.".PHP_EOL;
		if($taxon_id) $buf .= "<$uri> <$ss:hasAgent> <$taxon:$taxon_id>.".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "<$uri> <$ss:hasReference> <$pubmed:$pubmed_id> .".PHP_EOL;
		*/
		//echo $buf;exit;
	}
	gzwrite($outfp,$buf);
	return 0;
}



/*
  ChemicalName
X ChemicalID (MeSH accession identifier)
  CasRN
  DiseaseName
X DiseaseID (MeSH or OMIM accession identifier)
x ChemicalDiseaseRelation
X OmimIDs ('|'-delimited list)
X PubmedIDs ('|'-delimited list)
*/
function CTD_chem_disease_relations($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$cid = $a[1];

		$mesh_id = substr($a[4],strpos($a[4], ":")+1); // MESH:D000544
		if($a[6]) $omim_ids = explode("|",strtolower($a[6]));
		$pubmed_ids = explode("|",$a[7]);
		
		$uri = "$ctd:$cid$mesh_id";
		
		$buf .= "$uri $dc:identifier \"$uri\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"interaction between chemical $cid and disease $mesh_id [$uri]\".".PHP_EOL;
		$buf .= "$uri a $ctd:ChemicalDiseaseInteraction .".PHP_EOL;
		$buf .= "$uri $bio2rdf:disease $mesh:$mesh_id .".PHP_EOL;
		if($omim_id)    foreach($omim_ids AS $omim_id)     $buf .= "$uri $bio2rdf:disease $omim:$omim_id .".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "$uri $bio2rdf:article $pubmed:$pubmed_id .".PHP_EOL;
		
		//break;
		/*
		$buf .= "<$uri> <$rdf:type> <$ss:ChemicalDiseaseInteraction>.".PHP_EOL;
		$buf .= "<$uri> <$rdfs:comment> \"evidence: $a[5]\".".PHP_EOL;
		$buf .= "<$uri> <$ss:hasParticipant> <$mesh:$cid>.".PHP_EOL;
		$buf .= "<$uri> <$ss:hasParticipant> <$mesh:$mesh_id>.".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "<$uri> <$ss:hasReference> <$pubmed:$pubmed_id> .".PHP_EOL;
		if($omim_ids)   foreach($omim_ids AS $omim_id)     $buf .= "<$uri> <$ss:hasTag> <$omim:$omim_id>.".PHP_EOL;
		*/
		//echo $buf;exit;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  ChemicalName
X ChemicalID (MeSH accession identifier)
  CasRN
  PathwayName
X PathwayID (KEGG accession identifier)
x ChemicalPathwayRelation
*/
function CTD_chem_pathways($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$mid = $a[1];
		$pathway_id = substr($a[4],strpos($a[4], ":")+1); // MESH:D000544
		
		$buf .= "$mesh:$mid $bio2rdf:pathway $kegg:$pathway_id .".PHP_EOL;
		
		// @TODO NEED axiom annotation
		$uri = "$ctd:$mid$pathway_id";
		$buf .= "$uri a $owl:Annotation .".PHP_EOL;
		$buf .= "$uri $dc:identifier \"$uri\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"$a[5] [$uri]\".".PHP_EOL;
		$buf .= "$uri $ss:hasSubject $mesh:$mid.".PHP_EOL;
		$buf .= "$uri $ss:hasPredicate $bio2rdf:pathway.".PHP_EOL;
		$buf .= "$uri $ss:hasObject $kegg:$pathway_id.".PHP_EOL;
	
		//break;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  DiseaseName
X DiseaseDB (MeSH or OMIM)
X DiseaseID (MeSH or OMIM accession identifier)
*/
function CTD_diseases($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$id = strtolower($a[1]).':'.$a[2];

		$buf .= "$id $rdfs:label \"$a[0] [$id]\" .".PHP_EOL;
		$buf .= "$id $rdfs:subClassOf $ctd:Disease .".PHP_EOL;
		
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
*/
function CTD_disease_pathways($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$id = explode(":",$a[1]);
		$disease_id = strtolower($id[0]).':'.$id[1];
		$pathway_id = strtolower($a[3]); // includes kegg: prefix

		$buf .= "$disease_id $bio2rdf:pathway $pathway_id .".PHP_EOL;
		
		// extra
		$buf .= "$disease_id $dc:identifer \"$disease_id\" .".PHP_EOL;
		$buf .= "$disease_id $rdfs:label \"$a[0] [$disease_id]\" .".PHP_EOL;
		$buf .= "$pathway_id $dc:identifer \"$pathway_id\" .".PHP_EOL;
		$buf .= "$pathway_id $rdfs:label \"$a[2] [$pathway_id]\" .".PHP_EOL;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}


/*
  GeneSymbol
X GeneID (NCBI Gene or CTD accession identifier)
  DiseaseName
X DiseaseID (MeSH or OMIM accession identifier)
x GeneDiseaseRelation
X OmimIDs ('|'-delimited list)
X PubmedIDs ('|'-delimited list)
*/
function CTD_gene_disease_relations($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$gene_id    = $a[1];
		$disease_id = explode(":",$a[3]);
		unset($mesh_id);unset ($omim_id);
		
		if(strstr($disease_id[0],"MESH")) $mesh_id = $disease_id[1];
		else if(strstr($disease_id[0],"OMIM")) $omim_id = $disease_id[1];
		if($a[5]) {
			$omim_ids = explode("|",$a[5]);
		}
		if(isset($omim_id) && $omim_ids) $omim_ids[] = $omim_id;

		$pubmed_ids = explode("|",$a[6]);
		
		$uri = "$ctd:$gene_id$disease_id[1]";
		$buf .= "$uri $rdf:type $ctd:GeneDiseaseInteraction .".PHP_EOL;
		$buf .= "$uri $dc:identifier \"$uri\".".PHP_EOL;
		$buf .= "$uri $rdfs:label \"Interaction between gene $gene_id and disease $disease_id[0]:$disease_id[1] [$uri]\".".PHP_EOL;
		if($mesh_id) $buf .= "$uri $bio2rdf:disease $mesh:$mesh_id .".PHP_EOL;
		if($omim_ids)   foreach($omim_ids AS $omim_id)    $buf .= "$uri $bio2rdf:disease $omim:$omim_id .".PHP_EOL;
		if($pubmed_ids) foreach($pubmed_ids AS $pubmed_id) $buf .= "$uri $bio2rdf:article $pubmed:$pubmed_id .".PHP_EOL;
		
			//echo $buf; exit;
		/*
		$buf .= "<$uri> <$rdf:type> <$ss:GeneDiseaseInteraction>.".PHP_EOL;
		$buf .= "<$uri> <$rdfs:comment> \"evidence: $a[4]\".".PHP_EOL;
		$buf .= "<$uri> <$ss:hasParticipant> <$gene:$gene_id>.".PHP_EOL;
		$buf .= "<$uri> <$ss:hasParticipant> <$mesh:$mesh_id>.".PHP_EOL;
		if(isset($omim_ids)) {
			foreach($omim_ids AS $omim_id) {
				$buf .= "<$uri> <$ss:hasParticipant> <$omim:$omim_id>.".PHP_EOL;
			}
		}
		foreach($pubmed_ids AS $pubmed_id) {
			$buf .= "<$uri> <$ss:hasReference> <$pubmed:$pubmed_id> .".PHP_EOL;
		}
		
	
		*/
	}
	
	gzwrite($outfp,$buf);
	return 0;
}

/*
  GeneSymbol
X GeneID (NCBI Gene or CTD accession identifier)
x PathwayName
X PathwayID (KEGG accession identifier)
*/
function CTD_gene_pathways($infp, $outfp)
{
	require("../include.php");
	$buf = N3NSHeader($nslist);
	
	gzgets($infp);
	while($l = gzgets($infp)) {
		$a = explode("\t",trim($l));
		$gene_id = $a[1];
		$kegg_id = strtolower($a[3]);

		$buf .= "$ncbi_gene:$gene_id $bio2rdf:pathway $kegg_id .".PHP_EOL;
		
		// extra
		$buf .= "$kegg_id $dc:identifer \"$kegg_id\" .".PHP_EOL;
		$buf .= "$kegg_id $rdfs:label \"$a[2] [$kegg_id]\" .".PHP_EOL;
		$buf .= "$ncbi_gene:$gene_id $dc:identifer \"$ncbi_gene:$gene_id\" .".PHP_EOL;
		$buf .= "$ncbi_gene:$gene_id $rdfs:label \"gene ".addslashes($a[0])." [$ncbi_gene:$gene_id]\" .".PHP_EOL;
	}
	
	gzwrite($outfp,$buf);
	return 0;
}


?>
