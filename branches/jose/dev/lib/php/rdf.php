<?php

define("RDF","http://www.w3.org/1999/02/22-rdf-syntax-ns#");
define("RDFS","http://www.w3.org/2000/01/rdf-schema#");
define("OWL","http://www.w3.org/2002/07/owl#");
define("XML","http://www.w3.org/2001/XMLSchema#");
define("NS","&ss;");
define("SS","http://semanticscience.org/ontology/");
define("BIO2RDF","http://bio2rdf.org/");

function MakeORP($object, $role, $role_type, $process)
{
	$buf = '';
	$buf .= Statement($object,  "ss:hasRole", $role);
	$buf .= Statement($role, "rdf:type", $role_type);
	$buf .= Statement($role, "ss:isRealizedIn",$process);
	return $buf;
}
function MakeOQP($object, $quality, $quality_type, $process = NULL)
{
	$buf = '';
	$buf .= Statement($object, "ss:hasQuality", $quality);
	$buf .= Statement($quality, "rdf:type", $quality_type);
	if(isset($process)) $buf .= Statement($quality, "ss:isAgentIn",$process);
	return $buf;
}
function MakeOQVU($object, $quality, $quality_type, $value, $unit = NULL, $unit_type = NULL)
{
	$buf = '';
	$buf .= Statement($object, "ss:hasQuality", $quality);
	$buf .= Statement($quality, "rdf:type", $quality_type);
	$buf .= Statement($quality, "ss:hasValue", $value, "");
	if(isset($unit)) {
		$buf .= Statement($quality, "ss:hasUnit", $unit);
		if(isset($unit_type)) $buf .= Statement($unit, "rdf:type", $unit_type);
	}
	return $buf;
}

function MakeOQV($object, $quality, $quality_type, $value)
{
	return MakeOQVU($object, $quality, $quality_type, $value);
}


function MakeOQ($object, $quality, $quality_type)
{
	$buf = '';
	$buf .= Statement($object, "ss:hasQuality", $quality);
	$buf .= Statement($quality, "rdf:type", $quality_type);
	return $buf;
}


function MakeType($subject, $type, $type_ns)
{
return '
<'.$type_ns.':'.$type.' rdf:about="'.$subject.'"/>';
}

function Statement($s, $p, $o, $dt = NULL)
{
	if(!is_null($dt)) {
return '
<owl:Thing rdf:about="'.$s.'"><'.$p.'>'.$o.'</'.$p.'></owl:Thing>';
	}
	return '
<owl:Thing rdf:about="'.$s.'"><'.$p.' rdf:resource="'.$o.'"/></owl:Thing>';
}


function GetHeader($filename, $namespaces = NULL)
{

$a = '<?xml version="1.0"?>


<!DOCTYPE rdf:RDF [
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY dc "http://purl.org/dc/elements/1.1/" >
    <!ENTITY ss "http://semanticscience.org/ontology/" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY owl2xml "http://www.w3.org/2006/12/owl2-xml#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >';
	if(isset($namespaces)) {
		foreach($namespaces AS $prefix => $ns) {
			$a .= '
    <!ENTITY '.$prefix.' "'.$ns.'" >';
		}
	}
$a .= '
]>

<rdf:RDF xmlns="http://semanticscience.org/ontology/"
     xml:base="'.$filename.'"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:owl2xml="http://www.w3.org/2006/12/owl2-xml#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:ss="http://semanticscience.org/"';

	if(isset($namespaces)) {
		foreach($namespaces AS $prefix => $ns) {
			$a .= '
     xmlns:'.$prefix.'="'.$ns.'"';
		}
	}
	$a .= '
>
'; 
	return $a;
}

function GetFooter()
{
return '
</rdf:RDF>';
}
?>