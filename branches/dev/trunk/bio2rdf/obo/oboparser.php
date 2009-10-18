<?php


$options = array(
 "i" => "filename",
 "o" => "filename",
 "f" => "n3",
 "d" => "",
 "dl" => "false",
);

// show options
if($argc == 1) {
 echo "Usage: php $argv[0] ".PHP_EOL;
 echo " Default values as follows, * mandatory".PHP_EOL;
 foreach($options AS $key => $value) {
  echo " $key=$value ";
  if($key == "file") echo "*";
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

if($options['dl'] == 'true') {
  if($options['d'] == "") {
    echo "No directory to download into specified!".PHP_EOL;
    exit;
  }
  // download one or all files from NCBO bioportal
  $files = Download($options['i'],$options['d']);
}

// directory option
if($options['d'] !== '') {
  // @TODO add option to read files in directory

  if(isset($files)) {
   foreach($files AS $infile) {
    OBO2N3($infile,"");
   }
   echo "Done!";
  } else {
    echo "No files to process in ".$options['d'].PHP_EOL;
  }
  exit;
}

// file option
if($options['i'] == 'filename' || !file_exists($options['i'])) {
 echo "File ".$options['i']." does not exists. Please specify a *real* file with the i=filename option".PHP_EOL;
 exit;
}

OBO2N3($options['i'],$options['o']);





function OBO2N3($infile,$outfile)
{
 require(dirname(__FILE__).'/../../lib/php/ns.php');
 require_once(dirname(__FILE__).'/../../lib/php/n3.php');
 $in = fopen($infile,"r");
 if(FALSE === $in) {
	trigger_error("unable to open ".$infile);
	exit;
 }
 if($outfile == 'filename' || $outfile == '') {
  // add .n3
  $outfile = $infile.'.n3';
 }
 echo "Converting $infile to $outfile".PHP_EOL;


 if(FALSE !== ($pos = strrpos($infile,'\\'))) {
	$file = substr($infile,$pos+1);
 }else if(FALSE !== ($pos = strrpos($infile,'/'))) {
	$file = substr($infile,$pos+1);
 } else $file = $infile;
 $file .= ".owl";
 $ouri = "http://semantiscience.org/ontology/$file";

 $buf = N3NSHeader($basenslist);
 $buf .= "@prefix obo: <http://bio2rdf.org/obo:>.".PHP_EOL;
 $buf .= "<$ouri> a $owl:Ontology .".PHP_EOL;

 while($l = fgets($in)) {
	if(strlen(trim($l)) == 0) continue;
	
	if(strstr($l,"[Term]") || strstr($l,"Typedef")) {
		$term = '';
		$tid = '';
	} else {
		if(isset($term)) {
			$a = explode(": ",trim($l));
			if($a[0] == "id") {
				$c = explode(":",$a[1]);
				$ns = strtolower($c[0]);
				$id = $c[1];
				if(!isset($nslist[$ns])) {
					$buf .= "@prefix $ns: <http://bio2rdf.org/$ns:>.".PHP_EOL;
					$nslist[$ns] = $ns;
				}
				$tid = $ns.":".$id;
			}
			if($a[0] == "name") {
				$buf .= "$tid rdfs:label \"".stripslashes($a[1])." [$tid]\".".PHP_EOL;
			}
			//relationship "part_of GO:0042274". // followed by optional description
			if($a[0] == "relationship") {
				$b = explode(" ",$a[1]);
				$buf .= "$tid obo:$b[0] ".strtolower($b[1]).".".PHP_EOL;
			}
			// XREF  obo:xref "EC:2.4.1.-".
			if($a[0] == "xref") {
				$b = explode(" ",$a[1]);
				$c = explode(":",$b[0]);
				$buf .= "$tid rdfs:seeAlso <http://bio2rdf.org/".strtolower($c[0]).":".stripslashes($c[1]).">.".PHP_EOL;
			}
			preg_match("/(.*) \! (.*)/",$a[1],$m);
			if(count($m)) {
				$a[1] = $m[1];
			}
			if($a[0] == "is_a") {
				// do subclassing
				$buf .= "$tid rdfs:subClassOf ".strtolower($a[1]).".".PHP_EOL;
			} 
			$buf .= "$tid obo:$a[0] \"".str_replace('"','',stripslashes($a[1]))."\".".PHP_EOL;
					
		} else {
			// in the header
			//format-version: 1.0
			$a = explode(": ",trim($l));
			$buf .= "<$ouri> obo:$a[0] \"".str_replace('"','\"',$a[1])."\".".PHP_EOL;
		} 
	}
 }
 fclose($in);
 file_put_contents($outfile,$buf);
}

function Download($file, $dir)
{
 $email = 'michel.dumontier@gmail.com';
 $ontolist = 'http://rest.bioontology.org/bioportal/ontologies?email='.$email;
 $ontolist = 'ontologies.txt';
 $c = file_get_contents($ontolist);
 
 preg_match_all("/\<ontologyId\>([0-9]+)\<\/ontologyId\>/",$c,$o);
 preg_match_all("/\<format\>([A-Za-z0-9 \-]+)\<\/format\>/", $c, $format);
 preg_match_all("/\<abbreviation\>([A-Za-z0-9 \-]+)\<\/abbreviation\>/",$c,$abb);

 if(count($o) != count($format) ||  count($o) != count($abb)) {
  echo "Unequal parsing - fix me";
  exit;
 }
 $n = 0;
 foreach($o[1] AS $i => $id) {
   if($format[1][$i] == "PROTEGE") continue;	
   $name = strtolower($abb[1][$i]);
   echo "Downloading $id ... ";

   $onto_url = 'http://rest.bioontology.org/bioportal/virtual/download/'.$id.'?email='.$email;
   $onto = @file_get_contents($onto_url);
   if($onto !== FALSE) {
    if($format[1][$i] == "OBO") {
     $file = $dir.$id."-".$name.".obo";
     file_put_contents($file,$onto);
     $files [] = $file;
    } else {
     $file = $dir.$id."-".$name.".owl";
     file_put_contents($file,$onto);
    }
    echo "Done!".PHP_EOL;
   } else {
    echo "Error!".PHP_EOL;
   }
 }
 return $files;
 exit;
}

?>
