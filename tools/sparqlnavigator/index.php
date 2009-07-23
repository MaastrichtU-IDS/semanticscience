<?php

///// HTTP PARAMS
define("SPARQL_ENDPOINT","sparql_endpoint");
define("SPARQL_ENDPOINT_DEFAULT","sparql_endpoint_default");

define("GRAPH_IRI","graph_iri");
define("GRAPH_IRI_DEFAULT","graph_iri_default");

define("SEARCH","search");
define("MSEARCH","msearch");

define("FORMAT","format");
define("STYLESHEET","xsl");

define("BREADCRUMBS",'bc');
define("BC_DELIM",";");
// paging
define("LIMIT","limit");
define("OFFSET","offset");
define("START","start");

define("SUBMIT","Go!");


$defaults = array (
  SPARQL_ENDPOINT => array(
	"http://demo.openlinksw.com/sparql",
	"http://bio2rdf.org/sparql"),
	"http://dumontierlab.com:8890/sparql",
	"http://clusterhead.dumontierlab.com:8890/sparql", 
  GRAPH_IRI => array(
	"http://dumontierlab.com",
	"http://bio2rdf.org"),
  FORMAT => array(
	"html", 
/*	"rdf/xml", 
	"json", 
	"xml", 
	"n3",
	"text",
        "Exhibit"
*/   )
);


SetOptions($options);

if(isset($_REQUEST[SUBMIT]) && $options->SPARQL_ENDPOINT != '' && $options->SEARCH != '') {
 GetResults($options,$results);
 FormatResults($options,$results);
} else {
 ShowPage($options);
}




function SetOptions(&$options)
{

$options = '';
if(isset($_REQUEST[SPARQL_ENDPOINT]) && $_REQUEST[SPARQL_ENDPOINT] != '') {
  $options->SPARQL_ENDPOINT = $_REQUEST[SPARQL_ENDPOINT];

  // change in values
  if(isset($_REQUEST[SPARQL_ENDPOINT_DEFAULT]) && $_REQUEST[SPARQL_ENDPOINT_DEFAULT] != '' 
		&& $_REQUEST[SPARQL_ENDPOINT_DEFAULT] != $_REQUEST[SPARQL_ENDPOINT]) {
    $options->SPARQL_ENDPOINT = $_REQUEST[SPARQL_ENDPOINT_DEFAULT];
  }

} elseif( isset($_REQUEST[SPARQL_ENDPOINT_DEFAULT]) && $_REQUEST[SPARQL_ENDPOINT_DEFAULT] != '') {
  $options->SPARQL_ENDPOINT = $_REQUEST[SPARQL_ENDPOINT_DEFAULT];
} else {
  $options->SPARQL_ENDPOINT = '';
}

if(isset($_REQUEST[GRAPH_IRI]) && $_REQUEST[GRAPH_IRI] != '') {
  $options->GRAPH_IRI = $_REQUEST[GRAPH_IRI];

  //change in values
  if(isset($_REQUEST[GRAPH_IRI_DEFAULT]) && $_REQUEST[GRAPH_IRI_DEFAULT] != '' 
		&& $_REQUEST[GRAPH_IRI_DEFAULT] != $_REQUEST[GRAPH_IRI]) {
    $options->GRAPH_IRI = $_REQUEST[GRAPH_IRI_DEFAULT];
  }

} elseif( isset($_REQUEST[GRAPH_IRI_DEFAULT]) && $_REQUEST[GRAPH_IRI_DEFAULT] != '') {
  $options->GRAPH_IRI = $_REQUEST[GRAPH_IRI_DEFAULT];
} else {
  $options->GRAPH_IRI = '';
}

$options->SEARCH = $_REQUEST[SEARCH];
if($options->SEARCH != '') {
	if($options->SEARCH == "*") $options->MSEARCH = "?search";
	else $options->MSEARCH = "<".$options->SEARCH.">";
}

$options->BREADCRUMBS = $_REQUEST[BREADCRUMBS];
$options->BREADCRUMBS .= $options->SEARCH.BC_DELIM;

$options->FORMAT = $_REQUEST[FORMAT];

if(!isset($_REQUEST[LIMIT])) $_REQUEST[LIMIT] = 10;
$options->LIMIT = $_REQUEST[LIMIT];

$options->results = '';

}




function ShowPage($options)
{
 global $defaults;

$buf = '
<html>
 <head>
  <title>SPARQL Navigator</title> 
  <script type="text/javascript" language="JavaScript" src="http://dumontierlab.com/js/expandcollapse.js"></script>
  <style>a {font-size:0.75em};div#literal {font-size:0.75em}</style>
 </head>
 <body>

<center>
<h3>SPARQL Navigator</h3>
</center>
Enter a URI or * to browse.
<br>
<form>
  <input size="60" name="'.SEARCH.'" type="text" value="'.$options->SEARCH.'"/>
  <input name="'.SUBMIT.'" type="submit" value="'.SUBMIT.'"/>
  <br>
<table><tr valign="top"><td>
<img alt="Expand" border="0" src="http://dumontierlab.com/images/plus.jpg" class="ec" id="options_expand" onclick="doExpandCollapse(\'options\');">
</td><td>
<div style="display: block" id="options_summary">SPARQL options.</div><div style="display: none" id="options_content">
<strong>Set options:</strong> <br>

 Choose the SPARQL endpoint: 
  <select name="'.SPARQL_ENDPOINT_DEFAULT.'">
   <option value=""></option>';
foreach($defaults[SPARQL_ENDPOINT] AS $s) {

 $buf .= '
   <option value="'.$s.'">'.$s.'</option>';
}
$buf .= '
  </select><br>
  or enter it here: <input size="45" name="'.SPARQL_ENDPOINT.'" type="text" value="'.$options->SPARQL_ENDPOINT.'"/><br>

  Choose an optional Graph IRI: 

  <select name="'.GRAPH_IRI_DEFAULT.'">
   <option value=""></option>';
foreach($defaults[GRAPH_IRI] AS $s) {

 $buf .= '
   <option value="'.$s.'">'.$s.'</option>';
}
$buf .= '
 </select><br>
 Or select it here:  <input size="45" name="'.GRAPH_IRI.'" type="text" value="'.$options->GRAPH_IRI.'"/><br>

  

  Get results as: 
  <select name="'.FORMAT.'">';
foreach($defaults[FORMAT] AS $s) {
 $selected = '';
 if($s == $options->FORMAT) $selected = "SELECTED" ;

 $buf .= '
   <option value="'.$s.'" '.$selected.'>'.$s.'</option>';
}
$buf .= '
 </select><br/>


 Maximum results: <input name="'.LIMIT.'" type="text" value="'.$options->LIMIT.'"/><br>

</div>
</td></tr></table>

</form>';

$buf .= HTMLBreadcrumbs($options)."<br><br>";

$buf .= $options->results;

$buf .= '
 </body>
</html>';

echo $buf;
}

function GetGraphs($options, &$graphs)
{
  $sparql = 'SELECT DISTINCT ?g WHERE { GRAPH ?g {?x ?y ?z}}';

}

function GetGraphsInvolvingSearch($options, &$graphs)
{
//  $sparql = "SELECT DISTINCT ?g WHERE { GRAPH ?g {?

}


function SPARQLSubject(&$options){return  '{'.$options->MSEARCH.' ?p ?o}';}
function SPARQLPredicate(&$options){return '{?s '.$options->MSEARCH.' ?o}';}
function SPARQLObject(&$options){return '{?s ?p '.$options->MSEARCH.'}';}
function SPARQLLiteral(&$options){return '{?s ?p ?o . FILTER(regex(?o,'.$options->SEARCH.',i))}';}
function SPARQLUnion(&$options){return SPARQLSubject.' UNION '.SPARQLPredicate.' UNION '.SPARQLObject;} 


function SPARQLSelectSubject(&$options) {return 'SELECT * WHERE '.SPARQLSubject($options);}
function SPARQLSelectPredicate(&$options) {return 'SELECT * WHERE '.SPARQLPredicate($options);}
function SPARQLSelectObject(&$options) {return 'SELECT * WHERE '.SPARQLObject($options);}

function SPARQLSelectGraphAndTriples(&$options){return 'SELECT ?g ?s ?p ?o WHERE { graph ?g {'.$options->MSEARCH.' ?p ?o}}';}
function SPARQLSelectGraph(&$options){return 'SELECT DISTINCT $g WHERE {graph $g {'.$options->MSEARCH.' ?p ?o} UNION graph $g{?s ?p '.$options->MSEARCH.'}}';}
function SPARQLConstructTriples(&$options){return 'CONSTRUCT {'.$options->MSEARCH.' ?y ?z} WHERE {'.$options->MSEARCH.' ?y ?z}';}
function SPARQLConstructGraph(&$options){return 'CONSTRUCT {$g '.$options->MSEARCH.' ?y ?z} WHERE {graph $g{ '.$options->MSEARCH.' ?y ?z}}';}

function PrepareSPARQL_XML(&$options, $which, &$sparql, &$format)
{
  if($which == "subject") $sparql = SPARQLSelectSubject($options);
  else if($which == "object") $sparql = SPARQLSelectObject($options);
  else if($which == "predicate") $sparql = SPARQLSelectPredicate($options);

  if($options->FORMAT=="html") {
     if($which == "predicate") {
       $sparql .= "ORDER BY ?s ?o";
     } else {
      if($options->SEARCH == "*") {
//         $sparql .= " ORDER BY ".$options->MSEARCH." ?p";
      } else {
         $sparql .= " ORDER BY ?p";
      }
     }
     $sparql .= " LIMIT ".$options->LIMIT;

  }
}


function PrepareSPARQLQuery($sparql_endpoint, $graph_iri, $sparql)
{  
  $a = $sparql_endpoint.
		'?default-graph-uri='.urlencode($graph_iri).
		'&query='.urlencode($sparql).
		'&format=xml'; // '.$options->FORMAT.
//		'&query='.urlencode($sparql).
//		'&format=application%2Frdf%2Bxml'; // '.$options->FORMAT.
//		'&format=text%2Fn3%2Bturtle'. // '.$options->FORMAT.
//		'&debug=off';
  return $a;
}

function GetResults(&$options, &$results)
{
  // as subject
  PrepareSPARQL_XML($options, 'subject', $sparql, $options->FORMAT);
  $url = PrepareSPARQLQuery($options->SPARQL_ENDPOINT, $options->GRAPH_IRI, $sparql);
  $results['subject'] = file_get_contents($url);

  // as predicate
  PrepareSPARQL_XML($options, 'predicate', $sparql, $options->FORMAT);
  $url = PrepareSPARQLQuery($options->SPARQL_ENDPOINT, $options->GRAPH_IRI, $sparql);
  $results['predicate'] = file_get_contents($url);

  // as object
  PrepareSPARQL_XML($options, 'object', $sparql, $options->FORMAT);
  $url = PrepareSPARQLQuery($options->SPARQL_ENDPOINT, $options->GRAPH_IRI, $sparql);
  $results['object'] = file_get_contents($url);

}


function RewriteURI($options, $in)
{
  return "?".SPARQL_ENDPOINT."=".$options->SPARQL_ENDPOINT.
	"&".GRAPH_IRI."=".URLENCODE($options->GRAPH_IRI).
	"&".SEARCH."=".URLENCODE($in).
        "&".BREADCRUMBS."=".URLENCODE($options->BREADCRUMBS).
	"&".LIMIT."=".$options->LIMIT.
	"&".FORMAT."=".$options->FORMAT.
        "&".SUBMIT."=".SUBMIT;

}



function FormatResultsInHTML(&$options,&$results)
{
 $html = '';

 foreach($results AS $type => $result) {

  $xml = simplexml_load_string($result);
  $a = $xml->results;
  if(!isset($a->result)) continue;
  $rows = $elabel = $ecomment = '';
 
  foreach($a->result AS $r) { 
    $binding = $r->binding;

    if(count($binding) == 2) {
     // on subject
     if($type == 'subject') {
      $s->uri = $options->SEARCH;
      $p = $binding[0];
      $o = $binding[1];
     } else if($type == 'predicate') {
     $p->uri = $options->SEARCH;
      $s = $binding[0];
      $o = $binding[1];
    } else if($type == 'object') {
      $s = $binding[0];
      $p = $binding[1];
      $o->uri = $options->SEARCH;
    }

   } else if(count($binding) == 3) {
     // we searched for all triples
     $s = $binding[0];
     $p = $binding[1];
     $o = $binding[2];
    }

    $row = '';
    $row .= '<tr valign="top">';
    $row .= '<td>';
    $uri = $s->uri;
    SplitByNS($uri, $ns, $prefix, $entity, $label);
    if(strstr($uri,"http://")) $row .= '[<a title="Linked data" href="'.$uri.'">LD</a>]';
    $row .= '&nbsp;<a href="'.RewriteURI($options,$uri).'">'.$label.'</a>'; 
    $row .= '</td>';

    $row .= '<td>';
    $uri = $p->uri;
    SplitByNS($uri, $ns, $prefix, $entity, $label);
    if(strstr($uri,"http://")) $row .= '&nbsp;&nbsp;[<a title="Linked data" href="'.$uri.'">LD</a>]';
    else $row .='&nbsp;&nbsp;';
    $row .= '&nbsp;<a href="'.RewriteURI($options,$uri).'">'.$label.'</a>&nbsp;&nbsp;';
    $row .= '</td>';

    $row .= '<td>';
    if(isset($o->uri) || isset($o->bnode)) {
     if(isset($o->uri)) $uri = $o->uri;
     else $uri = $o->bnode; 

     SplitByNS($uri, $ns, $prefix, $entity, $label);
     if(strstr($uri,"http://")) $row .= '[<a title="Linked data" href="'.$uri.'">LD</a>]';
     $row .= '&nbsp;<a href="'.RewriteURI($options,$uri).'">'.wordwrap($label,45,"<br>",true).'</a>';
    } else {
	$row .= "<span style=\"font-size: 0.75em;\">".wordwrap($o->literal,100,"<br>", true)."</span>";
        if($p->uri == "http://www.w3.org/2000/01/rdf-schema#label") {
          $elabel = $o->literal;
	}
        if($p->uri == "http://www.w3.org/2000/01/rdf-schema#comment") {
          $ecomment = $o->literal;
	}
    }

    $row .= '</td>';
    $row .= '</tr>';
    $rows .= $row;
  }

  $html .= "<strong>".ucfirst($type)."</strong>";   
  if($type == 'subject' && $elabel) {$html .= "<span style=\"font-size=1em\">$elabel</span><br><span class=\"comment\">".wordwrap($ecomment,150,"<br>",true)."</span>";}
  $html .= '<table cellspacing="0">';
  $html .= $rows."</table>";
 }
 $options->results .= $html;
}


function FormatResults(&$options, &$results)
{
 if($options->FORMAT == 'html') {
	FormatResultsInHTML($options,$results);
	ShowPage($options);
 } elseif($options->FORMAT == 'rdf/xml') {
	header("Content-type: text/xml");
	echo $results;
 }

}




function RewriteURLs(&$results, &$r)
{
// read results into into model
// iterate over triples
// rewrite urls
// add sameas to subject

$file = tempnam("/tmp","swb_");
file_put_contents($file,$results);

$rdfapi_dir = '/software/code/external/rdfapi-php/api/';
define("RDFAPI_INCLUDE_DIR", $rdfapi_dir);
include(RDFAPI_INCLUDE_DIR . "RdfAPI.php");
$model = ModelFactory::getDefaultModel();
$model->load($file);

// Get Iterator from model
$it = $model->getStatementIterator();

// Traverse model and output statements
$buf = '';
while ($it->hasNext()) {
   $statement = $it->next();
   $buf .= "Statement number: " . $it->getCurrentPosition() . "<BR>";
   $buf .= "Subject: " . $statement->getLabelSubject() . "<BR>";
   $buf .= "Predicate: " . $statement->getLabelPredicate() . "<BR>";
   $buf .=  "Object: " . $statement->getLabelObject() . "<P>";
}
$r= $buf;

}





function SplitByNS($in, &$ns, &$prefix, &$entity, &$label)
{
 $namespaces = array(
  "http://www.w3.org/1999/02/22-rdf-syntax-ns#" => "rdf",
  "http://www.w3.org/2000/01/rdf-schema#" => "rdfs",
  "http://www.w3.org/2002/07/owl#" => "owl",
  "http://purl.org/dc/elements/1.1/" => "dc",
  "http://ontology.dumontierlab.com/" => "dl",
  "http://semanticscience.org/" => "ss",
  "http://ontology.semanticscience.org/" => "ss",
  "http://bio2rdf.org/ns/bio2rdf" => "bio2rdf",
  "http://bio2rdf.org/" => "bio2rdf",
  "nodeID://" => "bn",
 );
 $ns = '';
 $prefix = '';
 $entity = '';

// check for canonical bio2rdf syntax  http://xxxx/ns:id
 $a = explode(":",$in);
 $b = explode("#",$in);
 if(count($a) == 3) {$x[0] = $a[0].$a[1];$x[1]=$a[2];$symbol=':';}
 if(count($b) == 2) {$x[0] = $b[0];$x[1]=$b[1];$symbol='#';}
 if(count($x) == 2) {
   $pos = strrpos($x[0],"/");   
   if(FALSE !== $pos) {
     $ns = substr($x[0],0,$pos);
     $prefix = substr($x[0], $pos+1);
     if(isset($namespaces[$x[0].$symbol])) {
	$prefix = $namespaces[$x[0].$symbol];
     }
     $label = $prefix.":".$x[1];
     return;
   }
 }



 foreach($namespaces AS $my_ns => $my_prefix) {
  if(FALSE !== strstr($in,$my_ns)) {
    $pos = strlen($my_ns);
    $entity = substr($in,$pos);
    $ns = $my_ns;
    $prefix = $my_prefix;
    $label = $prefix.":".$entity;
    return;
  }
 }
 $label = $in;

}


function HTMLBreadcrumbs(&$options)
{
 $html = '';

 $a = explode(BC_DELIM,URLDECODE($options->BREADCRUMBS));

 // pick the last 5?
 foreach($a AS $bc) {
   if($bc == '') continue;
   SplitByNS($bc, $ns, $prefix, $entity, $label);
   $html .= '>&nbsp;<a href="'.RewriteURI($options,$bc).'">'.$label.'</a>&nbsp;';
 }
// if($html) $html = "<strong>Trace</strong> <small>".nl2br(wordwrap($html))."</small>";
 if($html) $html = "<strong>Trace</strong> <small>".$html."</small>";
 return $html;
}
?>
