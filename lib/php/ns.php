<?php

$xsd = 'xsd';         $xsd_uri  = 'http://www.w3.org/2001/XMLSchema#';
$rdf = 'rdf';         $rdf_uri  = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
$rdfs = 'rdfs';       $rdfs_uri = 'http://www.w3.org/2000/01/rdf-schema#';
$owl = 'owl';         $owl_uri  = 'http://www.w3.org/2002/07/owl#';
$dc = 'dc';           $dc_uri   = 'http://purl.org/dc/elements/1.1/';
$ss = 'ss';           $ss_uri   = 'http://semanticscience.org/resource/';
$bio2rdfns = 'bio2rdf_ns';  $bio2rdfns_uri   = 'http://bio2rdf.org/ns/bio2rdf:';

/** BIO2RDF **/
$afcs = 'afcs';
$bio2rdf = 'bio2rdf';
$bm = $bio2rdf_uri = 'http://bio2rdf.org/';
$bind = 'bind';
$biogrid = 'biogrid';
$candida = 'candida';
$cas = 'cas'; 
$chebi = 'chebi';
$ctd = 'ctd';
$dip = 'dip';
$ddbj = 'ddbj';
$ec  = 'ec'; 
$embl = 'embl';
$ensembl = 'ensembl';
$eco = 'eco';
$euroscarf = 'euroscarf'; 
$flybase = 'fb';
$kegg = 'kegg';
$germonline = 'germonline'; 
$go = 'go';
$gp = 'gp'; // ncbi genome projects
$grid = 'grid';
$iubmb = 'iubmb';
$intact = 'intact';
$irefindex = 'irefindex';
$mesh = 'mesh'; 
$metacyc = 'metacyc';
$mi = 'mi';
$mint = 'mint';
$mips = 'mips';
$entrez_gene = 'geneid';
$ncbi_gene = 'geneid';
$ncbi   = 'ncbi';
$refseq = 'refseq';
$ncbi   = 'ncbi';
$omim   = 'omim';
$ophid = 'ophid';
$pharmgkb = 'pharmgkb';
$pir = 'pir';
$prf = 'prf';
$pdb    = 'pdb';
$pubmed = 'pubmed';
$pubchem = 'pubchem';
$sgd    = 'sgd';
$sp     = 'swissprot';
$taxon  = 'taxon';
$tcdb = 'tcdb';
$tigr = 'tigr';
$tpg = 'tpg';
$trembl = 'trembl';
$uniparc = 'uniparc';
$uniprot = 'uniprot';

$basenslist = array($xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $ss =>$ss_uri);

$nslist = array(
	$xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $ss =>$ss_uri, 
	$afcs, $bind,$biogrid, $cas, $candida, $ctd, $ddbj,$dip, $ec, $embl, $ensembl, $eco, 
	$euroscarf, $flybase, $kegg, $germonline, $go, $gp, $grid, 
	$iubmb, $intact,$irefindex,  $mesh, $metacyc,$mi,$mint,$mips,
	$ncbi_gene, $refseq, $ncbi, $omim, $ophid, $pdb,$pharmgkb, $pir,$prf, $pubchem, $pubmed, 
	$sgd, $sp, $taxon, $tcdb, $tigr, $tpg, $trembl, $uniparc, $uniprot,
	"profilescan","superfamily","patternscan","blastprodom","fprintscan","gene3d","seg","hmmsmart","hmmpanther","hmmpfam","hmmpir","hmmtigr",
	$bio2rdf => $bio2rdf_uri, $bio2rdfns => $bio2rdfns_uri 
);


/*
bio2rdf predicates

molecule
gene
protein
chemical
disease
organism
pathway
article

url

interactsWith

*/

?>
