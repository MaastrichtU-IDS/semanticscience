<?php

$prefix = "http://bio2rdf.org/";

$rfile = "http://www.brenda-enzymes.info/brenda_download/brenda_dl_0905.zip";

$file = "/opt/data/brenda/brenda_download.txt";
$n3file = "/opt/data/brenda/brenda.n3";
if(!file_exists($file)) {
	trigger_error("File $file doesn't exists");
	exit;
}
$n3fp = fopen($n3file,"w");


$id = '';
$fnx = '';
$ll = '';

$fp = fopen($file,"r");
while($l = fgets($fp)) {
   $l = rtrim($l);
//echo "line: $l".PHP_EOL;

   // if we see * - this is the copyright notice, so just ignore
   if($l[0] == '*') continue;

   // if there is nothing in the line, then process the last line
   if(strlen($l) == 0) {
     // end of function block
     if(function_exists($fnx)) {
	$b = $fnx($ll,$id);
	fwrite($n3fp,$b);
     }
     $fnx = '';
     $ll = '';
     continue;
   }
   if($l=='///') {
      // start of a new record
      if($id == '') continue;
 
      // store the record into the database
      // @todo
   }
   $a = explode("\t",$l);
//print_r($a);
   // if we see only one element in the array, then this corresponds to the function name
   if(count($a) == 1) {
	// function name
        $fnx = $a[0];
        continue;
   }
   if(count($a) == 2 && strlen($a[0]) == 0) {
     // add this to the previous line
     $ll .= " ".$a[1];
     continue; 
   } else {
     if($ll) {
       // process this line
       if(function_exists($fnx)) {
		$b = $fnx($ll,$id);
                fwrite($n3fp,$b);
       } 

       $ll = $l;
     } else {
       $ll = $l;
     }
     if($a[0] == 'ID') $id = $a[1];
   }
   

   // if the text corresponds to a function, then call the function with the file pointer so as to
   // process the text for the block

}

fclose($n3fp);
//*****************************************************************************************************************************************************//
//*****************************************************************************************************************************************************//

//************//
// FUNCTIONS: //
//************//

//******************************************************** PROTIEN ************************************************************************************//
function PROTEIN($l,$id)
{
 global $prefix;

//echo "PROTEIN:".$l.PHP_EOL;
  preg_match("/(PR\t#(\d+)#\s+(\w+\s+\w*\.*)\s+(\w*)\s+.*)+/", $l, $m);
//   print_r($m);
 
  $sid = "<$prefix/brenda_species:$id/species$m[2]>";
  $b = '';
  $b .= "<$prefix/brenda:$id> brenda:species $sid.".PHP_EOL;
  $b .= "$sid rdfs:label \"$m[3] [$sid]\".".PHP_EOL;
  $b .= "$sid rdf:type brenda:Species .".PHP_EOL;
  return $b;
}

//******************************************************** RECOMMENDED NAME ***************************************************************************//
function RECOMMENDED_NAME($l,$id)
{
 global $prefix;
 $a = explode("\t",$l);  
 $b = "<$prefix/brenda:$id> brenda:recommended_name \"$a[1]\".".PHP_EOL;
 return $b;
}

//******************************************************** SYSTEMATIC NAME ****************************************************************************//
function SYSTEMATIC_NAME($l,$id)
{
 global $prefix;
 $a = explode("\t",$l);  
 $b = "<$prefix/brenda:$id> brenda:systematic_name \"$a[1]\".".PHP_EOL;
 return $b;
}

//******************************************************** CAS REGISTERY NUMBER ***********************************************************************//
function CAS_REGISTRY_NUMBER($l,$id)
{
 global $prefix;
 $a = explode("\t",$l);  
 $b = "<$prefix/brenda:$id> brenda:cas_registry_number \"$a[1]\".".PHP_EOL;
 return $b;
}

//************************************************************** REACTION *****************************************************************************//
function REACTION($l,$id)
{
 global $prefix;
 $rx = explode("\t",$l);  
 $reaction = $rx[1];
 $b = "<prefix/brenda:$id> brenda:reaction_description \"$reaction\".".PHP_EOL;
 return $b;
}

//***********************************************************  REACTION_TYPE **************************************************************************//
function REACTION_TYPE($l,$id)
{
  global $prefix;
  $a = explode("\t",$l);
  $rxid = "<$prefix/brenda:$id/reaction>";
  $rtype = "brenda:".md5($a[1]);
  $rtype_uri = "<$prefix/brenda:".md5($a[1]).">";
  $n3 .= "$rxid a $rtype_uri";
  $n3 .= "$rtype_uri rdfs:label \"$a[1] [$rtype]\".".PHP_EOL;

  return $n3;
}

//******************************************************** TURN OVER NUMBER ***************************************************************************//
function TURNOVER_NUMBER($l,$id)
{
  global $prefix;

return ;

  $tid = "brenda:$id/turnover".md5($l);
  $b .= "$tid rdfs:label \"turnover number [$tid]\".".PHP_EOL;
  $b .= "$tid rdf:type brenda:TurnoverNumber .".PHP_EOL;

//$l = "TN	#4,16# 25 {NADPH}  (#16# pH 7.0, 25°C <14>; #4# pH 7.0, 25°C, wild-type enzyme <13>) <13,14>";
  preg_match("/TN\t#([0-9,]+)#\s([0-9\.?\-?]+)\s{(.*)}\s+(\(#[0-9]+#\s?(p?H? [0-9\.]+)?,?\s?([0-9\.]+)?°?C?)?/",$l,$m);
  if(count($m) == 0) {
	echo "error in parsing turnover number: $l"."\n";
  }
  $c = explode(",",$m[1]);
  foreach($c as $speciesid) {
   $sid = "brenda:$id/species$speciesid";
   $b .= "$tid brenda:species $sid .".PHP_EOL; 
  }

  $b .= "$tid brenda:kcat \"$m[2]\".".PHP_EOL;
  $b .= "$tid brenda:substrate \"$m[3]\".".PHP_EOL;
  $t = explode(" ",$m[4]);
  $b .= "$tid brenda:pH \"$t[1]\".".PHP_EOL;
  $b .= "$tid brenda:temperature \"$m[5]\".".PHP_EOL;

  return $b; 
}

//**************************************************************** Km Value ***************************************************************************//
function KM_VALUE($l,$id)
{
  $kid = "brenda:$id/km".md5($l);
  $b .= "$kid rdfs:label \"km [$kid]\".".PHP_EOL;
  $b .= "$kid rdf:type brenda:Km .".PHP_EOL;

//$l = "KM	#1# 0.29 {L-Xylulose}  <1>";
//$l = "KM	#4# 0.1 {1,4-dibromo-2,3-butanedione}  (#4# pH 7.0, 25°C, mutant K153M<13>) <13>";
  preg_match("/KM\t#([0-9,]+)#\s([0-9\.?\-?]+)\s{(.*)}\s+(\(#[0-9]+#\s?(p?H? [0-9\.]+)?,?\s?([0-9\.]+)?°?C?)?/",$l,$m);

return ;
 if(count($m) == 0) {
	echo $l."\n";   
 }

  $c = explode(",",$m[1]);

  foreach($c as $speciesid) {
   $sid = "brenda:$id/species$speciesid";
   $b .= "$kid brenda:species $sid .".PHP_EOL; 
  }

  $b .= "$kid brenda:km \"$m[2]\".".PHP_EOL;
  $b .= "$kid brenda:substrate \"$m[3]\".".PHP_EOL;
  $t = explode(" ",$m[4]);
  $b .= "$kid brenda:pH \"$t[1]\".".PHP_EOL;
  $b .= "$kid brenda:temperature \"$m[5]\".".PHP_EOL;

//echo $b;
//print_r($m);
//exit;
 
}


?>
