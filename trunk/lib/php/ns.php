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

$candida = 'candida';
$cas = 'cas'; 
$chebi = 'chebi';
$ctd = 'ctd';
$dip = 'dip';
$ec  = 'ec'; 
$evd = 'evd';
$euroscarf = 'euroscarf'; 
$kegg = 'kegg';
$germonline = 'germonline'; 
$go = 'go';
$gp = 'gp'; // ncbi genome projects
$iubmb = 'iubmb';
$irefindex = 'irefindex';
$mesh = 'mesh'; 
$metacyc = 'metacyc';
$ncbi_gene = 'gene';
$ncbi_ref  = 'refseq';
$ncbi_acc  = 'ncbi_accession';
$ncbi_gi   = 'ncbi_gi';
$ncbi   = 'ncbi';
$omim   = 'omim';
$pubmed = 'pubmed';
$pubchem = 'pubchem';
$sgd    = 'sgd';
$sp     = 'swissprot';
$taxon  = 'taxon';
$trembl = 'trembl';
$uniparc = 'uniparc';

$nslist = array(
	$xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $ss =>$ss_uri, 
	$cas, $candida, $ctd, $dip, $ec, $evd, $euroscarf, $kegg, $germonline, $go, $gp, $iubmb,  $mesh, $metacyc, $ncbi_gene, $ncbi_ref, $ncbi_acc, $ncbi_gi, $ncbi, $omim, $pubchem, $pubmed, $sgd, $sp, $taxon, $trembl, $uniparc, "profilescan","superfamily","patternscan","blastprodom","fprintscan","gene3d","seg","hmmsmart","hmmpanther","hmmpfam","hmmpir","hmmtigr",
	$bio2rdf => $bio2rdf_uri, $bio2rdfns => $bio2rdfns_uri );
	

/*
bio2rdf predicates

sequence
gene
protein
chemical
disease
organism
pathway
article

url
*/

?>