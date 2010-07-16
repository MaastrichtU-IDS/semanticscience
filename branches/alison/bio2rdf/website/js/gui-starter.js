
function getSuggestBox(){
        var sugBox = {
                'box-shadow' : '#888 5px 10px 10px',
                '-webkit-box-shadow' : '#888 5px 10px 10px', // Safari
                '-moz-box-shadow' : '#888 5px 10px 10px'
        };
        return sugBox;
}//getSuggestBox

function lookup(inputString){

	if(inputString.length == 0){
	        $("#suggestions").fadeOut();
        }//if
	else if(inputString.length < 2){
                $("#suggestions").fadeOut();
        }else{
		nsRegExp = /^(\S+):(.*)$/;
        	matches = nsRegExp.exec(inputString);
		if (matches != null){
			if(matches[1].length >= 2 && matches[2].length > 2){
				namespace = matches[1];
				//alert("http://bio2rdf.org/"+matches[1]+":"+matches[2]);
				//window.location = "http://bio2rdf.org/"+matches[1]+":"+matches[2];

				/*$.post("bin/searcher.php",{queryNs: ""+namespace+""}, function(data){
                                        $("#suggestions").fadeIn();
                                        $("#suggestions").html(data);
                                });*/

			}//if
			if(matches[1].length >= 2 && matches[2].length >= 2){
                                namespace = matches[1];
                                searchTerm = matches[2];
                                //alert("NS:"+namespace+" searchTerm:"+searchTerm);
                        }//if
		}//if
		else if(matches == null){
			 $.post("bin/searcher.php", {queryString: ""+inputString+""}, function(data){
                                        $("#suggestions").fadeIn();
                                        $("#suggestions").html(data);
                        });
		}	
	}//else

}//lookup

