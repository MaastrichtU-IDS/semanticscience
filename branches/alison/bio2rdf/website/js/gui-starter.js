function getSuggestBox(){
        var sugBox = {
                'box-shadow' : '#888 5px 10px 10px',
                '-webkit-box-shadow' : '#888 5px 10px 10px', // Safari
                '-moz-box-shadow' : '#888 5px 10px 10px'
        };
        return sugBox;
}//getSuggestBox

function searchIndex(str){
	if(str.length == 0){
		$("#suggestions").fadeOut();
    }//if
	else if(str.length <= 2){
		$("#suggestions").fadeOut();
	}//else if
	else{
		myRegEx = /^([A-Za-z0-9]+):([A-Za-z0-9\s\-]+)$/; 
		matches = myRegEx.exec(str);
		if (matches != null){
			if(matches[1].length >= 2 && matches[2].length >= 2){
				var namespace = matches[1];
				var searchString = matches[2];
				$.get("bin/servletcall.php", {query:searchString, ns:namespace}, function(data){
					parseXML(data, searchString);
				});//get
			}//if	
		}else{
			mySecondRegEx = /^[A-Za-z0-9\-\s]+$/;
			matches2 = mySecondRegEx.exec(str);
			if(matches2 != null){
				var searchStr = matches2[0];
				if(searchStr.length > 1){
					 $.get("bin/servletcall.php", {query:searchStr}, function(data){
						parseXML(data, searchStr);
					});//get
				}//if
			}//if
			else{
				return false;
			}//else
		}//else
	}//else	
}//searchIndex

function parseXML(xml, str){
	
	var table = "<table class=\"search_table\">";
	table += "<thead>";
	table += "<tr><th colspan=\"2\">Limit the search to a specific dataset using its prefix like this: <i>prefix:query</i>.</th></tr>";
	table += "</thead>";
	table += "<tbody>";
	$(xml).find("result").each(function(){
		var uri = $(this).find("uri").text();
		var name = $(this).find("name").text();
		var type = $(this).find("type").text();
		var def = $(this).find("definition").text();
		table += "<tr><td class=\"searchResult\" url=\""+uri+"\"><span class=\"resourceName\"><strong>"+name+"</strong></span><br/><span class=\"resourceType\"><i>Type</i>: "+type+"</span><br/>";
		if(def.length >110){
			var defWords = def.split(" ",18);
			var defStr = "";
			$.each(defWords,function(i,val){
				defStr += val+" ";
			});
			defStr += "...";
			table += "<span class=\"resourceDef\"><i>Definition</i>: "+defStr+"</span></td></tr>";
		}else{
			table += "<span class=\"resourceDef\"><i>Definition</i>: "+def+"</span></td></tr>";
		}//else
	});//each
	//table += "<tr><th colspan=2>Hits by dataset</th></tr>";
	table += "<tr><th colspan=\"2\">Click on a dataset to limit your search.</th></tr>";
	$(xml).find("nsHit").each(function(){
		var ns = $(this).find("ns").text();
		var count = $(this).find("count").text();
		prefixRegEx = /.*\[(\w+)\]/;//fixed -- problem was there is a space at end of ns, so regex can't look for this pattern at END of line
		matches = prefixRegEx.exec(ns);
		table += "<tr><td class=\"datasetResult\" ns=\""+matches[1]+"\"><span class=\"datasetName\"><span class=\"nsCount\">"+count+" </span> in <strong>  "+ns+"</strong></span>";
		table += "</td></tr>";
	});
	table += "<tr><th colspan=2>Didn't find what you were looking for? <a href=\"http://www.google.ca\" >Click here</a></th></tr>";
	table += "</tbody>";
	table += "</table>";
	$("#suggestions").fadeIn();
	$("#suggestions").html(table);
	//initialize tablehover plugin
	$(".search_table").tableHover();
	//listen for row hovering
	rowClickListener();
	/**
	//navigate table
	$.getScript('js/jquery.table_navigation.js',function(){
		jQuery.tableNavigation({
			table_selector: 'table.search_table',
			row_selector: 'table.search_table tbody tr',
			bind_key_events_to_links: false,
			on_activate:function(row){
				var l = jQuery("td.searchResult",row).attr("url");
				window.location = l;
				return false;
			}
		});
	});
	**/
}//parseUnlimitedXML

function rowClickListener(){
	$("td.searchResult").click(function(){
		var x = $(this).attr("url");
		window.location = x;
	});	
	$("td.datasetResult").click(function(){
		var ns = $(this).attr("ns");
		var val = $("#input").val();

		myRegEx = /^([A-Za-z0-9\s]+)$/; 
		matches = myRegEx.exec(val);
		if(matches == null){
			$("#suggestions").fadeOut();
		}else if(matches[1] != null){
			$("#input").val(ns+":"+val);		
			$("#suggestions").fadeOut();
			searchIndex(ns+":"+val);
		}else if(matches[1] == null){
			$("#suggestions").fadeOut();
		}else {
			return false;
		}//else
	});
}//rowClickListener
