<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" 
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
 <title>Bio2RDF - Linked Data for the Life Sciences</title>
 <meta content="text/html; charset=UTF-8" http-equiv="content-type" /> 
 <link rel="stylesheet" href="css/dataset.css" type="text/css" /> 
 <link rel="stylesheet" href="css/main.css" type="text/css" /> 
 <link type="image/png" href="images/bio2rdf_favicon.ico" rel="shortcut icon" />
 <!--adding js-->
 <script src="http://code.jquery.com/jquery-latest.js"></script>
 <script src="js/gui-starter.js"></script>
 <script type="text/javascript">
// Safely inject CSS3 and give the search results a shadow
$(document).ready(function(){
 $("#suggestions").css(getSuggestBox());
 //Fade out the suggestions when not active
 $("input").blur(function(){
        $("#suggestions").fadeOut();
 });

 $("#search-form").submit(function(){
	var val = $("#input").val();
	if(val.length != 0){
		nsRegExp = /^(\S+):(.*)$/;
        	matches = nsRegExp.exec(val);
		if (matches != null){
			if(matches[1].length >= 2 && matches[2].length > 2){
				window.location = "http://bio2rdf.org/"+val;
				return false;
			}
		}else{
			window.location = "http://bio2rdf.org/search/"+val;
			return false;		
		}
	}	
  });
 
}); 

 </script>


</head>
<body>
 <div id="content">
  <div class="logo">
    <img border="0" title="Bio2RDF - Linked Data for the Life Sciences" src="images/bio2rdf_logo.png" width="100%"/>
    <span id="tagline">Linked Data for the Life Sciences</span>
  </div>

  <div class="search">
   <form id="search-form">
    <div id="inputWrapper">
     <input id="input" type="text" size="35" id="inputString" onkeyup="lookup(this.value);"/>
     <button id="search-button" type="submit" value="GO">GO</button>
     <div id="suggestions"></div>
    </div>
   </form>
  </div>
 </div>

 <div id="links">
  <div class="links">
   [<a title="about" href="about.php">about</a>] 
   [<a title="datasets" href="datasets.php">datasets</a>] 
   [<a title="download" href="download.php">download</a>]
		
   <br><br>
        <a href="http://www.opendefinition.org/"><img border="0" alt="This material is Open Knowledge" src="images/od_80x15_red_green.png" border="0"></a> 
        <a href="http://www.w3.org/RDF/" title="RDF data"><img border="0" src="images/sw-rdf-blue.png" alt="[RDF Data]"></a> 
        <a href="http://www.w3.org/TR/rdf-sparql-query/"><img border="0" alt="W3C Semantic Web Technology" src="images/sw-sparql-blue.png" border="0"></a> 
	<a title="Creative Commons - By Attribution - Share-Alike" rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/ca/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/2.5/ca/80x15.png" /></a>
 </div>
</div>
<div id="footer"></div>
 
</body>
</html>
