<?php

$xsd = 'xsd';         $xsd_uri  = 'http://www.w3.org/2001/XMLSchema#';
$rdf = 'rdf';         $rdf_uri  = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
$rdfs = 'rdfs';       $rdfs_uri = 'http://www.w3.org/2000/01/rdf-schema#';
$owl = 'owl';         $owl_uri  = 'http://www.w3.org/2002/07/owl#';
/* $dc = 'dc';           $dc_uri   = 'http://purl.org/dc/elements/1.1/'; */
$dc = 'dc';           $dc_uri   = 'http://purl.org/dc/terms/';
$skos = 'skos';       $skos_uri = 'http://www.w3.org/2004/02/skos/core#';
$foaf = 'foaf';       $foaf_uri = 'http://xmlns.com/foaf/0.1/';
$ss = 'ss';           $ss_uri   = 'http://semanticscience.org/resource/';
$bio2rdfns = 'bio2rdf_resource';  $bio2rdfns_uri   = 'http://bio2rdf.org/bio2rdf_resource:';

/** BIO2RDF **/
$afcs = 'afcs';
$apo = 'apo';
$bio2rdf = 'bio2rdf';
$bm = $bio2rdf_uri = 'http://bio2rdf.org/';
$bind = 'bind';
$biogrid = 'biogrid';
$candida = 'candida';
$cas = 'cas'; 
$chebi = 'chebi';
$ctd = 'ctd';
$dbsnp = 'dbsnp';
$dip = 'dip';
$ddbj = 'ddbj';
$drugbank = 'drugbank';
$ec  = 'ec'; 
$embl = 'embl';
$ensembl = 'ensembl';
$eco = 'eco';
$euroscarf = 'euroscarf'; 
$flybase = 'flybase';
$kegg = 'kegg';
$germonline = 'germonline'; 
$go = 'go';
$gp = 'gp'; // ncbi genome projects
$grid = 'grid';
$iubmb = 'iubmb';
$intact = 'intact';
$ipi = 'ipi';
$irefindex = 'irefindex';
$mesh = 'mesh'; 
$metacyc = 'metacyc';
$mi = 'mi';
$mint = 'mint';
$mips = 'mips';
$entrez_gene = 'entrez_gene';
$ncbi_gene = 'entrez_gene';
$ncbi   = 'ncbi';
$refseq = 'refseq';
$ncbi   = 'ncbi';
$omim   = 'omim';
$ophid = 'ophid';
$pato = 'pato';
$pharmgkb = 'pharmgkb';
$pir = 'pir';
$prf = 'prf';
$pdb    = 'pdb';
$pubmed = 'pubmed';
$pubchem = 'pubchem';
$sgd    = 'sgd';
$sgd_resource = 'sgd_resource';
$so = 'so';
$sp     = 'swissprot';
$taxon  = 'taxon';
$tcdb = 'tcdb';
$tigr = 'tigr';
$tpg = 'tpg';
$trembl = 'trembl';
$uniparc = 'uniparc';
$uniprot = 'uniprot';
$uo = 'uo';
$registry = 'registry';
$registry_dataset = 'registry_dataset';
$serv = 'serv';

$basenslist = array($xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $skos => $skos_uri,$foaf => $foaf_uri, $ss =>$ss_uri);

$nslist = array(
	$xsd => $xsd_uri, $rdf => $rdf_uri, $rdfs => $rdfs_uri, $owl => $owl_uri, $dc => $dc_uri, $skos => $skos_uri, $foaf=>$foaf_uri, $ss =>$ss_uri,  
	$afcs, $apo, $bind,$biogrid, $cas, $candida, $ctd,$dbsnp, $ddbj,$dip,$drugbank, $ec, $embl, $ensembl, $eco, 
	$euroscarf, $flybase, $kegg, $germonline, $go, $gp, $grid, 
	$ipi, $iubmb, $intact,$irefindex,  $mesh, $metacyc,$mi,$mint,$mips,
	$ncbi_gene, $refseq, $ncbi, $omim, $ophid, $pato, $pdb,$pharmgkb, $pir,$prf, $pubchem, $pubmed, 
	$so, $sgd, $sgd_resource, $sp, $taxon, $tcdb, $tigr, $tpg, $trembl, $uniparc, $uniprot,
	"profilescan","superfamily","patternscan","blastprodom","fprintscan","gene3d","seg","hmmsmart","hmmpanther","hmmpfam","hmmpir","hmmtigr",
	$bio2rdf => $bio2rdf_uri, $bio2rdfns => $bio2rdfns_uri, $serv, $uo, $registry, $registry_dataset
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
