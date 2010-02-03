<?php include('header.php');?>
<div id="trans-box">
<h1>Syntactic Integration</h1>
<h2>Entity Naming</h2>
<p>The first step of the syntactic normalization requires a consistent naming scheme so as to syntactically normalize all named resources across the Bio2RDF network. Normalization enables a reproducible mechanism for accessing resources and establishing relations with other resources. Linked data network require HTTP-based resolvable identifiers such that rich descriptions are obtained when looking up the entity by its HTTP URI identifier in your web browser. Bio2RDF identifiers are given by the following URI pattern:</p>

<span class="http-uri">http://bio2rdf.org/&lt;namespace&gt;:&lt;identifier&gt;</a></span>

<p><namespace> is a short name that uniquely identifies the source (dataset/database). The list of namespaces is available through our <a title="The Registry" href="registry.php">registry</a>. <identifier> is the original database identifier. For instance, the gene identified by the number 15275 in the NCBI Gene Database (namespace = geneid) is now has the following identifier:</p>

<span class="http-uri">http://bio2rdf.org/geneid:15275</a></span>
<p>The Bio2RDF URI scheme is not only useful for naming data resources which have been imported into the Bio2RDF network, but also for naming the classes and relations found in the source or Bio2RDF ontologies. For example, the class bio2rdf:Protein has the following name:</p>

<span class="http-uri">http://bio2rdf.org/bio2rdf_resource:Protein</a></span>
<br><br>
<h2>Entity Labels and Descriptions</h2>
<p>
Each resource should contain the following annotation:
<ol>
<li>dc:title - a human readable title as it appears in the source data.</li>
<li>dc:identifier - a string that contains the identifier using the following pattern
<span class="http-uri">&lt;namespace&gt;:&lt;identifier&gt;</span></li>
<li>rdfs:label - A Bio2RDF generated label containing a title followed by the identifier. Used by convention in most RDF browsers to render the name of resource instead of using its URI.</li>
</ol>
</p>
	 
<h1>Semantic Integration</h1>

</div>
<?php include('footer.php');?>
