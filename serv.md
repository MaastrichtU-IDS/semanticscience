# Semantic Entity Resolution Vocabulary #

### November 1, 2009 ###

**Editor:**
> Michel Dumontier - Carleton University

**Authors:**
> Alexander De Leon - Carleton University

> Peter Ansell - Queensland University

> Marc-Alexandre Nolin - Universite de Laval


Copyright © 2009 semanticscience.org

This work is licensed under a [Creative Commons License](http://creativecommons.org/licenses/by/1.0/). This copyright applies to the SERV Specification and accompanying documentation and does not apply to SERV data formats, ontology terms, or technology.

## Introduction ##
The Semantic Web prides itself in being a platform for representing any kind of entity, whether they be classes (e.g. person), relations (e.g. loves) or individuals (e.g. you), and constructing statements to describe them (e.g. `<the moon> <is made of> <cheese>` ). The basic idea of linked data is to use URIs to name things and link them together, and use web technology to obtain documents that contain this information. This is great if you are an original data provider - you can publish documents on your web site that describe entities that you name and offer resolution services for. However, increasing numbers of people also want to make statements about primary data, and we'd also like to discover their documents for the statements contained within. Unfortunately, it's rather hard to find these documents coming out from the original data provider because there is no mechanism to automatically discover reciprocal links nor what they really mean.

To illustrate, let's look at how [Wikipedia](http://www.wikipedia.org) and [DBPedia](http://dbpedia.org) treat the topic "Planet". "Planet" is a topic in Wikipedia, and _is the subject of_ Wikipedia's HTML page [http://en.wikipedia.org/wiki/Planet](http://en.wikipedia.org/wiki/Planet). DBPedia, which obtains its raw data from structured information in Wikipedia articles, actually offers several different types of documents (HTML, RDF/N3, RDF/XML, JSON+RDF). DBPedia's HTML page about Wikipedia's Planet topic can be found at [http://dbpedia.org/resource/Planet](http://dbpedia.org/resource/Planet) and this contains the statement that the entity identified by
[http://dbpedia.org/resource/Planet](http://dbpedia.org/resource/Planet) _is the topic of_ Wikipedia's HTML page [http://en.wikipedia.org/wiki/Planet](http://en.wikipedia.org/wiki/Planet), as specified with FOAF's [foaf:page](http://xmlns.com/foaf/spec/#term_page) relation. However, the network of information is incomplete. What isn't being said is i) that DBPedia's entity is also the topic of DBPedia's document, and ii) DBPedia's entity is the same as the entity referred to in Wikipedia's Document. The problem for ii) is that there is only one source of information for Wikipedia's "Planet" -> the HTML page, and we don't know another URI for Wikipedia's entity that goes by the name "Planet".

While the word "Planet" has many meanings to many people, Wikipedia's article about the topic is clear. It would be useful to have a unique identifier for Wikipedia's Planet topic. Since Wikipedia isn't generating URIs for its concepts, we might use something like "wikipedia:Planet". This works because the word "Planet" is unique in Wikipedia and "wikipedia" can be recognized as a globally unique **namespace** for Wikepedia topics. By building a registry around these dataset identifiers and entity identifiers, we could automatically generate links to a data provisioner's documents using some URI pattern that they specify. In this way, original and third data providers could register their entity resolution capability with the types of documents they provide (eg HTML, RDF/N3, RDF/XML). This then can act as a linked data bridge for documents the entities they contain information about.

## Objective ##
The purpose of the Semantic Entity Resolution Vocabulary (SERV) is to facilitate the representation of entities contained in namespace-identified datasets, which are specifically the subject of documents which can be automatically constructed from URL patterns involving the entity identifier, and optionally the namespace.


## SERV at a glance ##


prefix dc: <http://purl.org/dc/terms/>

prefix serv: <http://semanticscience.org/serv:>

prefix foaf: <http://xmlns.com/foaf/0.1/>

prefix skos: <http://www.w3.org/2004/02/skos/core>

prefix sioc: <http://rdfs.org/sioc/ns#>




![http://semanticscience.googlecode.com/svn/trunk/wiki/serv_overview_diagram.png](http://semanticscience.googlecode.com/svn/trunk/wiki/serv_overview_diagram.png)




## Ontology ##
[SERV OWL Ontology](http://semanticscience.org/ontology/serv.owl) - updated [all predicates defined](not.md)

## Example ##





### serv:Entity ###
An entity is something that is identified (by name or otherwise).
```
 serv:Entity
  rdfs:subClassOf [sioc:Item]
  rdfs:label [string]                     # title [ns:id]
  dc:title [string]                       # title
  dc:identifier [string]                  # ns:id

  #optional
  serv:identifiedBy [serv:Identifier]     # relation between the entity and its identifier
```

### serv:Information ###
Information is an entity that is composed of data that can be meaningfully
interpreted/communicated (semantics) and whose syntax conforms to that
specified by an information system.

### serv:ICE ###
An Information content entity (ICE) is an entity that contains information
(e.g. meaningful data) about another entity and has at least one physical
manifestation (e.g. digital media, pixels on screen, ink on paper, neural patterns).

### serv:Agent ###
An agent is an entity capable of executing some task. Agents include people, organizations, systems, software.
```
 serv:Agent
  rdfs:subClassOf [serv:Entity]
  owl:equivalentClass [foaf:Agent] 

  rdfs:label [string]          # title [ns:id]
  dc:identifier [string]       # ns:id

  #optional
  foaf:name [string]           # the agent's name [e.g. Bio2RDF]
  foaf:mbox [string]           # the agent's email address for contact/notification
  foaf:homepage [url]          # the agent's homepage [e.g. http://bio2rdf.org]                                         
```


### serv:Namespace ###
A namespace is an information content entity composed of a set of symbols or identifiers.
```
 serv:Namespace
  rdfs:subClassOf [serv:ICE]
    owl:equivalentClass [sioc:Container] 

  rdfs:label [string]                     # title [ns:id]
  dc:identifier [string]                  # ns:id
  serv:value [string]                     # ns [e.g. 'kegg']

  #optional
  dc:replaces [serv:Namespace]            # for superceding namespaces [e.g. registry_namespace:kegg replaces nar_namespace:kegg]
  skos:narrower [serv:Namespace]          # for aggregation namespaces [e.g. kegg 'has narrower' kegg_ligand]
  serv:references [serv:Namespace]        # to indicate that at least one direct relation exists between namespaces
  serv:dataset [serv:Dataset]             # the dataset to which this namespace applies [e.g. registry_dataset:kegg]
  dc:source [foaf:Agent]                  # the source/publisher of the namespace [e.g. Registry, NAR, GO]
```
```
 serv:RegistryNamespace                  # to denote an *official* registry namespace
  rdfs:subClassOf serv:Namespace 
```

### serv:Identifier ###
An identifier is an information content entity that refers to another entity. An identifier defined in a namespace is associated with that namespace.
```
 serv:Identifier
  rdfs:subClassOf [serv:ICE]

  rdfs:label [string]                     # title [ns:id]
  dc:identifier [string]                  # ns:id
  serv:value [string]                     # id

  #optional
  serv:namespace [serv:Namespace]         # the namespace that this identifier is part of
  serv:entity [serv:Entity]               # the entity that this identifier denotes
  dc:replaces [serv:Identifier]           # to indicate a former identifier
```


### serv:Dataset ###
A dataset is an information content entity that is composed of information about entities.
```
 serv:Dataset
  rdfs:subClassOf [serv:ICE]
   owl:equivalentClass [sioc:Container]

  rdfs:label [string]                     # title [ns:id]
  dc:identifier [string]                  # ns:id

  #optional
  dc:title [string]                       # the official name of the resource
  dc:description [string]                 # an elaboration of the attributes of the resource 
  dc:subject [url|ns:id|string]           # a curated subject heading [e.g. protein]
  dc:publisher [foaf:Agent]               # link to the original/primary publisher [E.g. UniProt Consortium]
  dc:references [serv:Dataset]            # to link datasets together by reference - for linked data clouds
  foaf:homepage [url]                     # the homepage of the resource [e.g. http://uniprot.org]
  serv:id_example [string]                # an identifier in the dataset [e.g. 12345] 
  serv:id_specification [regex]           # a regular expression to validate the identifier against
```

## serv:Document ##
A document is an information content entity that is used to communicate information about some entity/entities.
```
 serv:Document
  owl:equivalentClass [foaf:Document]         
  owl:equilvanetClass [sioc:Item]

  rdfs:label [string]                     # title [ns:id]
  dc:identifier [string]                  # ns:id

  #optional
  dc:publisher[foaf:Agent]                # the publisher of the document
  serv:availability [string]              ["public"|"see license"] 
  dc:license [url]                        # a document that provides usage rights
  dc:source [uri|serv:Resolver]           # for derivative works: the original source of this data

  dc:fileFormat[string]                   # the document MIME-type ["text/html",etc]
  rdf:type [URI]                          [HTMLDocument, XMLDocument, RDFXMLDocument, OWLXMLDocument, etc]

  serv:entity [serv:Entity]               # identifies the entity that is the topic of the document
  serv:dataset [serv:Dataset]             # identifies the dataset that is the topic of the document
```


## serv:Statistics ##
Statistics is an information content entity that refers to quantities calculated from a dataset.
```
 serv:Statistics
  rdfs:label [string]                    # title [ns:id]
  dc:identifier [string]                 # ns:id

  #optional
  serv:records [integer]                 # number of entries in the core namespace
  serv:topics [integer]                  # number of unique entities
  serv:triples [integer]                 # number of unique statements
  serv:size [integer]                    # of bytes the file contains
  dc:source [Document|Dataset]           # the document/dataset for which the statistics were compiled
```