<?php

/*
http://virtuoso.openlinksw.com/dataspace/dav/wiki/Main/VirtFacetBrowserInstallConfig
*/
$isql = "/opt/virtuoso/default/bin/isql";
if(defined(PHP_WINDOWS_VERSION_MAJOR)) $isql = "isql";

$options = array(
 "file" => "filename",
 "graph" => "graphname",
 "port" => "1111",
 "user" => "dba",
 "pass" => "dba",
 "flags" => "16",
 "threads" => "2",
 "updatefacet" => "false",
 "deletegraph" => "false",
 "deleteonly" => "false",
 "initialize" => "false",
 "setns" => "false",
 "format" => "n3"
);


// show options
if($argc == 1) {
 echo "Usage: php $argv[0] ".PHP_EOL;
 echo " Default values as follows, * mandatory".PHP_EOL;
 foreach($options AS $key => $value) {
  echo " $key=$value ";
  if($key == "file" || $key == "graph") echo "*";
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


// check for valid graph
if($options['graph'] == 'graphname') {
 echo "Please specify a *real* graph with the graph=graphname option".PHP_EOL;
 exit;
}

$cmd_pre = "$isql -S ".$options['port']." -U ".$options['user']." -P ".$options['pass']." verbose=on banner=off prompt=off echo=ON errors=stdout exec=".'"'; $cmd_post = '"';


// associate a prefix with namespace
// http://docs.openlinksw.com/virtuoso/fn_xml_set_ns_decl.html
if($options['setns'] == 'true') {
 echo "Setting namespaces for facet browser\n";

 include('ns.php');
 $cmd = '';
 foreach($nslist AS $prefix => $base_uri) {
  if($prefix == 'bio2rdf') continue;
  $cmd .= "DB.DBA.XML_SET_NS_DECL ('$prefix', '$base_uri', 2);"; 
 }
  echo $out = shell_exec($cmd_pre.$cmd.$cmd_post);
  exit;
}


// do delete graph option
if($options['deletegraph'] == "true") {
 $cmd = "sparql clear graph <".$options['graph'].">";
 echo "Deleting ".$options['graph'].PHP_EOL;
 echo $out = shell_exec($cmd_pre.$cmd.$cmd_post);
 if($options['deleteonly'] == "true") exit;
}

// check for valid file
if($options['file'] == 'filename' || !file_exists($options['file'])) {
 echo "File ".$options['file']." does not exists. Please specify a *real* file with the file=filename option";
 exit;
}


// add file to graph
echo "Adding ".$options['file']." into ".$options['graph'].PHP_EOL;
if($options['format'] == 'n3') {
 // http://docs.openlinksw.com/virtuoso/fn_ttlp_mt.html
 $program = "DB.DBA.TTLP_MT"; 
} else {
 // http://docs.openlinksw.com/virtuoso/fn_rdf_load_rdfxml_mt.html
 $program = 'DB.DBA.RDF_LOAD_RDFXML';
}
$cmd = $program."(file_to_string_output ('".$options['file']."'), '', '".$options['graph']."', ".$options['flags'].", ".$options['threads']."); checkpoint;";

//echo $cmd_pre.$cmd.$cmd_post;

echo $out = shell_exec($cmd_pre.$cmd.$cmd_post);
if(strstr($out,"Error")) {
  exit;
}

// Facet update : http://virtuoso.openlinksw.com/dataspace/dav/wiki/Main/VirtFacetBrowserInstallConfig
if($options['updatefacet'] == "true") {
	$cmd = "RDF_OBJ_FT_RULE_ADD (null, null, 'All');VT_INC_INDEX_DB_DBA_RDF_OBJ ();urilbl_ac_init_db();s_rank();";
	echo "Updating facet";
	echo $out = shell_exec($cmd_pre.$cmd.$cmd_post);
}


if($options['initialize'] == 'true') {
  $cmd = "drop index RDF_QUAD_OPGS;drop index RDF_QUAD_POGS;drop index RDF_QUAD_GPOS;drop index RDF_QUAD_OGPS;checkpoint;
  create table R2 (G iri_id_8, S iri_id_8, P iri_id_8, O any, primary key (S, P, O, G)); alter index R2 on R2 partition (S int (0hexffff00));
  log_enable (2); insert into R2 (G, S, P, O) select G, S, P, O from RDF_QUAD;
  drop table RDF_QUAD; alter table R2 rename RDF_QUAD; checkpoint;
  create bitmap index RDF_QUAD_OPGS on RDF_QUAD (O, P, G, S) partition (O varchar (-1, 0hexffff));
  create bitmap index RDF_QUAD_POGS on RDF_QUAD (P, O, G, S) partition (O varchar (-1, 0hexffff));
  create bitmap index RDF_QUAD_GPOS on RDF_QUAD (G, P, O, S) partition (O varchar (-1, 0hexffff));
  checkpoint;";
  
}
?>
