<?php

require('../../php-lib/rdfapi.php');
require('../../arc2/ARC2.php');
$odir = "sio/release/";
$cdir = getcwd();
$sio_file = $cdir . "/sio.owl";
$parser = ARC2::getRDFParser();
$parser->parse('file://'.$sio_file);
$triples = $parser->getTriples();
$index = ARC2::getSimpleIndex($triples, false);

$ns = array( 
	'rdf' => 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
	'rdfs' => 'http://www.w3.org/2000/01/rdf-schema#',
	'owl' => 'http://www.w3.org/2002/07/owl#',
	'dct' => 'http://purl.org/dc/terms/',
	'sio' => 'http://semanticscience.org/resource/',
	'dc' => "http://purl.org/dc/elements/1.1/",
	'vann' => "http://purl.org/vocab/vann/",
	'cito' => "http://purl.org/spar/cito/",
	'protege' => "http://protege.stanford.edu/plugins/owl/protege#",
	'xsd' => "http://www.w3.org/2001/XMLSchema#"
);

$equiv = array(
	$ns['owl'].'Class' => $ns['owl'].'EquivalentClass',
	$ns['owl'].'ObjectProperty' => $ns['owl'].'EquivalentProperty',
	$ns['owl'].'DatatypeProperty' => $ns['owl'].'EquivalentProperty'
);

$sio = 'http://semanticscience.org/ontology/sio.owl';
$o = $index[$sio]['http://www.w3.org/2002/07/owl#versionInfo'][0]; 
$sio_version = $o['value'];
$version_iri = "http://semanticscience.org/ontology/sio/v".$sio_version."/sio-release.owl";

function writeGraph($filepath, $myindex)
{
  global $ns;
  $conf = array('ns' => $ns);
  $ser =  ARC2::getRDFXMLSerializer($conf);
  file_put_contents($filepath, $ser->getSerializedIndex($myindex));
}

function getParents($child, &$subClassOf)
{
	$parents = null;
	if(isset($subClassOf[$child])) {		
		foreach($subClassOf[$child] AS $parent) {
			$parents[] = $parent;
			$p = getParents($parent, $subClassOf);
			if(is_array($p)) $parents = array_merge($parents, $p);
		}
	}
	return $parents;
}
function getChildren($parent, &$superClassOf)
{
	$children = null;
	if(isset($superClassOf[$parent])) {
		foreach($superClassOf[$parent] AS $child) {
			$children[] = $child;
			$c = getChildren($child,$superClassOf);
			if(is_array($c)) $children = array_merge($children, $c);
		}
	}
	return $children;
}

// first identify relevant terms
foreach($index AS $s => $p_list) {
	foreach($p_list AS $p => $o_list) {
		// generate the label associative array
		if($p == "http://www.w3.org/2000/01/rdf-schema#label") {
			$label = $o_list[0]['value'];
			
			# camel case labels
			$camel_label_local_part = ucwords($label);
			$camel_label_local_part = str_replace(array(" ",'(',')'), "",$camel_label_local_part);
			foreach($p_list[$ns['rdf'].'type'] AS $p) {
				if($p['value'] == $ns['owl'].'ObjectProperty' || $p['value'] == $ns['owl'].'DatatypeProperty') {
					$camel_label_local_part = lcfirst($camel_label_local_part);
					break;
				}
			}
			$camel_label_uri = "http://semanticscience.org/resource/".urlencode($camel_label_local_part);
			$camel_labels[$s] = $camel_label_uri;

			# dash labels
			$dash_label = str_replace(" ","-", $label);
			$dash_label_uri = "http://semanticscience.org/resource/".urlencode($dash_label);
			$dash_labels[$s] = $dash_label_uri;
		}
		
		// get the subclass relationships for transitive closure
		if($p == $ns['rdfs'].'subClassOf' || $p == $ns['rdfs'].'subPropertyOf') {
			foreach($o_list AS $o) {
				if($o['type'] == 'uri' && $s != $o['value']) {
					$subClassOf[$s][] = $o['value'];
					$superClassOf[$o['value']][] = $s;
				}
			}
		}
		
		// generate the subset array
		if($p == "http://semanticscience.org/resource/subset") {
			foreach($o_list AS $o) {
				$subsets[$s][] = $o['value'];
			}
		}
		
		// generate the relations list
		if($p == $ns['rdf'].'type') {
			foreach($o_list AS $o) {
				if($o['value'] == $ns['owl'].'ObjectProperty' || 
				$o['value'] == $ns['owl'].'DatatypeProperty') {
					$relations[$s] = '';
				}
			}
		}
	}
}

// build up the list of terms required for transitive closures
$tree = array();
foreach($index AS $s => $p_list) {
	// subsets
	if(isset($subsets[$s])) {
		foreach($subsets[$s] AS $i => $subset) {
			// need to exclude rdfs:subClassOf and rdfs:subPropertyOf
			if(strstr($subset,"++")) {
				// generate the transitive closure up and down
				$new_subset_name = substr($subset,0,-2);
				$tree[$new_subset_name]['include'][] = $s;
				$children = getChildren($s, $superClassOf);
				if(is_array($children)) 
					$tree[$new_subset_name]['include'] = array_merge($tree[$new_subset_name]['include'], $children);
					
				$parents = getParents($s, $subClassOf);
				if(is_array($parents)) 
					$tree[$new_subset_name]['include'] = array_merge($tree[$new_subset_name]['include'], $parents);
				unset($subsets[$s][$i]);
			} else if(strstr($subset,"+")) {			
				$new_subset_name = substr($subset,0,-1);
				$tree[$new_subset_name]['include'][] = $s;
				// need to generate transitive closure
				$children = getChildren($s, $superClassOf);
				if(is_array($children)) 
					$tree[$new_subset_name]['include'] = array_merge($tree[$new_subset_name]['include'], $children);
				unset($subsets[$s][$i]);
			}
			if(strstr($subset,"-")) {
				$new_subset_name = substr($subset,0,-1);
				$tree[$new_subset_name]['exclude'][] = $s;
				// need to generate transitive closure
				$children = getChildren($s, $superClassOf);
				if(is_array($children)) 
					$tree[$new_subset_name]['exclude'] = array_merge($tree[$new_subset_name]['exclude'], $children);
				unset($subsets[$s][$i]);				
			}
		}
	}
}

// populate the per subject uri list
foreach($tree AS $subset => $ie_list) {
	// intersect the include + exclude
	if(isset($ie_list['exclude'])) {
		foreach($ie_list['exclude'] AS $exc) {
			foreach($ie_list['include'] AS $i => $inc) {
				if($exc == $inc) {
					unset($ie_list['include'][$i]);
					break;
				}
			}
		}
	}

	foreach($ie_list['include'] AS $s) {
		$subsets[$s][] = $subset;
	}
}


// now select the subclass/subproperty attributes where appropriate
foreach($index AS $s => $p_list) {
	// subsets
	if(isset($subsets[$s])) {
		foreach($subsets[$s] AS $subset) {		
			if($subset == "sadi") {
				// flat list
				$myplist = $p_list;
				if(isset($myplist[$ns['rdfs'].'subClassOf'])) 
					unset($myplist[$ns['rdfs'].'subClassOf']);
				if(isset($myplist[$ns['rdfs'].'subPropertyOf'])) 
					unset($myplist[$ns['rdfs'].'subPropertyOf']);
				$indexes[$subset][$s] = $myplist;
			} else {
				// only keep uri references to those in the subset
				$myplist = $p_list;
				foreach($myplist AS $p => $o_list) {
					foreach($o_list AS $i => $o) {
						$exclude = false;
						if($o['type'] == 'bnode') $exclude = true;
						if($o['type'] == 'uri' && !strstr($o['value'],"owl")) {
							if(isset($subsets[$o['value']])) {
								$exclude = true;
								foreach($subsets[$o['value']] AS $subs) {
									if($subs == $subset) {$exclude = false;break;}
								}
							}
						}
						if($subset=="relations" && 
							($p == $ns['rdfs'].'domain' || $p == $ns['rdfs'].'range')) {
								$exclude = true;
						}
						if($exclude) unset($myplist[$p][$i]);
					}
				}
				$indexes[$subset][$s] = $myplist;
			}
		}
	}
}

foreach($camel_labels AS $s => $uri) {
	$equiv_relation = null;
	$types = $index[$s][ $ns['rdf'].'type'];
	foreach($types AS $o) {
		if(isset($equiv[ $o['value'] ])) {
			$equiv_relation = $equiv[ $o['value'] ];
			$o['value'] = $uri;
			$indexes['equivs'][$s][$equiv_relation][] = $o;
			
			$o['value'] = $s;
			$indexes['equivs'][$uri][$equiv_relation][] = $o;
		}
	}
}

foreach($dash_labels AS $s => $uri) {
	$equiv_relation = null;
	$types = $index[$s][ $ns['rdf'].'type'];
	foreach($types AS $o) {
		if(isset($equiv[ $o['value'] ])) {
			$equiv_relation = $equiv[ $o['value'] ];
			$o['value'] = $uri;
			$indexes['equivs'][$s][$equiv_relation][] = $o;
			
			$o['value'] = $s;
			$indexes['equivs'][$uri][$equiv_relation][] = $o;
		}
	}
}

foreach($index AS $s => $p_list) {	
	// labels document
	if(isset($camel_labels[$s])) $s_uri = $camel_labels[$s];
	else $s_uri = $s;
	
	foreach($p_list AS $p => $o_list) {
		if(isset($camel_labels[$p])) $p_uri = $camel_labels[$p];
		else $p_uri = $p;
		
		foreach($o_list AS $o) {
			if(isset($camel_labels[$o['value']])) {
				$o['value'] = $camel_labels[$o['value']];
			} 
			$indexes['camelcase-label'][$s_uri][$p_uri][] = $o;
		}
	}

	// add dc:identifier
	$o = null;
	$o['value'] = substr($s,strrpos($s,"/")+1);
	$o['type'] = 'literal';
	$index[$s][ $ns['dc'].'identifier'][] = $o;

	// add equivs
	if(isset($indexes['equivs'][$s_uri])) {
		foreach($indexes['equivs'][$s_uri] AS $equiv_rel => $arr) {
			foreach($arr AS $o) {
				$indexes['camelcase-label'][$s_uri][$equiv_rel][] = $o;
			}
		}
	}
}

foreach($index AS $s => $p_list) {	
	// labels document
	if(isset($dash_labels[$s])) $s_uri = $dash_labels[$s];
	else $s_uri = $s;
	
	foreach($p_list AS $p => $o_list) {
		if(isset($dash_labels[$p])) $p_uri = $dash_labels[$p];
		else $p_uri = $p;
		
		foreach($o_list AS $o) {
			if(isset($dash_labels[$o['value']])) {
				$o['value'] = $dash_labels[$o['value']];
			} 
			$indexes['dash-labels'][$s_uri][$p_uri][] = $o;
		}
	}
}

$vi = $index[$sio]['http://www.w3.org/2002/07/owl#versionInfo'];
foreach($indexes AS $subset => $ind) {
	unset($myindex);

	// add the version iri
	//unset($index[$sio]['http://www.w3.org/2002/07/owl#versionInfo']);
	$myindex = $ind;

//	$myindex[$sio] = $index[$sio];
	$sio_subset_file = "sio-subset-".$subset.".owl";
	$o = null;
	$o['value'] = $sio_subset_file;
	$o['type'] = 'literal';
	
	$myindex[$sio]['http://www.w3.org/2002/07/owl#versionInfo'][] = $o;
	
	$sio_versioned_uri = "http://semanticscience.org/ontology/sio/v".$sio_version."/".$sio_subset_file;
	$o = null;
	$o['value'] = $sio_versioned_uri;
	$o['type'] = 'uri';
	$myindex[$sio]['http://www.w3.org/2002/07/owl#versionIRI'][] = $o;
	
	// add rdfs:isDefinedBy
	foreach($myindex AS $s => $p_obj) {
		if(!strstr($s,"semanticscience")) continue;
		$o = null;
		$o['value'] = $sio_versioned_uri;
		$o['type'] = 'uri';
		$myindex[$s]['http://www.w3.org/2000/01/rdf-schema#isDefinedBy'][] = $o;
		
		// @todo add http://open.vocab.org/terms/defines
	}
	
	// add the subset to the main one
	$sio_subset_url = "http://semanticscience.org/ontology/".$sio_subset_file;
	$o = null;
	$o['value'] = $sio_subset_url;
	$o['type'] = 'uri';
	$index[$sio]['http://rdfs.org/ns/void#subset'][] = $o;
	
	
	echo "generating $subset".PHP_EOL;
	writeGraph($odir."sio-subset-$subset.owl",$myindex);
}

echo "generating versioned SIO".PHP_EOL;

$index[$sio]['http://www.w3.org/2002/07/owl#versionInfo'] = $vi;
foreach($index AS $s => $p_obj) {
	if(!strstr($s,"semanticscience")) continue;
	$o = null;
	$o['value'] = 'http://semanticscience.org/ontology/sio.owl';
	$o['type'] = 'uri';
	$index[$s]['http://www.w3.org/2000/01/rdf-schema#isDefinedBy'][] = $o;
}
$o['value'] = $version_iri;
$o['type'] = 'uri';
$index[$sio]['http://www.w3.org/2002/07/owl#versionIRI'][] = $o;

$o['value'] = date('Y-m-d'); #DateTime::ISO8601);
$o['type'] = 'literal';
$o['datatype'] = 'http://www.w3.org/2001/XMLSchema#date';
$index[$sio]['http://purl.org/dc/terms/modified'][] = $o;

copy($odir."sio-subset-dash-labels.owl", $odir."sio-subset-labels.owl");
writeGraph($odir."sio-release.owl", $index);
