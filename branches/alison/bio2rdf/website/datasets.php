<?php include('header.php');?>
 <script type="text/javascript" language="javascript" src="api/dt/media/js/jquery.js"></script> 
 <script type="text/javascript" language="javascript" src="api/dt/media/js/jquery.dataTables.js"></script> 
 <script type="text/javascript">

var oTable;

function fnFormatDetails ( nTr )
{
	var aData = oTable.fnGetData( nTr );
	var sOut = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
	sOut += '<tr><td>Rendering engine:</td><td>'+aData[1]+' '+aData[4]+'</td></tr>';
	sOut += '<tr><td>Link to source:</td><td>Could provide a link here</td></tr>';
	sOut += '<tr><td>Extra info:</td><td>And any further details here (images etc)</td></tr>';
	sOut += '</table>';

	return sOut;
}
$(document).ready(function() {

 oTable = $('#dataset').dataTable({
 "bJQueryUI": true,
 "iDisplayLength":30,
 "sPaginationType": "full_numbers",
 "aoColumns": [
  /* open   */ { "bSearchable": false, "bSortable":false }
  /* prefix */ null,
  /* title  */  null, 
  /* url    */ { "bSearchable": false }
  ]
 });


	/* Add event listener for opening and closing details
	 * Note that the indicator for showing which row is open is not controlled by DataTables,
	 * rather it is done here
	 */
	$('td img', oTable.fnGetNodes() ).each( function () {
		$(this).click( function () {
			var nTr = this.parentNode.parentNode;
			if ( this.src.match('details_close') )
			{
				/* This row is already open - close it */
				this.src = "images/details_open.png";
				oTable.fnClose( nTr );
			}
			else
			{
				/* Open this row */
				this.src = "images/details_close.png";
				oTable.fnOpen( nTr, fnFormatDetails(nTr), 'details' );
			}
		} );
	} );
} );
} );
</script>
<div id="trans-box">

<h1>Life Science Dataset Registry</h1>
<?php
define("RDFAPI_INCLUDE_DIR", "/opt/software/rdfapi-php/api/");
include(RDFAPI_INCLUDE_DIR . "RdfAPI.php");

$client = ModelFactory::getSparqlClient("http://bio2rdf.semanticscience.org:8007/sparql");

$sparql = '
PREFIX serv: <http://bio2rdf.org/serv:>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?prefix ?title ?description ?url
WHERE { ?x a serv:Dataset ;
 dc:title ?title ;
 serv:namespace_prefix ?prefix .
 OPTIONAL {
  ?x dc:description ?description.
  ?x foaf:homepage ?url. 
 }
}
'; //LIMIT 100';

$query = new ClientQuery();
$query->addDefaultGraph("http://bio2rdf.org/graph/registry");
$query->query($sparql);
$result = $client->query($query,'html');
//echo '<pre>';print_r($result);exit;

echo '<p>'.count($result).' unique datasets merged from >2100 dataset listings from Gene Ontology dbxrefs, UniProt dbxrefs, NCBI dbxrefs, NAR database edition, PathGuide, LSRN.</p>';

echo '<table class="dataset" id="dataset">
<thead><tr><th></th><th>prefix</th><th></th><th>title</title></tr></thead>
<tbody>';
foreach($result AS $i => $r) {
 $even = "even";
 if($i % 2 == 1) $even = "odd";

 $p= $r['?prefix']; $t= $r['?title']; 
 $url = '';if(isset($r['?url']) && $r['?url']) {$u= $r['?url'];$url = $u->GetLabel();}

 if($p->getLabel() == "0") continue;
 echo '<tr>';
 echo '<td class="center"><img src="images/details_open.png"></td>';
 echo '<td>'.$p->getLabel().'</td>';
 if($url) echo '<td>[<a target="_blank" title="Website for '.$t->GetLabel().'" href="'.$url.'">W</a>]</td>';
 else echo '<td></td>';

 echo '<td>'.$t->getLabel().'</td>';
 // if($u) echo '<a target="_blank" title="Website for '.$t->GetLabel().'" href="'.$url.'">'.$t->getLabel().'</a></td>';

echo '
</tr>';
}
echo '</tbody></table>';

?>
<br/>
<br/>
</div>
<?php include('footer.php');?>
