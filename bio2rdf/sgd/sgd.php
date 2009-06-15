<?php
define('DEBUG','DEBUG');
$download = true;
$ldir = '/data/sgd/';
$n3dir = '/data/sgd/n3/';
$host = 'http://downloads.yeastgenome.org/';


$files = array(
/*
 "SGD_Domains" => array ("infile" => "sequence_similarity/domains/domains.tab","outfile" => "$n3dir/sgd_domains.n3","script" => "domains.php"),
 "SGD_BestHits" => array ("infile" => "sequence_similarity/best_hits/best_hits.tab","outfile" => "$n3dir/sgd_best_hits.n3","script" => "best_hits.php"),

 "SGD_ProteinInfo" => array ("infile" => "protein_info/protein_properties.tab","outfile" => "$n3dir/sgd_protein_properties.n3","script" => "protein_info.php"),
 "SGD_GeneAssociation" => array ("infile" => "literature_curation/gene_association.sgd.gz","outfile" => "$n3dir/sgd_gene_association.n3","script" => "gene_association.php"), 
 "SGD_GOSLIMMapping" => array ("infile" => "literature_curation/go_slim_mapping.tab","outfile" => "$n3dir/sgd_go_slim_mapping.n3","script" => "go_slim_mapping.php"),
 "SGD_GOProteinComplex" => array ("infile" => "literature_curation/go_protein_complex_slim.tab","outfile" => "$n3dir/sgd_go_protein_complex.n3","script" => "go_protein_complex.php"),
 "SGD_ChromosomalFeatures" => array ("infile" => "chromosomal_features/SGD_features.tab","outfile" => "$n3dir/sgd_chromosomal_features.n3","script" => "chromosomal_features.php"),
 "SGD_DBXREF" => array ("infile" => "chromosomal_features/dbxref.tab","outfile" => "$n3dir/sgd_dbxref.n3","script" => "dbxref.php"),
 */
 "SGD_interaction_data" => array ("infile" => "literature_curation/interaction_data.tab","outfile" => "$n3dir/sgd_interactions.n3","script" => "interaction.php"),
 "SGD_Phenotype" => array ("infile" => "literature_curation/phenotype_data.tab","outfile" => "$n3dir/sgd_phenotype_data.n3","script" => "phenotype.php"),
//"SGD_PSIBLAST_Hits" => array ("infile" => "sequence_similarity/psi_blast/psi_blast.tab.gz","outfile" => "$n3dir/sgd_psi_blast.n3","script" => "psiblast_hits.php"),
//"SGD_Expression" => array("infile" => "/systematic_results/expression_data/expression_connection_data/*","outfile"=>"$n3dir/expression/*.n3", "script" => "expression.php")
 );

require_once('../lib/utils.php');
//download
if($download) {
HTTPDownload($host, $files, $ldir);
exit;
} // download

foreach($files AS $fnx => $args) {
    echo "Running $fnx..";
	require($args['script']);
	BreakPath($args['infile'],$dir,$file);
	$n3 = $n3dir.substr($file,0,strpos($file,'.')).'.n3';

	$n = new $fnx($ldir.$file,$n3);
	$n->Convert2RDF();
	unset($n);
	echo "done!\n";
exit;
}

?>
