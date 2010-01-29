<?php
$unique = '';
$n3 = '@prefix registry: <http://bio2rdf.org/registry:>
@prefix serv: <http://bio2rdf.org/serv:> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
';

$dir = "tab/";
$files = array(
	"go",
	"nar",
	"pathguide",
	"uniprot",
	"ncbi"
);

$replace_rules = array(
 "fb" => "flybase",
 "wb" => "wormbase",
 "wb_ref" => "wormbase",
 "wp" => "wormbase",
 
 "agricola_id" => "agricola",
 "agricola_ind" => "agricola",
 "subtilistg" => "subtilist",
 "ugb" => "ucsc",
 "hs" => "hedgehog",
 "hmid" => "hivmid",
 "ig" => "img",
 "img_m" => "img",
 "imgt_ligm" => "imgt",
 "img_genomes" => "img",
 "imgt_genedb" => "imgt",
 "imgtgenedb" => "imgt",
 "merops_fam" => "merops",
 
 "rmd" => "rnamods",
 "mdb" => "msd",
 "mc" => "cygd",
 "pds" => "pathcase",
 "pathway_interaction_db" => "pid",
 "apidb_plasmodb" => "plasmodb",
 "hr" => "hdr",
 "phossite" => "xpd",
 "agi_locuscode" => "tair",
 "aspgd_locus" => "aspgd",
 "aspgd_ref" => "aspgd",
 "cgd_locus" => "cgd",
 "cgd_ref" => "cgd",
 "tgd_locus" => "tgd",
 "tgd_ref" => "tgd",
 "hinvdb_locus" => "hinvdb",
 "hinvdb_ref" => "hinvdb",
 "sgd_locus" => "sgd",
 "sgd_ref" => "sgd",
 "ecocyc_ref" => "ecocyc",
 
 "ag" => "aspgd",
 "biomd" => "biomodels",
 "ensd" => "embl",
 "g&eacute;noplanteinfo" =>  "genoplanteinfo",
 "goa_ref" => "goa",
 "go_ref" => "goa",
 "goc" => "goa",
 
 "ind" => "ec",
 "en" => "ec",
 "nciubmb" => "ec",
 "i" => "integr8",
 "eck" => "ecogene",
 "ecogene_g" => "ecogene",
 "ergolight" => "ergo",
 "fantom_db" => "fantom",
 "hgnc_gene" => "hgnc",
 "gramene" => "gr",
 "ma" => "mgi", 
 "mgd" => "mgi",
 "mips_resources" => "mips",
 
 "2dpage" => "rh2dpage",
 "ratheart2dpage" => "rh2dpage",
 
 "ntb" => "taxon",
 "pharmgkb_pa" => "pharmgkb",
 "pharmgkb_pgkb" => "pharmgkb",
 "hpa_antibody" => "hpa",
 "cep" => "wormpep",
 "pfamb" => "pfam",
 "sgn_ref" => "sgn",
 "usgmp" => "afcs",
 "tc" => "tcdb",
 "tgfd" => "tgdb",
  
 
 "swissprot" => "uniprot",
 "trembl" => "uniprot",
 "uniprotkb_swissprot" => "uniprot",
 "uniprotkb_trembl" => "uniprot",
 "uniprotkb" => "uniprot",
);

$aggregation_rules = array(
 "emage" => "ema",
);


/*
0. db id 
1. database name
2. database abbreviation
3. description 
4. contact 
5. URL
*/
$buf = '';
foreach($files AS $file) {
 $fp = fopen($dir.$file.".output.tab","r");
 while($l = fgets($fp)) {
  $a = explode("\t",trim($l));
  if($a[1] == "") continue;
  if($file == "nar") $a[2] = $a[1];
  
  // unique namespace identifier algorithm
  $b = explode(" - ",trim($a[2]));
  $b = explode(": ",$b[0]);
  $b = $original_ns = $b[0];
  $b = preg_replace("/(\(.+\))/","",$b);  // ( *** )
  $b = preg_replace("/(\<[a-zA-Z]+\>)/","",$b);  // <**>
  $b = preg_replace("/(\<\/[a-zA-Z]+\>)/","",$b);   // </**> 
  $b = str_replace(array('/','-','.',':',',','®',' | ',"'",'@','&eacute;','~'), 
                   array('_','', '', '_','', '', '',   '', '', 'e',       '' ),
				   $b);
  $c = explode(" ",strtolower($b));
  $id = $c[0];
  if(count($c) == 2) { // if two fragments, then merge with underscore
	$id = $c[0]."_".$c[1];
  } elseif(count($c) > 2) { // if three or more, then pick the first letter from each word
	  $e = '';
	  foreach($c AS $d) {
		$e .= substr($d,0,1);
	  }
	  $id = $e;
  }
   
  // see if we replace with something else
  if(isset($replace_rules[$id])) $id = $replace_rules[$id];

  // aggregate
  if(FALSE !== ($pos = strpos($id,"_"))) {
    $agg = substr($id,0,$pos);
	$aggregator[$agg][] = $id;
  }
  
  // end algorithm
  $line = "$file\t$id\t$a[2]\t$a[1]\t$a[3]\t$a[4]\t$a[5]\n";
  
  $unique[$id][] = array(
	'file' => $file,
	'id' => $id,
	'line' => $line
  );
  
   
  $n3 .= "registry:dataset/registry/$id a serv:Dataset .".PHP_EOL;
  $n3 .= "registry:dataset/registry/$id rdfs:label \"Registry Dataset: $id [registry:dataset/registry/$id]\" .".PHP_EOL;
  $n3 .= "registry:dataset/registry/$id dc:identifier \"registry:dataset/registry/$id\" .".PHP_EOL;
  $n3 .= "registry:dataset/registry/$id owl:sameAs registry:dataset/$file/$id .".PHP_EOL;
  $n3 .= "registry:dataset/registry/$id serv:source registry:agent/bio2rdf .".PHP_EOL; 
  $n3 .= "registry:dataset/registry/$id serv:namespace registry:ns/registry/$id .".PHP_EOL;
  $n3 .= "registry:ns/registry/$id serv:dataset registry:dataset/registry/$id .".PHP_EOL;
  
  
  $n3 .= "registry:ns/registry/$id a serv:Namespace .".PHP_EOL; 
  $n3 .= "registry:ns/registry/$id rdfs:label \"Registry Namespace: $id [registry:ns/registry/$id]\" .".PHP_EOL;
  $n3 .= "registry:ns/registry/$id dc:identifier \"registry:ns/registry/$id\" .".PHP_EOL;
  $n3 .= "registry:ns/registry/$id serv:value \"$id\" .".PHP_EOL;
  $n3 .= "registry:ns/registry/$id serv:source registry:agent/bio2rdf .".PHP_EOL; 
  $n3 .= "registry:ns/registry/$id dc:replaces registry:ns/$file/$id .".PHP_EOL;
    
  $n3 .= "registry:ns/$file/$id a serv:Namespace .".PHP_EOL;   
  $n3 .= "registry:ns/$file/$id rdfs:label \"Original namespace $original_ns from ".strtoupper($file)." automatically mapped to $id\".".PHP_EOL;
  $n3 .= "registry:ns/$file/$id dc:identifier \"registry:ns/$file/$id\" .".PHP_EOL;
  $n3 .= "registry:ns/$file/$id serv:source registry:agent/$file .".PHP_EOL; 
  $n3 .= "registry:ns/$file/$id serv:dataset registry:dataset/$file/$id .".PHP_EOL;
  $n3 .= "registry:dataset/$file/$id serv:namespace registry:ns/$file/$id .".PHP_EOL;
  $n3 .= "registry:dataset/$file/$id a serv:Dataset .".PHP_EOL;
  $n3 .= "registry:dataset/$file/$id serv:source registry:agent/$file .".PHP_EOL;   
  
  $buf .= $line;
 }
 fclose($fp);
}
file_put_contents("merged.tab",$buf);


// generate the aggregation
$buf = "agg_id\tid\n"; 
foreach($aggregator AS $agg_id => $a) {
	if(count($a) >= 2) {
		$buf .= $agg_id;
		$n3 .= "registry:ns/registry/$agg_id a serv:Namespace .".PHP_EOL;
		$n3 .= "registry:ns/registry/$agg_id dc:identifier \"registry:ns/registry/$agg_id\" .".PHP_EOL;
		$n3 .= "registry:ns/registry/$agg_id rdfs:label \"Registry aggregation namespace - $agg_id [registry:ns/registry/$agg_id]\"  .".PHP_EOL;
		foreach($a AS $b) {
			$n3 .= "registry:ns/registry/$agg_id skos:narrower registry:ns/registry/$b .".PHP_EOL;
			$buf .= "\t$b";
		}
		$buf .= "\n";
	}
}
file_put_contents("aggregator.tab",$buf);



// initialize the stats
foreach($files AS $i => $id) {
	$stats[$id]['total'] = 0;
	$s = 'sharedWith_'.$i;
	$stats[$id][$s] = 0;
}

$buf = '';
foreach($unique AS $id => $a) {
  $e = $a[0];
  $buf .= "$id\t".$e['line'];
   
  $n = count($a); // number of files that contain this entry
  foreach($a AS $e) {
	$id = $e['file'];
	$stats[$id]['total'] += 1;
	
	$s = 'sharedWith_'.($n-1);
	$stats[$id][$s] += 1;	
  }
}
file_put_contents("unique.tab",$buf);

$buf = "file\ttotal\tunique\tcommon\n";
foreach($stats AS $file => $e) {
  $buf .= "$file\t".$e['total'];
  foreach($files AS $i => $f) {
	$s = 'sharedWith_'.$i;
	$buf .= "\t".$stats[$file][$s];
   }
  $buf .= "\n";
}
file_put_contents("stats.tab",$buf);
file_put_contents("registry.n3",$n3);

?>