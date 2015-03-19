# Provenance #
Provenance refers to the chronology of an object, including the circumstances around its origin (creation/discovery) and subsequent transfer of ownership or derivation.

A [W3C working group](http://www.w3.org/2011/01/prov-wg-charter) was formed to provide a specification for the representation of provenance in RDF/OWL.  The proposed model involves 3 types (Entity, Activity and Agent) and 7 relations (WasDerivedFrom, WasGeneratedBy, WasAssociatedWith, WasAttributedTo, WasInformedBy, Used and ActedOnBehalfOf). The main use cases that are presented include: Generation, Usage, Communication, Invalidation, Derivation, Revision, Quotation and Influence. Let us consider these in the context of SIO.

### Process-Based Provenance ###
**Creation** ([sio:creation](http://semanticscience.org/resource/creation)) is the process by which an entity comes into existence, **destruction** ([sio:destruction](http://semanticscience.org/resource/Destruction)) is the process by which an entity ceases to exist, and **modification** ([sio:modification](http://semanticscience.org/resource/modification)) is the process by which an entity is modified (gains/loses parts, qualities, roles, dispositions, functions, etc) but _retains_ its identity.

Processes can be described in terms of their participants in the following way:
  * 'has participant' ([sio:has-participant](http://semanticscience.org/resource/has-participant)) specifies entities that _participate_ in a process
  * 'has agent' ([sio:has-agent](http://semanticscience.org/resource/has-agent)) specifies entities that direct or actively participate in the creation/modification/destruction/use of an object

  * 'has input' ([sio:has-input](http://semanticscience.org/resource/has-input)) specifies entities _used_ in a process
  * 'has target' ([sio:has-target](http://semanticscience.org/resource/has-target) specifies entities that are _modified_, but retain their identity
  * 'has substrate' ([sio:has-substrate](http://semanticscience.org/resource/has-substrate)) specifies entities that are _consumed_ (or are sufficiently changed that they lose their canonical identity)
  * 'has product' ([sio:has-product](http://semanticscience.org/resource/has-product)) specifies _new_ entities formed by the process

Process space and time can be specified by:
  * 'is located in' ([sio:is-located in](http://semanticscience.org/resource/is-located-in)) specifies the space of processes
  * 'exists at' ([sio:exists-at](http://semanticscience.org/resource/exists-at)) specifies the time instant (exact xsd:dateTime) or interval of processes (datatype range to specify the start and end date and times e.g. >= dateTime && <= dateTime).

### Object-Level Provenance ###
SIO offers several relations to specify the provenance relationship _among_ objects. In the first case, we consider objects that were created by, is being provided by or have been obtained from a source.

  * 'has source' ([sio:has-source](http://semanticscience.org/resource/has-source)) specifies _an_ origin of the object
  * 'has creator' ([sio:has-creator](http://semanticscience.org/resource/has-creator)) specifies the agent responsible for bringing the object into existence
  * 'has provider' ([sio:has-provider](http://semanticscience.org/resource/has-provider)) specifies the agent that provided the object
  * 'derives from' ([sio:derives-from](http://semanticscience.org/resource/derives-from)) specifies the object(s) from which this object was created from/with

_informational objects_

  * 'is version of' ([sio:is-version-of](http://semanticscience.org/resource/is-version-of)) specifies the object for which this is based on
  * 'is prior version of' ([sio:is-prior-version-of](http://semanticscience.org/resource/is-prior-version-of)) / 'is subsequent version of' ([sio:is-subsequent-version-of](http://semanticscience.org/resource/is-subsequent-version-of)) specifies the version order