<?php


$options = array(
 "i" => "",
 "indir" => "",
 "outdir" => "",
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
  if($options['indir'] == "") {
    echo "No directory to download into specified!".PHP_EOL;
    exit;
  }
  // download one or all files from NCBO bioportal
  $files = Download($options['i'],$options['indir']);
}

// file option
if($options['i'] !== '') {
 OBO2N3($options['i'],$options['indir'],$options['outdir']);
 exit;
}



// directory option
if($options['indir'] !== '') {
  if($options['outdir'] == '') {
   echo "output directory not specified!".PHP_EOL;
   exit;
  }
  require_once(dirname(__FILE__).'/../../lib/php/utils.php');
  $files = GetDirFiles($options['indir'],"");
 
  if(isset($files)) {
   foreach($files AS $f) {
    OBO2N3($f,$options['indir'],$options['outdir']);

   }
   echo "Done!";
  } else {
    echo "No files to process in ".$options['indir'].PHP_EOL;
  }
  exit;
}






function OBO2N3($file,$indir,$outdir)
{
 require(dirname(__FILE__).'/../../lib/php/ns.php');
 require_once(dirname(__FILE__).'/../../lib/php/n3.php');

 $infile = $indir.$file;
 $outfile = $outdir.$file.'.n3';

 $in = fopen($infile,"r");
 if(FALSE === $in) {
	trigger_error("unable to open ".$infile);
	exit;
 }
 echo "Converting $infile to $outfile".PHP_EOL;


 if(FALSE !== ($pos = strrpos($infile,'\\'))) {
	$file = substr($infile,$pos+1);
 }else if(FALSE !== ($pos = strrpos($infile,'/'))) {
	$file = substr($infile,$pos+1);
 } else $file = $infile;
 $file .= ".n3";
 $ouri = "http://bio2rdf.org/ontology:$file";

 $buf = N3NSHeader($basenslist);
 $buf .= "@prefix obo: <http://bio2rdf.org/obo:>.".PHP_EOL;
 $buf .= "<$ouri> a $owl:Ontology .".PHP_EOL;
 $buf .= "<$ouri> rdfs:label \"N3 converted OBO ontology $file (OBO file obtained from NCBO Bioportal) [bio2rdf:ontology:$file]\".".PHP_EOL;
 $buf .= "<$ouri> dc:creator \"Michel Dumontier\".".PHP_EOL;

 while($l = fgets($in)) {
	if(strlen(trim($l)) == 0) continue;
	
	if(strstr($l,"[Term]")) {
		unset($typedef);
		$term = '';
		$tid = '';
		continue;
	} else if(strstr($l,"[Typedef]")) {
		unset($term);
		$tid = '';
		$typedef = '';
		continue;
	} 
	
	$a = explode(": ",trim($l));
	if(isset($intersection_of)) {
		if($a[0] != "intersection_of") {
			$intersection_of .= ")].".PHP_EOL;
			$obointersection_of .= "].".PHP_EOL;
			$buf .= $intersection_of;
			$buf .= $obointersection_of;
			unset($intersection_of);
		}
	}

	if(isset($typedef)) {
		if($a[0] == "id") {
			$c = explode(":",$a[1]);
			if(count($c) == 1) {$ns = "obo";$id=$c[0];}
			else {$ns = strtolower($c[0]);$id=$c[1];}
			if(!isset($nslist[$ns])) {
				$buf .= "@prefix $ns: <http://bio2rdf.org/$ns:>.".PHP_EOL;
				$nslist[$ns] = $ns;
			}
			$tid = $ns.":".$id;
			$buf .= "$tid dc:identifier \"$id\".".PHP_EOL;
		}
		if($a[0] == "name") {
			$buf .= "$tid rdfs:label \"".stripslashes($a[1])." [$tid]\".".PHP_EOL;
		}
		if($a[0] == "is_a") {
			if(FALSE !== ($pos = strpos($a[1],"!"))) $a[1] = substr($a[1],0,$pos-1);
			$buf .= "$tid rdfs:subPropertyOf ".strtolower($a[1]).".".PHP_EOL;
		} 

		if($a[0][0] == "!") $a[0] = substr($a[0],1);
		$buf .= "$tid obo:$a[0] \"".str_replace('"','',stripslashes($a[1]))."\".".PHP_EOL;

	} else if(isset($term)) {
			if($a[0] == "id") {	
				$buf .= SplitNSTerm($a[1], $ns, $id, $nslist, $b);
				$tid = $ns.":".$id;
				$buf .= "$tid rdfs:isDefinedBy <$ouri>.".PHP_EOL;
				$buf .= "$tid dc:identifier \"$id\".".PHP_EOL;
			}
			if($a[0] == "name") {
				$buf .= "$tid rdfs:label \"".stripslashes($a[1])." [$tid]\".".PHP_EOL;
			}
			//relationship "part_of GO:0042274". // followed by optional description
			if($a[0] == "relationship") {
				$b = explode(" ",$a[1]);
				$buf .= "$tid obo:$b[0] ".strtolower($b[1]).".".PHP_EOL;
			}
			if($a[0] == "property_value") {
				$b = explode(" ",$a[1]);
				$buf .= "$tid obo:$b[0] ".strtolower($b[1]).".".PHP_EOL;				
			}
			// XREF  obo:xref "EC:2.4.1.-".
			if($a[0] == "xref") {
				if(FALSE !== ($pos = strpos($a[1],":"))) {
					$nspart = explode(" ",substr($a[1],0,$pos));
					$idpart = explode(" ",substr($a[1],$pos+1));
					// identifier can only be the first after
					$ns = $nspart[0];
					$id = $idpart[0];
					$buf .= "$tid rdfs:seeAlso <http://bio2rdf.org/".strtolower($ns).":".stripslashes($id).">.".PHP_EOL;
				}				
			} else if($a[0] == "synonym") {
/* 
"N,N,N-tributylbutan-1-aminium fluoride EXACT IUPAC_NAME [IUPAC:]".
"C16H36FN RELATED FORMULA [SUBMITTER:]".
"[F-].CCCC[N+](CCCC)(CCCC)CCCC RELATED SMILES [ChEBI:]".
*/
				$rel = "SYNONYM";
				$list = array("EXACT","RELATED");
				foreach($list AS $keyword) {
				  // get everything after the keyword up until the bracket [
				  if(FALSE != ($k_pos = strpos($a[1],$keyword))) {
					$str_len = strlen($a[1]);
					$term_len = strlen($keyword);
					$term_end_pos = $k_pos+$term_len;
					$b_pos = strrpos($a[1],"[");
					$diff = $b_pos-$term_end_pos-1;
					if($diff != 0) {
  						// then there is more stuff here
						$k = substr($a[1],$term_end_pos+1,$diff);
						$rel = trim($k);
					} else {
					// create the long predicate
						$rel = $keyword."_SYNONYM";
					}
					break;
				   } 
				}
				if($k_pos === FALSE) {
					// we didn't find a keyword
					// so take from the start to the bracket
					$str = substr($a[1],0,$b_pos);
				} else {
					$str = substr($a[1],0,$k_pos);
				}
				$l = "$tid chebi:".strtolower($rel)." $str.".PHP_EOL;
				$buf .= $l;
			}
			if(FALSE !== ($pos = strpos($a[1],"!"))) $a[1] = substr($a[1],0,$pos-1);

			if($a[0] == "alt_id") {
				$buf .= strtolower($a[1])." rdfs:seeAlso $tid .".PHP_EOL;
			}			
			if($a[0] == "is_a") {
				// do subclassing
				$buf .= "$tid rdfs:subClassOf ".strtolower($a[1]).".".PHP_EOL;
			} 
			if($a[0] == "intersection_of") {
				// generate a blank node
				if(!isset($intersection_of)) {
					$intersection_of = "$tid owl:equivalentClass [a owl:Class; owl:intersectionOf (";
					$obointersection_of = "$tid obo:intersection_of [";
				}
				$c = explode(" ",$a[1]);
				if(count($c) == 1) {
					preg_match("/(.*) \! (.*)/",$c[0],$m);
					if(count($m)) $c[0] = $m[0];
					SplitNSTerm($c[0], $ns, $id, $nslist, $b);
					$intersection_of .= "$ns:$id";
					$obointersection_of .= "a $ns:$id;";
				} else if(count($c) == 2) {
					preg_match("/(.*) \! (.*)/",$c[1],$m);
					if(count($m)) $c[1] = $m[0];

					$rel = $c[0];
					$obj = $c[1];
					$buf .= SplitNSTerm($c[1], $ns, $id, $nslist, $b);
					$intersection_of .= " [owl:onProperty obo:$rel; owl:someValuesFrom $ns:$id] ";
					$obointersection_of .= "obo:$rel $ns:$id;";
				}
			} else
	 		  $buf .= "$tid obo:$a[0] \"".addslashes(str_replace('"','',stripslashes($a[1])))."\".".PHP_EOL;
					
		} else {
			// in the header
			//format-version: 1.0
			$a = explode(": ",trim($l));
			$buf .= "<$ouri> obo:$a[0] \"".str_replace('"','\"',$a[1])."\".".PHP_EOL;
		} 
	
 }
 if(isset($intersection_of))  $buf .= $intersection_of."].".PHP_EOL;

 fclose($in);
 file_put_contents($outfile,$buf);
}

function SplitNSTerm($term, &$ns, &$id, &$nslist, &$buf) 
{
 $buf = '';
 $a = explode(":",$term);
 if(count($a) == 1) {$ns = '';$id=$a;}
 if(count($a) == 2) {
  $ns = strtolower($a[0]);
  $id = $a[1];
 }
 if($ns && !isset($nslist[$ns])) {
   $buf = "@prefix $ns: <http://bio2rdf.org/$ns:>.".PHP_EOL;
   $nslist[$ns] = $ns;
 }
 return $buf;
}



function Download($file, $dir)
{
 $email = 'michel.dumontier@gmail.com';
 $ontolist = 'http://rest.bioontology.org/bioportal/ontologies?email='.$email;
 $ontolist = 'ontologies.txt';
 $c = file_get_contents($ontolist);
 
 $root = simplexml_load_string($c);
 if($root === FALSE) {
  trigger_error("Error in opening $ontolist");
  exit;
 }

 $data = $root->data->list;
 foreach($data->ontologyBean AS $d) {
   $oid = (string) $d->ontologyId;
   $label = (string) $d->displayLabel;
   $abbv = (string) strtolower($d->abbreviation);
   if(!$abbv) {
	$a = explode(" ",$label);
	if(count($a) == 1) $abbv = strtolower($label);
	else {
 	 foreach($a AS $b) {
	  $abbv .= $b[0];
         }
         $abbv = strtolower($abbv);
	}
   }
   $format = (string) $d->format;
   if($format == "PROTEGE") continue;

   echo "Downloading $label ($abbv id=$oid) ... ";

   $onto_url = 'http://rest.bioontology.org/bioportal/virtual/download/'.$oid.'?email='.$email;
   $onto = @file_get_contents($onto_url);
   if($onto !== FALSE) {
    if($format == "OBO") {
     $file = $dir."$abbv.obo";
     file_put_contents($file,$onto);
     $files [] = $file;
    } else {
     $file = $dir."$abbv.owl";
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

