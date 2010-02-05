<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" 
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
 <title>Bio2RDF - Linked Data for the Life Sciences</title>
 <meta content="text/html; charset=UTF-8" http-equiv="content-type" /> 
 <link rel="stylesheet" href="css/main.css" type="text/css" /> 
 <link type="image/png" href="images/favicon.ico" rel="shortcut icon" />
 <!--adding js-->
 <script src="http://code.jquery.com/jquery-latest.js"></script>
 <script type="text/javascript">
// Safely inject CSS3 and give the search results a shadow
$(document).ready(function(){
 var cssObj = { 
        'box-shadow' : '#888 5px 10px 10px',
        '-webkit-box-shadow' : '#888 5px 10px 10px', // Safari
        '-moz-box-shadow' : '#888 5px 10px 10px'
        };
 $("#suggestions").css(cssObj);
 //Fade out the suggestions when not active
 $("input").blur(function(){
        $("#suggestions").fadeOut();
 });
}); 

function lookup(inputString){
        if(inputString.length == 0){
                $("#suggestions").fadeOut();
        }else{
                $.post("bin/searcher.php", {queryString: ""+inputString+""}, function(data){
                        $("#suggestions").fadeIn();
                        $("#suggestions").html(data);
                });
        }
}//lookup
 </script>


</head>
<body>
 <div id="content">
  <div class="logo">
    <img title="Bio2RDF - Linked Data for the Life Sciences" src="images/bio2rdf-logo.gif" width="100%"/>
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
		
   <br><br><a title="Creative Commons - By Attribution - Share-Alike" rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/ca/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/2.5/ca/80x15.png" /></a>
 </div>
</div>
<div id="footer"></div>
 
</body>
</html>
