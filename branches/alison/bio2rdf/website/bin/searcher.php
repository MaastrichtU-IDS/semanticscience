<?php
include('search_examples.html');
exit;
$str = '<p id="searchresults">';
$str .= '<span class="category">Data</span>';
$str .= '<a href="http://bio2rdf.org/geneid:3098">
 <span class="searchheading">Hexokinase [geneid:3098]</span>
 <span class="searchdef">Hexokinases phosphorylate glucose to produce glucose-6-phosphate, the first step in most glucose metabolism pathways...</span>
 <span class="search_dataset">An entity described in the Entrez Gene dataset published by the NCBI.</span>
</a>';
$str .= '<a href="http://cbc.ca">
        <span class="searchheading">Result Label</span>
        <span>Lorem ipsum doloit. Pellentesque id velit ac sem pulvinar tempor sed egestas augue. Donec imperdiet accumsa
n elementum.</span>
</a>';
$str .= '<a href="http://cnn.com">
        <span class="searchheading">Result label</span>
        <span>Lorem ipsum dolor sit amellentesque id velit ac sem pulvinar tempor sed egestas augue. Donec imperdiet accu
msan elementum.</span>
</a>';
$str .= '<span class="category">Dataset</span>';
$str .= '<a href="http://google.ca">
	<span class="searchheading">Result Label</span>
	<span>Lorem ipsum dolor sit am velit ac sem pulvinar tempor sed egestas augue. Donec imperdiet accumsan elementum
.</span>
</a>';

//$str .='<span class="seperator">
//	<a title="Sitemap" href="http://www.marcofolio.net/sitemap.html">Nothing interesting here? Try the sitemap.</a></
$str .= '</p>';
echo $str;
?>

