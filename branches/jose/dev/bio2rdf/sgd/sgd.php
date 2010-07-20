<?php
require_once(dirname(__FILE__).'/../../lib/php/utils.php');

$data = array(
 "dbxref"  => array("infile" => "chromosomal_features/dbxref.tab"),
 "domains" => array("infile" => "sequence_similarity/domains/domains.tab"),
 "protein" => array("infile" => "protein_info/protein_properties.tab"),
 "goa"     => array("infile" => "literature_curation/gene_association.sgd.gz"),
 "goslim"  => array("infile" => "literature_curation/go_slim_mapping.tab"),
 "complex" => array("infile" => "literature_curation/go_protein_complex_slim.tab"),
 "features" => array ("infile" => "chromosomal_features/SGD_features.tab"),
 "interaction" => array("infile" => "literature_curation/interaction_data.tab"),
 "phenotype"   => array("infile" => "literature_curation/phenotype_data.tab"),
 "pathways"  => array("infile" => "literature_curation/biochemical_pathways.tab"),
 "psiblast"    => array ("infile" => "sequence_similarity/psi_blast/psi_blast.tab.gz"),
// "expression" => array("infile" => "/systematic_results/expression_data/expression_connection_data/*"),
 );
$list = '[all|'.implode('|',array_keys($data)).']';

$options = array(
 "p" => $list,
 "tabdir" => "/opt/data/sgd/tab/",
 "n3dir" => "/opt/data/sgd/n3/",
 "dl" => "false",
 "ftp" => "http://downloads.yeastgenome.org/"
);

// show options
if($argc == 1) {
 echo "Usage: php $argv[0] ".PHP_EOL;
 echo " Default values as follows, * mandatory".PHP_EOL;
 foreach($options AS $key => $value) {
  if($key == "p") echo "*$key=$value";
  else echo " $key=$value ";
  echo PHP_EOL;
 }
}

// set options from user input
foreach($argv AS $i=> $arg) {
 if($i==0) continue;
 $b = explode("=",$arg);
 if(isset($options[$b[0]])) $options[$b[0]] = $b[1];
 else {echo "unknown key $b[0]";exit;}
}

if($options['p'] == $list) {
 exit;
}


//download
if($options['dl'] == "true") {
 $a = '';
 if($options['p'] == "all") $a = $data;
 else $a[$options['p']] = $data[$options['p']];

 HTTPDownload($options['ftp'], $a, $options['tabdir']);
}

if($options['p'] == 'all') $do = $data;
else if(isset($data[$options['p']])) $do[$options['p']] = $data[$options['p']];
else {echo "Invalid choice -> $list";exit;}

foreach($do AS $script => $args) {
   	echo "Running $script...";
	require($script.".php");
	BreakPath($args['infile'],$option['tabdir'],$file);

	$fnx = "SGD_".strtoupper($script);
	$n = new $fnx($options['tabdir'].$file,$options['n3dir'].$script.".n3");
	$n->Convert2RDF();
	unset($n);
	echo "done!\n";
}

?>
