<?php

$force_dl = false;
$xml_dir = "/opt/data/linkedct/xml/";
$rdf_dir = "/opt/data/linkedct/n3/";
@mkdir($xml_dir,"0777",true);
@mkdir($rdf_dir,"0777",true);

$ids = array();

// open the crawl page
$crawl_url = "http://clinicaltrials.gov/ct2/crawl";
$crawl_html = $xml_dir."crawl.html";

if($force_dl || !file_exists($crawl_html)) {
 $crawl = file_get_contents($crawl_url);
 file_put_contents($crawl_html,$crawl);
}
$crawl = file_get_contents($crawl_html);
preg_match_all("/crawl\/([0-9]+)/",$crawl,$m);

foreach($m[1] AS $i) {
 $crawl2_url = "http://clinicaltrials.gov/ct2/crawl/".$i;
 $crawl2_html = $xml_dir."crawl_$i.html";
 if($force_dl || !file_exists($crawl2_html)) {
   $crawl2 = file_get_contents($crawl2_url);
   file_put_contents($crawl2_html,$crawl2);
 }
 $crawl2 = file_get_contents($crawl2_html);
 
 preg_match_all("/show\/(NCT[0-9]+)/",$crawl2,$n);
 
 foreach($n[1] AS $j) {
   $j = "NCT00000106";
   $page_url = "http://clinicaltrials.gov/ct2/show/$j?displayxml=true";
   $page_xml = $xml_dir."$j.xml";
   $page_rdf = $rdf_dir."$j.rdf";

   echo "$j\n";   
   if($force_dl || !file_exists($page_xml)) {
    $xml = file_get_contents($page_url);
    file_put_contents($page_xml,$xml);
   } 
   $xml = file_get_contents($page_xml);
   
   $rdf = CTXML2RDF($xml);
   
   file_put_contents($page_rdf,$rdf);   
   exit;
 }
}



function CTXML2RDF($xml)
{
 global $ids;
 $x = simplexml_load_string($xml);
 $id = $x->id_info->nct_id;
 
$header = "@prefix linkedct_trial: <http://bio2rdf.org/linkedct_trial:> .
@prefix linkedct_record: <http://bio2rdf.org/linkedct_record:> .
@prefix linkedct_entity: <http://bio2rdf.org/linkedct_entity:> .
@prefix linkedct_resource: <http://bio2rdf.org/linkedct_resource:> .
@prefix linkedct_intervention: <http://bio2rdf.org/linkedct_intervention:> .
@prefix linkedct_drug: <http://bio2rdf.org/linkedct_drug:> .
@prefix linkedct_agent: <http://bio2rdf.org/linkedct_agent:> .
@prefix linkedct_criteria: <http://bio2rdf.org/linkedct_criteria:> .
@prefix linkedct_outcome: <http://bio2rdf.org/linkedct_outcome:> .
@prefix linkedct_oversight: <http://bio2rdf.org/linkedct_oversight:> .
@prefix linkedct_arm: <http://bio2rdf.org/linkedct_arm:> .
@prefix linkedct_location: <http://bio2rdf.org/linkedct_location:> .
@prefix registry_record: <http://bio2rdf.org/registry_record:> .
@prefix registry_dataset: <http://bio2rdf.org/registry_dataset:> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix serv: <http://bio2rdf.org/serv:> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
";

$dataset= "registry_dataset:linkedct rdfs:label \"LinkedCT is the data from clinicaltrials.gov\" .
registry_dataset:linkedct linkedct_resource:url <http://clinicaltrials.gov> .
linkedct_record:$id dc:partOf registry_dataset:linkedct .".PHP_EOL;

$record = "linkedct_record:$id a serv:Record .
linkedct_record:$id a registry_record:linkedct_record .
linkedct_record:$id rdfs:label \"Record #$id from ClinicalTrials.gov [linkedct_record:$id]\" .
linkedct_record:$id dc:title \"ClinicalTrials.gov Record #$id\" .
";
 
$entity = "linkedct_trial:$id a linkedct_resource:ClinicalTrial .
linkedct_trial:$id rdfs:label \"$x->brief_title [linkedct_trial:$id]\" .
linkedct_trial:$id dc:title \"$x->brief_title\" .
linkedct_trial:$id dc:identifier \"$id\" .
linkedct_trial:$id rdfs:isDefinedBy linkedct_record:$id .
";
 
 //echo $buf;
 foreach($x->children() AS $n => $c) {
   // check for the nested structure 
   switch($n) {
    case "required_header" :
	 $record .= "linkedct_record:$id linkedct_resource:download_date \"$c->download_date\" ." .PHP_EOL;
	 $record .= "linkedct_record:$id linkedct_resource:provider_html \"$c->url\" ." .PHP_EOL;
	 $record .= "linkedct_trial:$id linkedct_resource:provider_html \"$c->url\" ." .PHP_EOL;
	 break;

	case "id_info" :
	 foreach($c->children() AS $k => $v) {
		$entity .= "linkedct_trial:$id linkedct_resource:$k \"$v\" .".PHP_EOL;
	}
	break;
	
	case "oversight_info":
	 $name = $c->authority;
	 $tid = GetId("oversight",$id.$name);
	 $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_oversight", $tid, "linkedct_resource:Oversight", "Oversight for $id by $name") ;
	 if(isset($c->has_dmc)) $entity .= "linkedct_oversight:$tid linkedct_resource:has_dmc \"$c->has_dmc\" .".PHP_EOL;
	 
	 $aid = GetId("agent",$name, $exists);
	 if(!$exists) {
		$entity .= CreateEntryN3("linkedct_record", $id, "linkedct_agent", $aid, "linkedct_resource:Agent", $name) ;
	 }
	 $entity .= "linkedct_oversight:$tid linkedct_resource:agent linkedct_agent:$aid .".PHP_EOL;
	 break;
	 
	case "responsible_party":
	 if($n == "responsible_party")$name = $c->name_title;
	case "overall_contact":
	 if($n == "overall_contact")  $name = $c->last_name;
	case "overall_official":
	 if($n == "overall_official") $name = $c->last_name;
	 
	 $tid = GetId("agent",$name, $exists);
	 if(!$exists) {
		$entity .= CreateEntryN3("linkedct_record", $id, "linkedct_agent", $tid, "linkedct_resource:Agent", $name) ;
		 foreach($c->children() AS $k => $v) {
			$entity .= "linkedct_agent:$tid linkedct_resource:$k \"$v\" .".PHP_EOL;
		 }
	  }
	  $entity .= "linkedct_trial:$id linkedct_resource:$n linkedct_agent:$tid .".PHP_EOL;
	break;
	 
	case "brief_summary" :
	 $title = "Brief summary of trial $id";
	 $text = str_replace("\n      ","",trim($c->textblock));
	 $tid = GetId("entity",$title, $exists);
	 if(!$exists) 
	   $entity .= CreateEntryN3("linkedct_trial", $id, "linkedct_entity", $tid, "linkedct_resource:$n", $title);
	 $entity .= "linkedct_trial:$id linkedct_resource:$n linkedct_entity:$tid .".PHP_EOL;
	 $entity .= "linkedct_entity:$tid linkedct_resource:value \"\"\"".$text."\"\"\". ".PHP_EOL;
	 break;	  
	  
	case "detailed_description" :
	 $title = "Detailed description of trial $id";
	 $text = str_replace("\n      ","",trim($c->textblock));
	 $tid = GetId("entity",$title, $exists);
	 if(!$exists)
 	  $entity .= CreateEntryN3("linkedct_trial", $id, "linkedct_entity", $tid, "linkedct_resource:$n", $title);
	 $entity .= "linkedct_trial:$id linkedct_resource:$n linkedct_entity:$tid .".PHP_EOL;
	 $entity .= "linkedct_entity:$tid linkedct_resource:value \"\"\"".$text."\"\"\". ".PHP_EOL;
	 break;
	 
	case "primary_outcome" :
	case "secondary_outcome" :
 	 if($n == "primary_outcome") $outcome_type = "PrimaryOutcome";
	 else $outcome_type = "SecondaryOutcome";
	 
	 $title = "$c->measure ;Time Frame: $c->time_frame; Designated as safety issue: $c->safety_issue";
	 $tid = GetId("outcome",$title);
	 $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_outcome", $tid, "linkedct_resource:$outcome_type", $title) ;	  
	 $entity .= "linkedct_outcome:$tid linkedct_resource:measure \"$c->measure\" ;
 linkedct_resource:time_frame \"$c->time_frame\" ;
 linkedct_resource:safety_issue \"$c->safety_issue\" .".PHP_EOL;
	 break;
	 
	case "intervention" :
	 if(!isset($ids['intervention'])) $iid = $ids['intervention'] = 1;
	 else $iid = ++$ids['intervention'];
	 $title = "$c->intervention_type intervention : $c->intervention_name";
	 $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_intervention", $iid, "linkedct_resource:Intervention", $title) ;
	 $entity .= "linkedct_trial:$id linkedct_resource:intervention linkedct_intervention:$iid .".PHP_EOL;
	 
	 if($c->intervention_type == "Drug") {
	  $drug_id = GetId("drug",$c->intervention_name);
	  $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_drug", $drug_id, "linkedct_resource:Drug", $c->intervention_name) ;
	  $entity .= "linkedct_intervention:$iid linkedct_resource:involves linkedct_drug:$drug_id .".PHP_EOL;
	 }
	 if($c->description) $entity .= "linkedct_intervention:$iid dc:description \"\"\"$c->description\"\"\" .".PHP_EOL;
	 if(isset($c->arm_group_label)) {
		foreach($c->arm_group_label AS $arm_group_label) {
			$title = "Trial $arm_group_label for $id";
			$arm = $ids['arm_name'][md5($title)];
			$entity .= "linkedct_intervention:$iid linkedct_resource:arm linkedct_arm:$arm .".PHP_EOL;
		}
	 } 
	 if(isset($c->other_name)) {
		foreach($c->other_name AS $synonym) {
			$entity .= "linkedct_intervention:$iid linkedct_resource:synonym \"$synonym\" .".PHP_EOL;
		}
	 }
	 
	 break;
	  
	case "arm_group":
	 $title = "Trial $c->arm_group_label for $id";
	 $tid = GetId("arm",$title);
	 $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_arm", $tid, "linkedct_resource:ClinicalArm", $title) ;
	 $entity .= "linkedct_arm:$tid dc:description \"$c->description\" .
linkedct_trial:$id linkedct_resource:arm linkedct_arm:$tid .".PHP_EOL;
     break;
   
    case "eligibility":
     $entity .= ProcessCriteria($id, $c->criteria->textblock); 
     break;
   
	default: 
	  if(strstr($n,"date")) {
		if(in_array($n, array("firstreceived_date","lastchanged_date"))) $ns = "linkedct_record";
		else $ns = "linkedct_trial";
	    $entity .= ProcessDate($ns,$id,$n,$c);
	   break;
	  }
	
	  // check for attributed elements
	  // <enrollment type="Anticipated">150</enrollment>
	  if($c->attributes()) {
	   $a = $c->attributes();
	   foreach($a AS $x => $y) {
	    $entity .= "linkedct_trial:$id linkedct_resource:".strtolower($y)."_".$n." \"$c\" .".PHP_EOL;
	   }
       break;	
	  // check for children
	  } else if(count($c->children())) {
	    //echo "children: $n\n";
	    $entity .= Children2N3($id, $n, $c);
	  // otherwise it's an attribute
	  } else {
	    $exists = false;
		$tid = GetId('entity',$c, $exists);
		if(!$exists) {
		  $entity .= CreateEntryN3("linkedct_record", $id, "linkedct_entity", $tid, "linkedct_resource:Entity", $c) ;
		}
	   $entity .= "linkedct_trial:$id linkedct_resource:$n linkedct_entity:$tid .".PHP_EOL;
	  }
	 break;
   }
 
 }
 //return $header."registry_dataset:linkedct {
//".$record.$entity."}";
 return $header.$dataset.$record.$entity;
}

function Children2N3($id, $n, $c)
{
 global $ids;
 $entity = '';
 
 $nested = false;
 foreach($c AS $d => $e) {
  if(count($e)) {$nested = true; break;}
 }
 
 if($nested) echo "nested:$n\n";
 else echo "not nested:$n\n";
 
 if($nested == false) {
 	// create a new object with the attributes
	$tid = GetId($n,$c);
	$entity .= CreateEntryN3("linkedct_record", $id, "linkedct_$n", $tid, "linkedct_resource:$n", "$n $id") ;
	$entity .= "linkedct_trial:$id linkedct_resource:$n linkedct_$n:$tid .
";
 }
 
 
 
 foreach($c AS $d => $e) {
  
  switch($n) {
   case "sponsors": /** lead_sponsors **/ /** collaborator **/
	  $title = $e->agency;
	  $agent_id = GetId("agent",$title);
	  $a .= CreateEntryN3("linkedct_record", $id, "linkedct_agent", $agent_id, "linkedct_resource:$d", $title) ;
	  $a .= "linkedct_trial:$id linkedct_resource:$d linkedct_agent:$agent_id .".PHP_EOL;
      break;

   case "location":
	  $title = $e->name;
	  $tid = GetId("location",$title);
	  $a .= CreateEntryN3("linkedct_record", $id, "linkedct_location", $tid, "linkedct_resource:$d", $title) ;
	  $a .= "linkedct_trial:$id linkedct_resource:location linkedct_location:$tid .".PHP_EOL;
    // now the location data
	  if(isset($e->address)) {
		foreach($e->address->children() AS $key => $value) {
		$a .= "linkedct_location:$tid linkedct_resource:$key \"$value\" .".PHP_EOL;
	  }
	}
   break;
  
  default:
   if(!$e) {
	//echo $d.PHP_EOL;
	continue;
   }
   //echo $d.PHP_EOL;
   $a .= "linkedct_trial:$id linkedct_resource:$d \"$e\" .".PHP_EOL;
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
	  $title = $t; $cid = GetId("criteria",$title);
	  $buf .= CreateEntryN3("linkedct_record", $id, "linkedct_criteria", $cid, "linkedct_resource:$status", $title) ;
	  $buf .= "linkedct_trial:$id linkedct_resource:ClinicalTrialCriteria linkedct_criteria:$cid .
";
      $t = '';
	}
	
	if(strstr($text,"Inclusion Criteria")) {$status = "InclusionCriteria";continue;}
	else if(strstr($text,"Exclusion Criteria")) {$status = "ExclusionCriteria";continue;}

	if($text[0] == '-') $t = substr($text,3);
	else $t .= " ".$text;
  }
  if($t) {
	  $title = $t; $cid = GetId("criteria",$title);
	  $buf .= CreateEntryN3("linkedct_record", $id, "linkedct_criteria", $cid, "linkedct_resource:$status", $title) ;
	  $buf .= "linkedct_trial:$id linkedct_resource:ClinicalTrialCriteria linkedct_criteria:$cid .
";
}
  
  return $buf;
}

function GetId($type,$name, &$exists = false)
{
	global $ids;
	$exists = false;
	$md5 = md5($name);
	if(!isset($ids[$type.'_name'][$md5])) {
		if(!isset($ids[$type])) $id = $ids[$type] = 1;
		else $id = ++$ids[$type];
		$ids[$type.'_name'][$md5] = $id;
	} else {$id = $ids[$type.'_name'][$md5]; $exists = true;}
	return $id;
}
	
function CreateEntryN3($record_prefix, $record_id, $entity_prefix, $entity_id, $entity_type, $title) 
{
	return "$entity_prefix:$entity_id rdfs:isDefinedBy $record_prefix:$record_id .
$entity_prefix:$entity_id rdfs:label \"$title [$entity_prefix:$entity_id]\" .
$entity_prefix:$entity_id dc:identifier \"$entity_id\" .
$entity_prefix:$entity_id dc:title \"$title\" .
$entity_prefix:$entity_id a $entity_type .
";
}

function GetMonthNumber($month)
{
	$m = array ("January"=>"01","February"=>"02","March"=>"03","April"=>"04","May"=>"05","June"=>"06","July"=>"07","August"=>"08","September"=>"09","October"=>"10","November"=>"11","December"=>"12");
	if(!isset($m[$month])) echo "Invalid $month".PHP_EOL;
	else return $m[$month];
}


/* July 2002; January 20, 2010 */
function ProcessDate($ns,$id, $field, $date)
{
	$a = explode(" ",$date);
	$m = GetMonthNumber($a[0]);
	if(count($a) == 2) {
		$y = $a[1];
		$r = "$ns:$id linkedct_resource:$field \"$y-$m-01\"^^xsd:date .".PHP_EOL; //gYearMonth
	} else {
		$d = str_pad(substr($a[1],0,-1), 2, "0", STR_PAD_LEFT);
		$y = $a[2];
		$r = "$ns:$id linkedct_resource:$field \"$y-$m-$d\"^^xsd:date .".PHP_EOL;
	}
	return $r;
}
