<?php

class SGD_PRONTO_GOSLIM {

	function __construct($infile, $outfile)
	{
		$this->_in = fopen($infile,"r");
		if(!isset($this->_in)) {
			trigger_error("Unable to open $infile");
			return 1;
		}
		$this->_out = fopen($outfile,"w");
		if(!isset($this->_out)) {
			trigger_error("Unable to open $outfile");
			return 1;
		}
		
	}
	function __destruct()
	{
		fclose($this->_in);
		fclose($this->_out);
	}
	function Convert2RDF()
	{
		require ('../include.php');
//		$buf = N3NSHeader($nslist);
$buf = pronto_header();
		$goterms = array(
                        "F" => array("type" => "Function", "p" => "hasFunction", "plabel" => "has function"),
                        "C" => array("type" => "Location", "p" => "isLocatedIn", "plabel" => "is located in"),
                        "P" => array("type" => "Process", "p" => "isParticipantIn", "plabel" => "is participant in")
                );
		
		while($l = fgets($this->_in,2048)) {
			$a = explode("\t",trim($l));
			
			$id = $a[0];
			if($id[0] !== "Y") continue;
			$id = ucfirst(strtolower($id))."p";

			if($a[3] != "C") continue;
			$go = substr($a[5],3);

$buf .= '
    <SubClassOf>
        <Class URI="http://bio2rdf.org/sgd:'.$id.'"/>
        <ObjectSomeValuesFrom>
            <ObjectProperty URI="&protein;isLocatedIn"/>
            <Class URI="http://bio2rdf.org/go:'.$go.'"/>
        </ObjectSomeValuesFrom>
    </SubClassOf>
';
		}
$buf .= pronto_footer();
		fwrite($this->_out, $buf);
		
		return 0;
	}

};


function pronto_header() {
return '
<?xml version="1.0"?>
<!DOCTYPE Ontology [
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY owl2xml "http://www.w3.org/2006/12/owl2-xml#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >    
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <!ENTITY protein "file:/C:/kl/java/pronto/examples/protein/protein.owl#" >
]>        
<Ontology xmlns="http://www.w3.org/2006/12/owl2-xml#"
     xml:base="http://www.w3.org/2006/12/owl2-xml#"    
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"     
     xmlns:owl2xml="http://www.w3.org/2006/12/owl2-xml#"
     xmlns:protein="&protein;"
     xmlns:owl="http://www.w3.org/2002/07/owl#"           
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"      
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     ontologyIRI="file:/C:/kl/java/pronto/examples/protein/protein.owl">
';

}

function pronto_footer() {              
 return '
</Ontology>';
}

?>
