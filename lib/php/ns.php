<?php

$xsd = 'xsd';         $xsd_uri  = 'http://www.w3.org/2001/XMLSchema#';
$rdf = 'rdf';         $rdf_uri  = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
$rdfs = 'rdfs';       $rdfs_uri = 'http://www.w3.org/2000/01/rdf-schema#';
$owl = 'owl';         $owl_uri  = 'http://www.w3.org/2002/07/owl#';
$dc = 'dc';           $dc_uri   = 'http://purl.org/dc/elements/1.1/';
$ss = 'ss';           $ss_uri   = 'http://semanticscience.org/ontology/';
$bio2rdfns = 'bio2rdf_ns';  $bio2rdfns_uri   = 'http://bio2rdf.org/bio2rdf:';

/** BIO2RDF **/
$bio2rdf = 'bio2rdf';
$bm = $bio2rdf_uri = 'http://bio2rdf.org/';
$bind = 'bind';
$candida = 'candida';
$cas = 'cas'; 
$chebi = 'chebi';
$ctd = 'ctd';
$dip = 'dip';
$ddbj = 'ddbj';
$ec  = 'ec'; 
$embl = 'embl';
$evd = 'evd';
$euroscarf = 'euroscarf'; 
$kegg = 'kegg';
$germonline = 'germonline'; 
$go = 'go';
$gp = 'gp'; // ncbi genome projects
$iubmb = 'iubmb';
$intact = 'intact';
$irefindex = 'irefindex';
$mesh = 'mesh'; 
$metacyc = 'metacyc';
$mi = 'mi';
$mint = 'mint';
$ncbi_gene = 'geneid';
$ncbi   = 'ncbi';
$refseq = 'refseq';
$ncbi   = 'ncbi';
$omim   = 'omim';
$pir = 'pir';
$prf = 'prf';
$pdb    = 'pdb';
$pubmed = 'pubmed';
$pubchem = 'pubchem';
$sgd    = 'sgd';
$sp     = 'swissprot';
$taxon  = 'taxon';
$tigr = 'tigr';
$trembl = 'trembl';
$uniparc = 'uniparc';
$uniprot = 'uniprot';

$basenslist = array($xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $ss =>$ss_uri);

$nslist = array(
	$xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $ss =>$ss_uri, 
	$bind, $cas, $candida, $ctd, $ddbj,$dip, $ec, $embl, $evd, $euroscarf, $kegg, $germonline, $go, $gp, $iubmb, $intact,$irefindex,  $mesh, $metacyc,$mi,$mint,$ncbi_gene, $refseq, $ncbi, $omim, $pdb,$pir,$prf, $pubchem, $pubmed, $sgd, $sp, $taxon, $tigr, $trembl, $uniparc, $uniprot,"profilescan","superfamily","patternscan","blastprodom","fprintscan","gene3d","seg","hmmsmart","hmmpanther","hmmpfam","hmmpir","hmmtigr",
	$bio2rdf => $bio2rdf_uri, $bio2rdfns => $bio2rdfns_uri );
	

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
