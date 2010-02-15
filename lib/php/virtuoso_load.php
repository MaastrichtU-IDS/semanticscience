<?php

/*
http://virtuoso.openlinksw.com/dataspace/dav/wiki/Main/VirtFacetBrowserInstallConfig
*/
$isql = "/bio2rdf/default/bin/isql";
//$isql = "isql";

$options = array(
 "file" => "filename",
 "dir" => "dirname",
 "graph" => "graphname",
 "port" => "1111",
 "user" => "dba",
 "pass" => "dba",
 "flags" => "16",
 "threads" => "4",
 "updatefacet" => "false",
 "deletegraph" => "false",
 "deleteonly" => "false",
 "initialize" => "false",
 "setns" => "false",
 "format" => "n3",
 "ignoreerror" => "true",
 "startat" => ""
);


// show options
if($argc == 1) {
 echo "Usage: php $argv[0] ".PHP_EOL;
 foreach($options AS $key => $value) {
  echo " $key=$value ". PHP_EOL;
 }
}

// set options from user input
foreach($argv AS $i=> $arg) {
 if($i==0) continue;
 $b = explode("=",$arg);
 if(isset($options[$b[0]])) $options[$b[0]] = $b[1];
 else {echo "unknown key $b[0]";exit;}
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
if($options['dir'] == 'dirname') {
 // must be a file
 if(!file_exists($options['file'])) {
  echo "File ".$options['file']." does not exists. Please specify a *real* file with the file=filename option\n";
  exit;
 }
 $files[] = $options['file'];
} else {
 if(!is_dir($options['dir'])) {
  echo "Directory ".$options['dir']." does not exists. Please specify a *real* directory with the dir=dirname option\n";
  exit;
 } 
 // get the files
 $files = GetFiles($options['dir']);
}


// add file to graph
if($options['format'] == 'n3') {
 // http://docs.openlinksw.com/virtuoso/fn_ttlp_mt.html
 $program = "DB.DBA.TTLP_MT"; 
// $program = "DB.DBA.TTLP_MT_LOCAL_FILE";
} else {
 // http://docs.openlinksw.com/virtuoso/fn_rdf_load_rdfxml_mt.html
 $program = 'DB.DBA.RDF_LOAD_RDFXML';
}

foreach($files AS $file) {
 if($options['startat'] != '') {
  if($options['startat'] == $file) { $options['startat'] = ''; }
  else continue;
 }

 echo 'Processing '.$file."\n";

 // if the graph has not been set, then create a graph name from the file, minus path and extension
 $graph = $options['graph'];
 if($graph == "graphname") {
  $pos = strrpos($file,"/");
  if($pos !== FALSE) {
   $graph = substr($file,$pos+1);
  }
  $pos = strpos($graph,".");
  if($pos !== FALSE) {
   $graph = substr($graph,0,$pos);
  }
  $graph = "http://bio2rdf.org/graph/".$graph;
 }

 $path = '';
 $pos = strrpos($file,"/");
 if($pos !== FALSE) {
   $path = substr($file,0, $pos+1);
 }

 $f = $file;
 $fcmd = 'file_to_string_output';
 if(strstr($file,".gz")) {
   $gzfile = $file;
   $un = substr($file,0,-3);
   
   $out = fopen($un,"w");
   $in = gzopen($file,"r");
   while($l = gzgets($in)) {
       fwrite($out,$l);
   }
   fclose($out);
   gzclose($in);
   
   $f = $un;
 } elseif(strstr($file,".bz")) {
   $bzfile = $file;
   $un = substr($file,0,-3);
   $out = fopen($un,"w");
   $in = bzopen($file,"r");
   while($l = bzread($in)) {
	fwrite($out,$l);
   }
   fclose($out);
   bzclose($in);
   $f = $un;
 }

 $t1 = $path."t1.txt"; // the source
 $t2 = $path."t2.txt"; // the destination
 if(file_exists($t1)) unlink($t1);
 if(file_exists($t2)) unlink($t2);

 do { 
  echo "Loading $file into $graph ...".PHP_EOL; 
  $cmd = $program."($fcmd ('$f'), '', '".$graph."', ".$options['flags'].", ".$options['threads']."); checkpoint;";
  // echo $cmd_pre.$cmd.$cmd_post;
  $out = shell_exec($cmd_pre.$cmd.$cmd_post);
 
  if(strstr($out,"Error")) {
    // *** Error 37000: [Virtuoso Driver][Virtuoso Server]SP029: TURTLE RDF loader, line 43: syntax error
    preg_match("/Error ([0-9]+)\:/",$out,$m);
    if(!isset($m[1]) || (isset($m[1]) && $m[1] != '37000')) {
	// some other error
	echo $out;
	exit;
    } 

    preg_match("/line\s([0-9]+)\:/",$out,$m);
    if(!isset($m[1])) {
	// some problem here
	exit;
    }

    $line = $m[1]; 
   // write to log?
    echo "Skipping line:$line ... ";

   // we need find find the line number, and slice the file  
    if(!file_exists($t1)) {
      // first use
      echo "making copy of $f\n";
      copy($f,$t1);
    }
    if(file_exists($t2)) {
	unlink($t1);
 	rename($t2,$t1);
    } 
    $fp_in = fopen($t1,"r");
    $fp_out = fopen($t2,"w");
    $i = 0;
    while($l = fgets($fp_in,4096)) {
      $i++;
      if($i == $line) echo "Problem in: $l\n";
      if($l[0] == '@' || $i > $line) {
	fwrite($fp_out,$l);
      }
    }
    fclose($fp_in);
    fclose($fp_out);
    $f=$t2;
  } else {
	if(file_exists($t1)) unlink($t1);
	if(file_exists($t2)) unlink($t2);
	echo "Done!\n";
	break;
  }
 } while (true);

 if(strstr($file,".gz") || strstr($file,".bz")) {
  if(file_exists($f)) unlink($f);
 }
 echo PHP_EOL;

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

function GetFiles($dirname)
{
 $d = dir($dirname);
 while (false !== ($e = $d->read())) {
   if($e == '.' || $e == '..') continue;
   $files[] = $dirname.$e;
 }
 sort($files);
 $d->close();
 return $files;
}
?>
