<?php

require('../../../git/php-lib/rdfapi.php');
require('../../../git/arc2/ARC2.php');
$odir = "../../ontology/sio/release/";
$parser = ARC2::getRDFParser();
$parser->parse('file:///code/semanticscience/ontology/sio.owl');
$triples = $parser->getTriples();
$index = ARC2::getSimpleIndex($triples, false);

$ns = array( 
	'rdf' => 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
	'rdfs' => 'http://www.w3.org/2000/01/rdf-schema#',
	'owl' => 'http://www.w3.org/2002/07/owl#',
	'dc' => 'http://purl.org/dc/terms/',
	'sio' => 'http://semanticscience.org/resource/'
);

$equiv = array(
	$ns['owl'].'Class' => $ns['owl'].'EquivalentClass',
	$ns['owl'].'ObjectProperty' => $ns['owl'].'EquivalentProperty',
	$ns['owl'].'DatatypeProperty' => $ns['owl'].'EquivalentProperty'
);

$sio = 'http://semanticscience.org/ontology/sio.owl';
$o = $index[$sio]['http://www.w3.org/2002/07/owl#versionInfo'][0]; 
$sio_version = $o['value'];
//unset($index[$sio]['http://www.w3.org/2002/07/owl#versionInfo'][0]);

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
			$label_uri = "http://semanticscience.org/resource/".urlencode(str_replace(" ","-",$label));
			$labels[$s] = $label_uri;
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

foreach($labels AS $s => $uri) {
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
	if(isset($labels[$s])) $s_uri = $labels[$s];
	else $s_uri = $s;
	
	foreach($p_list AS $p => $o_list) {
		if(isset($labels[$p])) $p_uri = $labels[$p];
		else $p_uri = $p;
		
		foreach($o_list AS $o) {
			if(isset($labels[$o['value']])) {
				$o['value'] = $labels[$o['value']];
			} 
			$indexes['labels'][$s_uri][$p_uri][] = $o;
		}
	}
	/*
	$o = null;
	$o['type'] = 'literal';
	$o['value'] = $s_uri;
	$indexes['labels'][$s_uri][ $ns['dc'].'identifier' ][] = $o;
	$o = null;
	$o['type'] = 'literal';
	$o['value'] = $s;
	$indexes['labels'][$s_uri][ $ns['sio'].'equivalentTo' ][] = $o;	
*/
	// add dc:identifier
	$o = null;
	$o['value'] = substr($s,strrpos($s,"/")+1);
	$o['type'] = 'literal';
	$index[$s][ $ns['dc'].'identifier' ][] = $o;
}

foreach($indexes AS $subset => $ind) {
	unset($myindex);

	// add the version iri
	unset($index[$sio]['http://www.w3.org/2002/07/owl#versionInfo']);
	//$myindex = ARC2::getMergedIndex($index, $ind);
	$myindex = $ind;
	$myindex[$sio] = $index[$sio];
	
	$sio_versioned_file = "sio-v".$sio_version."-".$subset."-subset.owl";
	$o = null;
	$o['value'] = $sio_versioned_file;
	$o['type'] = 'literal';
	
	$myindex[$sio]['http://www.w3.org/2002/07/owl#versionInfo'][] = $o;
	
	$sio_versioned_uri = "http://semanticscience.org/ontology/sio/".$sio_versioned_file;
	$o['value'] = $sio_versioned_uri;
	$o['type'] = 'uri';
	$myindex[$sio]['http://www.w3.org/2002/07/owl#versionIRI'][] = $o;
	
	// add rdfs:isDefinedBy
	$o = null;
	$o['value'] = $sio_versioned_uri;
	$o['type'] = 'uri';
	$myindex[$sio]['http://www.w3.org/2000/01/rdf-schema#isDefinedBy'][] = $o;
	
	echo "generating $subset".PHP_EOL;
	file_put_contents($odir."sio-subset-$subset.owl",$parser->toRDFXML($myindex));
}

echo "generating versioned SIO".PHP_EOL;
file_put_contents($odir."sio-release.owl", $parser->toRDFXML($index));


