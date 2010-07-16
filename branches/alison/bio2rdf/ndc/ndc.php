<?php
// documentation: http://www.fda.gov/Drugs/InformationOnDrugs/ucm142454.htm
// example: http://www.accessdata.fda.gov/scripts/cder/ndc/getlblcode.cfm

$remote_file = 'http://www.fda.gov/downloads/Drugs/DevelopmentApprovalProcess/UCM070838.zip';

$ldir = '/opt/data/ndc/';
$n3file = 'ndc.n3';
$out = fopen($ldir."n3/".$n3file,"w");
if(FALSE === $out) {
  trigger_error("unable to open $ldir$n3file");
  exit;
}
fwrite($out,"@prefix dc: <http://purl.org/dc/terms/>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix ndc_nda: <http://bio2rdf.org/ndc_nda:>.
@prefix ndc_doseform: <http://bio2rdf.org/ndc_doseform:>.
@prefix ndc_firm: <http://bio2rdf.org/ndc_firm:>.
@prefix ndc_listing: <http://bio2rdf.org/ndc_listing:>.
@prefix ndc_formulation: <http://bio2rdf.org/ndc_fomulation:>.
@prefix ndc_package: <http://bio2rdf.org/ndc_package:>.
@prefix ndc_product: <http://bio2rdf.org/ndc_product:>.
@prefix ndc_facility: <http://bio2rdf.org/ndc_facility:>.
@prefix ndc_route: <http://bio2rdf.org/ndc_route:>.
@prefix ndc_schedule: <http://bio2rdf.org/ndc_schedule:>.
@prefix ndc_dosage: <http://bio2rdf.org/ndc_dosage:>.
@prefix ndc_unit: <http://bio2rdf.org/ndc_unit:>.

@prefix ndc_resource: <http://bio2rdf.org/ndc_resource:>.
");


$files = array( 
 "applicat.txt" => "nda",
 "doseform.TXT" => "dosageform",
 "FIRMS.TXT" => "firms",
 "FORMULAT.TXT" => "formulation",
 "listings.TXT" => "listing",
 "packages.txt" => "package",
 "REG_SITES.TXT" => "facility",
 "ROUTES.TXT" => "routes",
 "SCHEDULE.TXT" => "schedule",
 "TBLdosag.TXT" => "tbldosage",
 "TBLROUTE.TXT" => "tblroute",
 "TBLUNIT.TXT" => "tblunit",
);




foreach($files AS $file => $fnx) {
  $in = fopen($ldir.$file,"r");
  if(FALSE === $in) {
	trigger_error("Unable to open $file");
        return 1;
  }
  if(function_exists($fnx)) $fnx($in,$out);
  fclose($in);
}
fclose($out);


function GetValue($string,$start,$end)
{
  return trim(substr($string,$start-1, $end-$start+1));
}

/*
New Drug Application Data

LISTING_SEQ_NO NOT NULL NUM(7) COL:1-7
Linking field to LISTINGS.

APPL_NO NULL CHAR(6) COL:9-14
Number of New Drug Application if applicable. If none has been provided by the firm then the value ‘Other’ is used.

PROD_NO NULL CHAR(3) COL:16-18
Number used to identify the products of a New Drug Application

168     018780 001
*/
function nda(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   $listing_id = GetValue($l,1,7);
   $nda_id = GetValue($l,9,14);
   $prod_id = GetValue($l,16,18);

   if($nda_id == "Other") continue; 
   $id = "ndc_nda:$nda_id";
   $n3 .= "$id rdfs:label \"New Drug Application #$nda_id [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:NewDrugApplication .".PHP_EOL;
   if($prod_id != "UNK") $n3 .= "ndc_nda:$listing_id ndc_resource:product ndc_product:$prod_id.".PHP_EOL;

   $n3 .= "ndc_listing:$listing_id ndc_resource:new_drug_application $id.".PHP_EOL;
   $n3 .= "$id ndc_resource:listing ndc_listing:$listing_id.".PHP_EOL;
  }
  fwrite($out,$n3);
}


/*
LISTING_SEQ_NO NOT NULL NUM(7) COL:1-7
Linking field to LISTINGS.

DOSEFORM NULL CHAR(3) COL:9-11
The code for the route of administration. File will allow all assigned values for this element.

DOSAGE_NAME NULL CHAR(240) COL:13-252
The translation for the route of administration code.

25097   610 CAPSULE, EXTENDED RELEASE
*/
function dosageform(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) == 0) continue;
   $listing_id = GetValue($l,1,7);
   $doseform_id = GetValue($l,9,11);
   $dosage_name = GetValue($l,13,252);

   $id = "ndc_doseform:$doseform_id";
   $n3 .= "$id rdfs:label \"$dosage_name [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Dosage .".PHP_EOL;
   $n3 .= "$id ndc_resource:dosage_name \"$dosage_name\".".PHP_EOL;
   $n3 .= "ndc_listing:$listing_id ndc_resource:doseform $id.".PHP_EOL;
   $n3 .= "$id ndc_resource:listing ndc_listing:$listing_id .".PHP_EOL;
   
  }
  fwrite($out,$n3);
}


/*
EACH FIRM HAS A UNIQUE FIRM SEQ NO WHICH CAN OCCUR MULTIPLE TIMES IN THE LISTINGS FILE.
Contains the firm's full name, and compliance address. The compliance address is the mailing address where the FDA sends listing information to the firm.
LBLCODE  NOT NULL NUM(6) COL:1-6
FDA generated identification number for each firm. The number is padded to the left with zeroes to fill out to length 6.
FIRM_NAME NOT NULL CHAR(65) COL:8-72
Firm name as reported by the firm.
ADDR_HEADER NULL CHAR(40) COL:74-113
Address Heading as reported by the firm.
STREET NULL CHAR(40) COL:115-154
Street Address as reported by firm.
PO_BOX NULL CHAR(9) COL:156-164
Post office box number as reported by firm.
FOREIGN_ADDR NULL CHAR(40) COL:166-205
Address information report by firm for foreign countries that does not fit the U.S. Postal service configuration.
CITY NULL CHAR(30) COL:207-236
STATE NULL CHAR(2) COL:238-239
ZIP NULL CHAR(9) COL:241-249
USPS Zip code.
PROVINCE NULL CHAR(30) COL:251-280
Province of Foreign country if appropriate.
COUNTRY_NAME NOT NULL CHAR(40) COL:282-321
*/
function firms(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   $firm_id = GetValue($l,1,6);
   $firm_name = GetValue($l,8,72);
   $addr_hdr = GetValue($l,74,113);
   $st = GetValue($l,115,154);
   $po_box = GetValue($l,156,164);
   $foreign = GetValue($l,166,205);
   $city = GetValue($l,207,236);
   $state = GetValue($l,238,239);
   $zip = GetValue($l,241,249);
   $province = GetValue($l,251,280);
   $country = GetValue($l,282,321);

   $id = "ndc_firm:$firm_id";
   $n3 .= "$id rdfs:label \"$firm_name [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Firm.".PHP_EOL;
   $n3 .= "$id ndc_resource:firm_name \"$firm_name\".".PHP_EOL;
   if($addr_hdr) $n3 .= "$id ndc_resource:address_header \"$addr_hdr\".".PHP_EOL;
   if($st)       $n3 .= "$id ndc_resource:street \"$st\".".PHP_EOL;
   if($po_box)   $n3 .= "$id ndc_resource:po_box \"$po_box\".".PHP_EOL;
   if($foreign)  $n3 .= "$id ndc_resource:foreign_address \"$foreign\".".PHP_EOL;
   if($city)     $n3 .= "$id ndc_resource:city \"$city\".".PHP_EOL;
   if($state)    $n3 .= "$id ndc_resource:state \"$state\".".PHP_EOL;
   if($zip)      $n3 .= "$id ndc_resource:zip \"$zip\".".PHP_EOL;
   if($province) $n3 .= "$id ndc_resource:province \"$province\".".PHP_EOL;
   if($country)  $n3 .= "$id ndc_resource:country \"$country\".".PHP_EOL;
  }
  fwrite($out,$n3);
}


/*
MAY OCCUR MULTIPLE TIMES PER LISTING SEQ NO.
Lists active ingredients contained in product's formulation.

LISTING_SEQ_NO NOT NULL NUM(7) COL: 1-7
Linking field to LISTINGS.

STRENGTH NULL CHAR(10) COL: 9-18
This is the potency of the active ingredient.

UNIT NULL CHAR(5) COL: 20-24
Unit of measure corresponding to strength.

INGREDIENT_NAME NOT NULL CHAR(100) COL: 26-125
Truncated preferred term for the active ingredient.

*/
function formulation(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) == 0) continue;
   $listing_id = GetValue($l,1,7);
   $strength = GetValue($l,9,18);
   $unit = GetValue($l,20,24);
   $ingredient = GetValue($l,26,125);

   $id = "ndc_formulation:".md5($l);
   $n3 .= "$id rdfs:label \"formulation [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Formulation .".PHP_EOL;
   $n3 .= "$id ndc_resource:strength \"$strength\".".PHP_EOL;
   $n3 .= "$id ndc_resource:unit \"$unit\".".PHP_EOL;
   $n3 .= "$id ndc_resource:ingredient \"$ingredient\".".PHP_EOL;
   $n3 .= "ndc_listing:$listing_id ndc_resource:formulation $id.".PHP_EOL;
   $n3 .= "$id ndc_resource:listing ndc_listing:$listing_id .".PHP_EOL;

  }
  fwrite($out,$n3);

}


/*
EACH PRODUCT HAS A UNIQUE LISTING SEQ NO; EACH FIRM SEQ NO CAN HAVE MULTIPLE LISTING SEQ NO'S. Each line in this file represents a product for an individual firm. The listing includes such information as the product's name, firm's seq number, dose form(s), and Rx/OTC.

LISTING_SEQ_NO   NOT NULL   NUM(7)  COL: 1-7
FDA generated unique identification number for each product.

LBLCODE          NOT NULL   CHAR(6) COL: 9-14
Labeler code portion of NDC; assigned by FDA to firm. The labeler code is the first segment of the National Drug Code. While always displayed as 6 digits in this file; for labeler codes 2 through 9999, some systems display it as 4 digits; for labeler codes 10,000 through 99,999 it is 5 digits.  Can be used to link to the FIRMS.TXT file to obtain firm name.

PRODCODE NOT NULL CHAR(4) COL: 16-19
Product code assigned by firm. The prodcode is the second segment of the National Drug Code. 
It may be a 3-digit or 4-digit code depending upon the NDC configuration selected by the firm.

STRENGTH NULL CHAR(10) COL: 21-30
For single entity products, this is the potency of the active ingredient. For combination products, it may be null or a number or combination of numbers, e.g., Inderide 40/25.

UNIT NULL CHAR(10) COL: 32-41
Unit of measure corresponding to strength. This non-mandatory field contains the unit code for a single entity product, e.g., MG, %VV.

RX_OTC NOT NULL CHAR(1) COL: 43
Indicates whether product is labeled for Rx or OTC use (R/O).

TRADENAME NOT NULL CHAR(100) COL: 45-144
Product's name as it appears on the labeling.
*/
function listing(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) == 0) continue;
   $listing_id = GetValue($l,1,7);
   $firm_id = GetValue($l,9,14);
   $product_id = GetValue($l,16,19);
   if($product_id[0] == "*") $product_id = substr($product_id,1);
   $strength = GetValue($l,21,30);
   $unit = GetValue($l,32,41);
   $rx_otc = GetValue($l,43,43);
   $tradename = GetValue($l,45,144);

   $id = "ndc_listing:$listing_id";
   $n3 .= "$id rdfs:label \"NDC listing [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Listing .".PHP_EOL;
   $n3 .= "$id ndc_resource:firm ndc_firm:$firm_id.".PHP_EOL;
   $n3 .= "$id ndc_resource:product ndc_product:$product_id.".PHP_EOL;
   $n3 .= "$id ndc_resource:strength \"$strength\".".PHP_EOL;
   $n3 .= "$id ndc_resource:unit \"$unit\".".PHP_EOL;
   $n3 .= "$id ndc_resource:tradename \"$tradename\".".PHP_EOL;
   $n3 .= "$id ndc_resource:used_by \"".($rx_otc=="R"?"Rx":"OTC")."\".".PHP_EOL;

 }
  fwrite($out,$n3);

}


/*
PACKAGE 

MAY OCCUR MULTIPLE TIMES PER LISTING SEQ NO
Stores packages for an individual listing. The packages table includes all packages for a corresponding listing. The PKGCODE field contains the last one or two digit segment of the NDC.

LISTING_SEQ_NO NOT NULL NUM(7) COL: 1-7
Linking field to LISTINGS.

PKGCODE NULL CHAR(2) COL: 9-10
The package code portion of NDC code. The package code is the last segment of the NDC.

PACKSIZE NOT NULL CHAR(25) COL: 12-36
The unit or number of units which make up a package.

PACKTYPE NOT NULL CHAR(25) COL: 38-62
Package type, i.e., box, bottle, vial, plastic, or glass.

*/
function package(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) == 0) continue;
   $listing_id = GetValue($l,1,7);
   $pkg_id = GetValue($l,9,10);
   if(strstr($pkg_id,"**")) $pkg_id = md5("package_for_".$listing);
   else if($pkg_id[0] == "*") $pkg_id = substr($pkg_id,1);
   $pack_size = addslashes(GetValue($l,12,36));
   $pack_type = GetValue($l,38,62);

   $id = "ndc_package:".$listing_id."_".$pkg_id;
   $n3 .= "$id rdfs:label \"NDC package #$pkg_id for listing #$listing_id [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Package .".PHP_EOL;
   $n3 .= "$id ndc_resource:package_size \"$pack_size\".".PHP_EOL;
   $n3 .= "$id ndc_resource:pack_type \"$pack_type\".".PHP_EOL;
   $n3 .= "ndc_listing:$listing_id ndc_resource:package $id.".PHP_EOL;
  }
  fwrite($out,$n3);
}


/*

This file contains a list of all currently active and registered domestic manufacturing facilities. 
UNLIKE THE FILES ABOVE, IT IS A TAB DELIMITED FILE, WITH THE FIRST LINE CONTAINING THE COLUMN HEADERS. The data elements are:

FEI: Unique ID number
LAST_REG_YEAR: Last year the annual registration obligation was fulfilled.  Some older, inactive sites may be on the list.  The records need to be updated by the firm and/or FDA.
NAME: Registered firm name
STREET: street address
CITY: name of city
STATE:  name of state
ISO_COUNTRY_CODE: identifies the country. Currently only U.S. sites are included.
COUNTRY_NAME: translation of country code.
*/

function facility(&$in,&$out)
{
 $n3 = '';
 fgets($in);
 while ($l = fgets($in)) {
  $a = explode("\t",trim($l));
  
  $id = "ndc_facility:$a[0]";
  $n3 .= "$id rdfs:label \"$a[2] [$id]\".".PHP_EOL;
  $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
  $n3 .= "$id a ndc_resource:Facility .".PHP_EOL;
  $n3 .= "$id ndc_resource:current_registration_year \"$a[1]\".".PHP_EOL;
  $n3 .= "$id ndc_resource:name \"$a[2]\" .".PHP_EOL;
  $n3 .= "$id ndc_resource:street \"$a[3]\" .".PHP_EOL;
  $n3 .= "$id ndc_resource:city \"$a[4]\" .".PHP_EOL;
  $n3 .= "$id ndc_resource:state \"$a[5]\" .".PHP_EOL;
  $n3 .= "$id ndc_resource:iso_country_code \"$a[6]\" .".PHP_EOL;
  $n3 .= "$id ndc_resource:country \"$a[7]\" .".PHP_EOL;
 }
 fwrite($out,$n3);
}


/*
LISTING_SEQ_NO NOT NULL NUM(7) COL:1-7
Linking field to LISTINGS.

ROUTE_CODE NULL CHAR(3) COL:9-11
The code for the route of administration. File will allow all assigned values for this element.

ROUTE_NAME NULL CHAR(240) COL:13-252
The translation for the route of administration code.

*/
function routes(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) == 0) continue;
   $listing_id = GetValue($l,1,7);
   $route_id = GetValue($l,9,11);
   $route_name = GetValue($l,13,252);

   $id = "ndc_route:$route_id";
   $n3 .= "$id rdfs:label \"NDC route $route_name [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Route .".PHP_EOL;
   $n3 .= "$id ndc_resource:route_name \"$route_name\".".PHP_EOL;
   $n3 .= "$id ndc_resource:listing ndc_listing:$listing_id.".PHP_EOL;
   $n3 .= "ndc_listing:$listing_id ndc_resource:route $id.".PHP_EOL;
 }
 fwrite($out,$n3);
}

/*
This file identifies those listed products in the directory which have a DEA schedule designation.
LISTING_SEQ_NO NOT NULL NUM(7) COL:1-7 Linking field to LISTINGS.
SCHEDULE NOT NULL NUM(1) COL:9
*/
function schedule(&$in,&$out)
{
 $n3 = '';
  while($l = fgets($in)) {
   $listing_id = GetValue($l,1,7);
   $schedule_id = GetValue($l,9,9);

   $id = "ndc_schedule:$schedule_id";
   $n3 .= "$id rdfs:label \"DEA schedule #$schedule_id for listing #$listing_id [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:DEASchedule .".PHP_EOL;
   $n3 .= "$id ndc_resource:listing ndc_listing:$listing_id.".PHP_EOL;
   $n3 .= "ndc_listing:$listing_id ndc_resource:schedule $id.".PHP_EOL;
 }
 fwrite($out,$n3);
}

/*
THIS FILE CONTAINS A COMPLETE LIST OF THE DOSAGEFORM CODES USED IN THE DIRECTORY
DOSEFORM CHAR(3) COL:1-3
The code for the dosage form.
 
TRANSLATION CHAR(100) COL:5-104
The translation for the DOSAGE FORM 
*/
function tbldosage(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   $dosage_id = GetValue($l,1,3);
   $dosage_name = GetValue($l,5,104);

   $id = "ndc_dosage:$dosage_id";
   $n3 .= "$id rdfs:label \"$dosage_name [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Dosage .".PHP_EOL;
 }
 fwrite($out,$n3);
}


/*
THIS FILE CONTAINS A COMPLETE LIST OF THE ROUTE CODES USED IN THE DIRECTORY
ROUTE CHAR(3) COL:1-3
The code for the ROUTE OF ADMINISTRATION.
 
TRANSLATION CHAR(100) COL:5-104
The translation for the ROUTE code.
*/
function tblroute(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   $route_id = GetValue($l,1,3);
   $route_name = strtolower(GetValue($l,5,104));

   $id = "ndc_route:$route_id";
   $n3 .= "$id rdfs:label \"$route_name [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Route .".PHP_EOL;
 }
 fwrite($out,$n3);
}



/*
THIS FILE CONTAINS A COMPLETE LIST OF THE POTENCY UNIT ABBREVIATIONS USED IN THE DIRECTORY.
 
UNIT CHAR(15) COL:1-15
The potency unit abbreviations used in the directory.
 
TRANSLATION CHAR(100) COL:17-115
The translation for the UNIT abbreviat
*/
function tblunit(&$in,&$out)
{
  $n3 = '';
  while($l = fgets($in)) {
   if(strlen($l) <= 1) continue;
   $unit_code = GetValue($l,1,15);
   $unit_name = strtolower(GetValue($l,17,115));

   $id = "ndc_unit:".md5($unit_code);
   $n3 .= "$id rdfs:label \"$unit_name ($unit_code) [$id]\".".PHP_EOL;
   $n3 .= "$id dc:identifier \"$id\".".PHP_EOL;
   $n3 .= "$id a ndc_resource:Unit .".PHP_EOL;
   $n3 .= "$id ndc_resource:unit_label \"$unit_code\".".PHP_EOL;
   $n3 .= "$id ndc_resource:unit_name \"$unit_name\".".PHP_EOL;
 }
 fwrite($out,$n3);
}
