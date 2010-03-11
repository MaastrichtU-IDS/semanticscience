<?php

$force_dl = false;
$dir = "pages/";
$ids = array();

// open the crawl page
$crawl_url = "http://clinicaltrials.gov/ct2/crawl";
$crawl_html = $dir."crawl.html";

if($force_dl || !file_exists($crawl_html)) {
 $crawl = file_get_contents($crawl_url);
 file_put_contents($crawl_html,$crawl);
}
$crawl = file_get_contents($crawl_html);
preg_match_all("/crawl\/([0-9]+)/",$crawl,$m);

foreach($m[1] AS $i) {
 $crawl2_url = "http://clinicaltrials.gov/ct2/crawl/".$i;
 $crawl2_html = $dir."crawl_$i.html";
 if($force_dl || !file_exists($crawl2_html)) {
   $crawl2 = file_get_contents($crawl2_url);
   file_put_contents($crawl2_html,$crawl2);
 }
 $crawl2 = file_get_contents($crawl2_html);
 
 preg_match_all("/show\/(NCT[0-9]+)/",$crawl2,$n);
 
 foreach($n[1] AS $j) {
   $j = "NCT00576927";
   $page_url = "http://clinicaltrials.gov/ct2/show/$j?displayxml=true";
   $page_xml = $dir."$j.xml";
   
   if($force_dl || !file_exists($page_xml)) {
    $xml = file_get_contents($page_url);
    file_put_contents($page_xml,$xml);
   } 
   $xml = file_get_contents($page_xml);
   
   CTXML2RDF($xml);
   
   exit;
   
 }

}



function CTXML2RDF($xml)
{
 $x = simplexml_load_string($xml);
 $id = $x->id_info->nct_id;
 
$header = "@prefix linkedct: <http://bio2rdf.org/linkedct:> .
@prefix linkedct_record: <http://bio2rdf.org/linkedct_record:> .
@prefix linkedct_resource: <http://bio2rdf.org/linkedct_resource:> .
@prefix linkedct_intervention: <http://bio2rdf.org/linkedct_intervention:> .
@prefix linkedct_drug: <http://bio2rdf.org/linkedct_drug:> .
@prefix linkedct_agent: <http://bio2rdf.org/linkedct_agent:> .
@prefix linkedct_criteria: <http://bio2rdf.org/linkedct_criteria:> .
@prefix linkedct_facility: <http://bio2rdf.org/linkedct_facility:> .
@prefix registry_record: <http://bio2rdf.org/registry_record:> .
@prefix registry_dataset: <http://bio2rdf.org/registry_dataset> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix serv: <http://bio2rdf.org/serv:> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
";
 
$record = "linkedct_record:$id a serv:Record .
linkedct_record:$id a registry_record:linkedct_record .
linkedct_record:$id rdfs:label \"Record #$id from ClinicalTrials.gov [linkedct_record:$id]\" .
linkedct_record:$id dc:title \"ClinicalTrials.gov Record #$id\" .
linkedct_record:$id dc:partOf registry_dataset:linkedct .
";
 
$entity = "linkedct:$id a linkedct_resource:ClinicalTrial .
linkedct:$id rdfs:label \"$x->brief_title [linkedct:$id]\" .
linkedct:$id dc:title \"$x->brief_title\" .
linkedct:$id dc:identifier \"$id\" .
linkedct:$id rdfs:isDefinedBy linkedct_record:$id .
";
 
 //echo $buf;
 foreach($x->children() AS $n => $c) {
   // check for the nested structure
   
 
   switch($n) {
     case "required_header" :
	  $record .= "linkedct_record:$id linkedct_resource:download_date \"$c->download_date\" ." .PHP_EOL;
	  $record .= "linkedct_record:$id linkedct_resource:provider_html \"$c->url\" ." .PHP_EOL;
	  break;
	 case "brief_summary" :
	  $entity .= "linkedct:$id linkedct_resource:brief_summary \"\"\"".str_replace("\n      ","",trim($c->textblock))."\"\"\". ".PHP_EOL;
	  break;	  
	 case "detailed_description" :
	  $entity .= "linkedct:$id linkedct_resource:description \"\"\"".str_replace("\n      ","",trim($c->textblock))."\"\"\". ".PHP_EOL;
	  break;
	  
	 case "lastchanged_date" :
	 case "verification_date" :
	 case "firstreceived_date" :
	  $entity .= "linkedct_record:$id linkedct_resource:$n \"$c\" .".PHP_EOL;
	  break;
	 case "primary_outcome" :
	 case "secondary_outcome" :
	  if(!isset($ids['outcome'])) $outcome_id = $ids['outcome'] = 1;
	  else $outcome_id = ++$ids['outcome'];
	  if($n == "primary_outcome") $type = "PrimaryOutcome";
	  else $type = "SecondaryOutcome";
	  
$entity .= "linkedct_outcome:$outcome_id a linkedct_resource:$type ;
 rdfs:isDefinedBy linkedct_record:$id ;
 rdfs:label \"$c->measure [ Time Frame: $c->time_frame ] [ Designated as safety issue: $c->safety_issue ] [linkedct_outcome:$outcome_id]\" ;
 dc:identifier \"$outcome_id\" ;
 linkedct_resource:measure \"$c->measure\" ;
 linkedct_resource:time_frame \"$c->time_frame\" ;
 linkedct_resource:safety_issue \"$c->safety_issue\" .
";

	 break;
	 
	 case "intervention" :
	  if(!isset($ids['intervention'])) $iid = $ids['intervention'] = 1;
	  else $iid = ++$ids['intervention'];
	  
$entity .= "linkedct:$id linkedct_resource:intervention linkedct_intervention:$iid .
linkedct_intervention:$iid rdfs:isDefinedBy linkedct_record:$id .
linkedct_intervention:$iid a linkedct_resource:$c->intervention_type .
linkedct_intervention:$iid rdfs:label \"$c->intervention_type intervention : $c->intervention_name [linkedct_intervention:$iid]\" .
linkedct_intervention:$iid dc:title \"$c->intervention_type intervention : $c->intervention_name\" .
";
if($c->intervention_type == "Drug") {
	if(!isset($ids['drug'])) $drug_id = $ids['drug'] = 1;
	else $drug_id = ++$ids['drug'];
	
$entity .= "linkedct_intervention:$iid linkedct_resource:involves linkedct_drug:$drug_id .
linkedct_drug:$drug_id rdfs:isDefinedBy linkedct_record:$id .
linkedct_drug:$drug_id a linkedct_resource:Drug .
linkedct_drug:$drug_id rdfs:label \"$c->intervention_name [linkedct_drug:$drug_id]\" .
linkedct_drug:$drug_id dc:identifier \"$drug_id\" .
linkedct_drug:$drug_id dc:title \"$c->intervention_name\" .
";
}
	  break;
	  
	 default: 
	  if(count($c->children())) {
	    $entity .= Children2N3($id, $n, $c);
 
	  } else {
	   $entity .= "linkedct:$id linkedct_resource:$n \"$c\" .".PHP_EOL;
	   //echo "default: $n\n";
	  }
	 break;
   }
 
 }
 //echo $header."registry_dataset:linkedct {".$record.$entity."}";
 echo $header.$record.$entity;
 exit;

}

function Children2N3($id, $n, $c)
{
 global $ids;
 $a = '';
 foreach($c AS $d => $e) {
 
  switch($d) {
  
   case "lead_sponsor":
   case "collaborator":
	if(!isset($ids['agent'])) $ids['agent'][] = "";
	
    if((FALSE === ($key = array_search($e->agency, $ids['agent'])))) {
     $ids['agent'][] = $e->agency;
	 $key = array_search($e->agency, $ids['agent']);
	 
	 $a .= "linkedct_agent:$key rdfs:isDefinedBy linkedct_record:$id .
linkedct_agent:$key a linkedct_resource:$d .
linkedct_agent:$key dc:title \"$e->agency\" .
linkedct_agent:$key rdfs:label \"$e->agency [linkedct_agent:$key]\" .
";
    }
    $a .= "linkedct:$id linkedct_resource:$d linkedct_agent:$key .".PHP_EOL;
    break;
   
   case "criteria":
     $a .= ProcessCriteria($id, $e->textblock);   
     break;
	 
   case "facility":
    if(!isset($ids['facility'])) $facility_id = $ids['facility'] = 1;
	else $facility_id = ++$ids['facility'];
	
	$a .= "linkedct_facility:$facility_id a linkedct:Facility .
linkedct_facility:$facility_id rdfs:label \"$e->name [linkedct_facility:$facility_id]\" .
linkedct_facility:$facility_id dc:title \"$e->name\" .
linkedct_facility:$facility_id dc:identifier \"$facility_id\" .
linkedct_facility:$facility_id rdfs:isDefinedBy linkedct_record:$id .
linkedct_facility:$id linkedct_resource:facility linkedct_facility:$facility_id .
";

// now the location data
    foreach($e->address->children() AS $key => $value) {
	 $a .= "linkedct_facility:$facility_id linkedct_resource:$key \"$value\" .
";
	}
   
	
   break;
  
  default:
   if(!$e) continue;
   $a .= "linkedct:$id linkedct_resource:$d \"$e\" .".PHP_EOL;
  }
  
  
 }
 return $a;
}

/*
Inclusion Criteria:
  -  diagnosed with Congenital Adrenal Hyperplasia (CAH)
  -  normal ECG during baseline evaluation

Exclusion Criteria:
  -  history of liver disease, or elevated liver function tests
  -  history of cardiovascular disease
*/
function ProcessCriteria($id, $c)
{
  global $ids;
  if(!isset($ids['criteria'])) $cid = $ids['criteria'] = 0;
  else $cid = $ids['criteria'];
  
  $buf = '';
  $status = '';
  
  $t = '';
  $a = explode("\n",str_replace("          ","",$c));
  foreach($a AS $text) {
    $text = trim($text);
	if(!$text) continue;
		
	if($text[0] == '-' && $t) { // process the last one
	$criteria_id = ++$ids['criteria'];
	$buf .= "linkedct:$id linkedct_resource:trial_criteria linkedct_criteria:$criteria_id .
linkedct_criteria:$criteria_id rdfs:isDefinedBy linkedct_record:$id .	
linkedct_criteria:$criteria_id a linkedct_resource:$status .
linkedct_criteria:$criteria_id rdfs:label \"$t [linkedct_criteria:$criteria_id]\" .
linkedct_criteria:$criteria_id dc:title \"$t\" .
"; 
     $t = '';
	}
	
	if(strstr($text,"Inclusion Criteria")) {$status = "InclusionCriteria";continue;}
	else if(strstr($text,"Exclusion Criteria")) {$status = "ExclusionCriteria";continue;}

	if($text[0] == '-') $t = substr($text,3);
	else $t .= $text;
  }
  if($t) {
  	$criteria_id = ++$ids['criteria'];
	$buf .= "linkedct:$id linkedct_resource:trial_criteria linkedct_criteria:$criteria_id .
linkedct_criteria:$criteria_id rdfs:isDefinedBy linkedct_record:$id .	
linkedct_criteria:$criteria_id a linkedct_resource:$status .
linkedct_criteria:$criteria_id rdfs:label \"$t [linkedct_criteria:$criteria_id]\" .
linkedct_criteria:$criteria_id dc:title \"$t\" .
"; 
}
  
  return $buf;
}
