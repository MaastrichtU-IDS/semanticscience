<?php
include(dirname(__FILE__).'/ns.php');
function N3NSHeader($nslist)
{
	$buf = '';
	foreach($nslist AS $a => $b) {
		if(is_numeric($a)) {$prefix=$b;$base_uri="http://bio2rdf.org/$prefix:";}
		else {$prefix=$a;$base_uri=$b;}
		$buf .= "@prefix $prefix: <$base_uri>.".PHP_EOL;
	}
	//$buf .= 'dc:identifier rdfs:subPropertyOf <http://www.openlinksw.com/schemas/virtrdf#label>.'.PHP_EOL;;
	return $buf;
}
?>