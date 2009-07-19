<?php
require(dirname(__FILE__).'/../include.php');

// ftp://ftp.ncbi.nlm.nih.gov/genomes/genomeprj/gp.xml
$site= "ftp://ftp.ncbi.nlm.nih.gov";
$rdir= "/genomes/genomeprj/";
$ldir= DATA."gp/";
$infile = "gp.xml";
$outdir = DATA."gp/n3/";
$outfile = "gp.n3";

shell_exec("chdir $ldir;wget -N $site$rdir$infile");
if(!file_exists($ldir.$infile)) {
	trigger_error("No file at $ldir$infile");
	exit();
}

echo "RDFizing: NCBI Genome Projects\n";
echo "$ldir$infile to $outdir$outfile\n";
$buf = N3NSHeader($nslist);

$documentset = simplexml_load_file($ldir.$infile);
if($documentset === FALSE) {
	trigger_error("Error in opening $ldir$infile");
	exit;
}
/* 
gp:ProjectID, gp:IsPrivate?, gp:eType, gp:eMetagenomeType?, gp:eMethod, gp:eTechnologies+, gp:OriginDB?, gp:CreateDate?, gp:ModificationDate?, gp:ProjectName?, gp:OrganismName?, gp:StrainName?, gp:TaxID?, gp:LocusTagPrefix?, gp:DNASource?, gp:SequencingDepth?, gp:ProjectURL?, gp:DataURL?, gp:OrganismDescription?, gp:EstimatedGenomeSize?, gp:Consortium, gp:Submitters, gp:Centers, gp:Contacts, gp:ChromosomeDefinitions, gp:SubmittedSequences, gp:LegacyPrefixes)> 
*/

$i = 0;
foreach ($documentset->children('gp') as $d) { 
	//if($i++ == 5) break;
	$o = $d->children('gp');
	$id = $o->ProjectID; 

	$duri = "$gp:record_$id";
	$buf .= "$duri a $ss:Record.".PHP_EOL;
	$buf .= "$duri $rdfs:label \"NCBI Genome Project Record [$duri]\".".PHP_EOL;
 	if(isset($o->CreateDate) && $o->CreateDate != '') 
		$buf .= "$duri $gp:created \"".$o->CreateDate."\" .".PHP_EOL;
	if(isset($o->ModificationDate) && $o->ModificationDate != '' ) 
		$buf .= "$duri $gp:modified \"".$o->ModificationDate."\" .".PHP_EOL;	
	
	$uri = "$gp:$id";
	$buf .= "$uri $dc:identifier \"gp:$id\" .".PHP_EOL;
	$buf .= "$uri $rdfs:label \"".$o->OrganismName." genome project [$gp:$id]\" .".PHP_EOL;
	$buf .= "$uri a $gp:GenomeProject .".PHP_EOL;
	
	if(isset($o->OrganismDescription) && $o->OrganismDescription != '') 
		$buf .= "$uri $rdfs:comment \"".str_replace('"','\"',$o->OrganismDescription)."\" .".PHP_EOL;
	
	if(isset($o->eType) && $o->eType != '') 
		$buf .= "$uri $gp:subject $gp:".substr($o->eType,1)." .".PHP_EOL;
	if($o->eMethod != "eUndefined" && $o->eMethod != '') 
		$buf .= "$uri $gp:method $gp:".$gpns.substr($o->eMethod,1)." .".PHP_EOL;
	if(isset($o->OriginDB) && $o->OriginDB != '') 
		$buf .= "$uri $gp:database \"".$o->OriginDB."\" .".PHP_EOL;
	
	if(isset($o->ProjectName) && $o->ProjectName != '') 
		$buf .= "$uri $gp:title \"".$o->ProjectName."\" .".PHP_EOL;			
	
	// gp:eType,  gp:eMethod, gp:eTechnologies+
	if(isset($o->TaxID) && $o->TaxID != '') {
	  $buf .= "$uri $bio2rdfns:organism $taxon:".$o->TaxID." .".PHP_EOL;
	  if(isset($o->OrganismName) && $o->OrganismName != '') {
		$buf .= "$taxon:".$o->TaxID." rdfs:label \"".$o->OrganismName."\".".PHP_EOL;
	  }
	}
	if(isset($o->ProjectURL) && $o->ProjectURL != '') {
		$url = str_replace(" ","+", $o->ProjectURL); 
		$buf .= "$uri $bio2rdfns:url <$url> .".PHP_EOL;
		$buf .= "<$url> a $ss:HtmlDocument.".PHP_EOL;
	}
	if(isset($o->DataURL) && $o->DataURL != '') {
		$url = str_replace(" ","+", $o->DataURL); 
		$buf .= "$uri $gp:dataUrl <$url> .".PHP_EOL;
		$buf .= "<$url> a $ss:Document.".PHP_EOL;
	}
	// submitters
	foreach($o->Submitters AS $s) {
		foreach($s->children('gp')->Center AS $t) { 
			if(isset($t->CenterName) && $t->CenterName != '')
				$buf .= "$uri $gp:center \"".str_replace(array("'"),array('\"'), $t->CenterName)."\" .".PHP_EOL;
		}
	}
	
	foreach($o->SubmittedSequences AS $s) {
		foreach($s->children('gp')->Sequence AS $t) {
			// clean up accINSDC - can contain xxx:xxx
			$a = explode(":",$t->accINSDC);
			$acc = "$ncbi:".$a[0];
			$buf .= "$uri $bio2rdfns:molecule $acc .".PHP_EOL;
			  
			if(isset($t->accRefSeq) && $t->accRefSeq != '') {
				$acc = "$refseq:".$t->accRefSeq;
				$buf .= "$uri $bio2rdfns:molecule $acc .".PHP_EOL;
			}

			if(isset($t->SeqSize)) {
				$buf .= "$acc $bio2rdfns:size \"$t->SeqSize $t->SzUnit\".".PHP_EOL;
			}
			if(isset($t->ChrType)) {
				$buf .= "$acc a gp:".substr($t->ChrType,1).".".PHP_EOL;
			}
			if(isset($t->ChrName)) {
				$buf .= "$acc dc:title \"$t->ChrName\".".PHP_EOL;
			}
		}
	}
	
	$buf .= "$uri $rdfs:isDefinedBy $duri .".PHP_EOL;
	$buf .= "$duri $dc:subject $uri .".PHP_EOL;
	  
} 
file_put_contents($outdir.$outfile,$buf);

?>