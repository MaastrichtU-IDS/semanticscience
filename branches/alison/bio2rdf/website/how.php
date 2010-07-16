<?php include('header.php');?>
<div id="trans-box">
<h1>Syntactic Integration</h1>
<h2>Resource Naming</h2>
<p>Bio2RDF applies a simple and consistent resource naming scheme that facilitates syntactic integration of resources mentioned in different datasets. Bio2RDF resources are identified using both their assigned identifier and the dataset in which the identifier is assigned. The Bio2RDF URI pattern follows the form:</p>

<span class="http-uri">http://bio2rdf.org/<em>prefix</em>:<em>identifier</em></a></span>

<p><em>prefix</em> is a short name (meme) that uniquely identifies the dataset that contains information about resource(s). The <a title="The Life Science Dataset Registry" href="registry.php">Life Science Dataset Registry</a> contains a list of datasets and their prefixes.<br/><br/>
Taken together, the gene identified by the number 15275 in the NCBI Entrez Gene dataset has the following URI:</p>

<span class="http-uri">http://bio2rdf.org/geneid:15275</a></span>


<br/><br/>
<h1>Semantic Integration</h1>
<h2>Describing Resources</h2>
<p>In order to describe a resource, we must make statements about it. In RDF, our statement is a 3-tuple (aka triple) that specifies a relation between a subject and an object.</p>
<h3>Annotations</h3>
 The following shows a triple in which the title is formally associated with the resource.</p>
<span class="http-uri">geneid:15275 dc:title ""</span>

<p>
Each resource should contain the following annotation:
<ol>
<li>dc:title - a human readable title as it appears in the source data.</li>
<li>dc:identifier - a string that contains the identifier using the following pattern -
<em>prefix</em>:<em>identifier</em></li>
<li>rdfs:label - A Bio2RDF generated label containing a title followed by the identifier - title [<em>prefix</em>:<em>identifier</em>].</li>
</ol>
</p>

<h3>Types</h3>
<p>Semantic integration is facilitated by ensuring that every instance is an instance of a type defined or documented by the dataset.</p>
<span class="http-uri">geneid:15275 rdf:type geneid_resource:Gene</span>

<p>Note that when the RDFization process creates new types or identifiers, we place them in a new namespace using the prefix + '_resource'. In addition to this dataset-specific typing information, we create a semantic mapping to the <a href="http://semanticscience.org/ontology/sio.owl">Semanticscience Integrated Ontology (SIO)</a>. Thus, we can use this type to group together entities from different datasets. Request for new types can be submitted to the Google Code project <a href="http://semanticscience.googlecode.com">issues</a></p>

<span class="http-uri">geneid_resource:Gene rdfs:subClassOf sio:XXXXX</span>


<h3>Object Relations</h3>
<p>relations between the entities are established in the dataset that defines it, therefore if the above statement came from the Entrez Gene dataset, we would say:</p>
 
 <span class="http-uri">geneid:15275 geneid_resource:encodes refseq:XXXXX</span>
 
<h3>Literals</h3>
<p>In addition to relations between objects, we also consider relations between objects and literals. A typical case might be:</p>
 <span class="http-uri">refseq:15275 refseq_resource:molecular_weight "XXX"^^xsd:decimal</span>
 
 <p>While the literal provides a value for the molecular weight of the protein, it precludes us saying anything more about it e.g.how it was determined, what units the value was measured against or error associated with a calculated/observed value. Bio2RDF now strives to represent these in the following manner:</p>

 <span class="http-uri">
refseq:15275 refseq_resource:property refseq_resource:15275_mw<br/>
refseq_resource:15275_mw rdf:type refseq_resource:Molecular_Weight<br/>
refseq_resource:15275_mw refseq_resource:has_value "XXX"^^xsd:decimal
</span>


<br/><br/>
<h2>Provenance</h2>
<h3>Records</h3>
<p>Records are documents that contain information (e.g. collection of facts) about some resource. However, as the product of some data management process, records are themselves described - for instance, we collect information about when the record was created, modified or deleted. Thus, as of April 1, 2010, Bio2RDF will distinguish records from the entities they describe. Records identifiers are constructed in the following fashion, by appending '_record' to the dataset prefix:</p>
<span class="http-uri">http://bio2rdf.org/<em>prefix</em>_record:<em>identifier</em></a></span>

<p>Thus, the record for the gene identified by 15275 will have the following identifier:</p>
<span class="http-uri">http://bio2rdf.org/geneid_record:15275</a></span>

<p>We can also capture that the resource is the subject of the record:</p>

 <span class="http-uri">geneid_record:15275 sio:XXXXXX geneid:15275</span>
 
 <p>and the parthood relation between the record and the dataset it belongs to:</p>
 
 <span class="http-uri">geneid_record:15275 sio:XXXXXXX registry:geneid</span>

 
<h3>Records as Named Graphs</h3>
<p>Bio2RDF creates named graphs out of the record URIs to maintain the provenance of statements. This can be done by either i) Trig, ii) n-quads, iii) specifying the graph for each set of triples loaded, depending on the level of support by the triple store. </p>




</div>
<?php include('footer.php');?>
