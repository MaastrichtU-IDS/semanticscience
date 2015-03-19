## Purpose ##
The Semantic Entity Discovery Service provides a Semantic Web Document that indicates which documents contain information about entities of interest.

## USE CASES ##
  1. Discover all serv:Documents that contain statements about a serv:Entity that is part of a serv:Dataset.
  1. Discover which serv:Documents in 1. are provided by a) the original data provider, b) mirrors and c) third-parties.
  1. Discover which serv:Documents in 1./2. are in a specific format (e.g. HTML, RDF/N3, RDF/XML, etc).
  1. Discover which serv:Entities are equivalent across serv:Namespaces resolved by data providers.

## Methods ##
The service first queries the [Life Science Dataset Registry (LSDR)](http://code.google.com/p/semanticscience/wiki/lsdr) for all resolvers that respond to a specified (or equivalent) namespace. For each resolver, it constructs the URI from their specified uri\_pattern by substituting the entity identifier and the (directly linked) namespace. The service then constructs a document containing i. entity, ii. dataset, iii. document(s) + format, iv) providers. The type of document returned is based on the content-header or format=[html|rdf/n3|rdf/xml] argument.

## Example ##

## Vocabulary ##
### serv:Locator ###
A locator is an agent that is capable of providing the location of **information** about some entity given an identifier and optionally the namespace it belongs to.

```
 serv:Locator
  rdfs:label [string]                     # title [ns:id]
  dc:identifier [string]                  # ns:id

  dc:publisher [foaf:Agent]               # the publisher of the locator [e.g. Bio2RDF publishes one RDF locator for all namespaces]
  serv:namespace [serv:Namespace]         # the namespace(s) for which the locator provides information 
  serv:document [serv:Document]           # the document that the locator identifier    
  serv:file_format [string]               # the format of the files located
                                           ["auto","rdfxml","n3","xml","json","html"]
```

A URI locator is a locator that is capable of constructing the location of information about an entity using a defined URI pattern.
```
 serv:URILocator
  rdfs:subClassOf serv:Locator

  serv:uri_pattern [uri regex]            # A regular expression for the constructing the URI, 
                                          # using variables $ns for the namespace and $id for the identifier 
                                           [e.g. http://bio2rdf.org/$ns:$id]
```

A SPARQL endpoint locator is a locator that is capable of providing the location of a SPARQL endpoint for a given namespace.
```
 serv:SPARQLEndpointLocator
  rdfs:subClassOf serv:Locator
 
  serv:sparql_endpoint [url]              # SPARQL endpoint URL [e.g. http://geneid.bio2rdf.org/sparql]
  serv:query_parameter_name [string]      # the name of the SPARQL query parameter
  serv:graph_parameter_name [string]      # the name of the default graph parameter
  serv:graph [uri]                        # Default graph URI
  serv:fileformat_parameter_name [string] # the name of the fileformat parameter
```


## RESTful Service ##
default:
> http://semanticscience.org/discover/namespace:identifier

custom:
> http://semanticscience.org/discover/?namespace=[namespace]&identifier=[identifier]&provider=[provider]&format=[format]