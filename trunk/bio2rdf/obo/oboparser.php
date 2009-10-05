<?php

require(dirname(__FILE__).'/../../lib/php/n3.php');

$options = array(
 "i" => "filename",
 "o" => "filename",
 "f" => "n3"
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

if($options['i'] == 'filename' || !file_exists($options['i'])) {
 echo "File ".$options['i']." does not exists. Please specify a *real* file with the i=filename option";
 exit;
}

$in = fopen($options['i'],"r");
if(FALSE === $in) {
	trigger_error("unable to open ".$options['i']);
	exit;
}
if($options['o'] == 'filename') {
  // add .n3
  $options['o'] = $options['i'].'.n3';
}
echo "Converting ".$options['i']." to ".$options['o'].PHP_EOL;



if(FALSE !== ($pos = strrpos($options['i'],'\\'))) {
	$file = substr($options['i'],$pos+1);
}else if(FALSE !== ($pos = strrpos($options['i'],'/'))) {
	$file = substr($options['i'],$pos+1);
} else $file = $opitons['i'];
$file .= ".owl";
$ouri = "http://semantiscience.org/ontology/$file";

$buf = N3NSHeader($basenslist);
$buf .= "@prefix obo: <http://bio2rdf.org/obo:>.".PHP_EOL;
$buf .= "<$ouri> a $owl:Ontology .".PHP_EOL;

while($l = fgets($in)) {
	if(strlen(trim($l)) == 0) continue;
	
	if(strstr($l,"[Term]")) {
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
				$buf .= "$tid rdfs:label \"$a[1] [$tid]\".".PHP_EOL;
			}
			
			preg_match("/(.*) \! (.*)/",$a[1],$m);
			if(count($m)) {
				$a[1] = $m[1];
			}
			if($a[0] == "is_a") {
				// do subclassing
				$buf .= "$tid rdfs:subClassOf ".strtolower($a[1]).".".PHP_EOL;
			} 
			$buf .= "$tid obo:$a[0] \"".str_replace('"','',$a[1])."\".".PHP_EOL;
					
		} else {
			// in the header
			//format-version: 1.0
			$a = explode(": ",trim($l));
			$buf .= "<$ouri> obo:$a[0] \"".str_replace('"','\"',$a[1])."\".".PHP_EOL;
		} 
	}
}
fclose($in);
file_put_contents($options['o'],$buf);

?>
