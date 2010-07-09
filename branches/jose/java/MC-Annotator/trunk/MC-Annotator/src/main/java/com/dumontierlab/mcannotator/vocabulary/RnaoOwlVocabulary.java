package com.dumontierlab.mcannotator.vocabulary;

import java.util.HashMap;

import com.dumontierlab.mcannotator.vocabulary.RnaoOwlVocabulary.ObjectProperty;
import com.hp.hpl.jena.ontology.AnnotationProperty;
import com.hp.hpl.jena.ontology.DatatypeProperty;
import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;

public class RnaoOwlVocabulary {
	public static final String DEFAULT_NAMESPACE = "http://purl.obofoundry.org/obo/rnao/";
	public static final String RNAO_NS = "http://purl.obofoundry.org/obo/rnao/RNAO_";
	public static final String RNAO_NS2 = "http://purl.obofoundry.org/obo/rnao/";
	public static final String RO_NS = "http://purl.obofoundry.org/ro/ro.owl#";
	
	private static final OntModel model = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
	
	static {
		model.setNsPrefix("rnao", RnaoOwlVocabulary.DEFAULT_NAMESPACE);
	}

	public final static HashMap<String, String> rnaoLabels = new HashMap<String, String>();
	static{
		rnaoLabels.put("0000145", "base stack adjacent base orientation");
		rnaoLabels.put("0000146", "base stack non-adjacent base orientation");
		rnaoLabels.put("0000122", "syn nucleoside conformation");
		rnaoLabels.put("0000123", "anti nucleoside conformation");
		rnaoLabels.put("0000114", "base pair cis-orientation");
		rnaoLabels.put("0000115", "base pair trans-orientation");
		rnaoLabels.put("0000324", "pairs with CHH");
		rnaoLabels.put("0000325", "pairs with THH");
		rnaoLabels.put("0000327", "pairs with CHS");
		rnaoLabels.put("0000328", "pairs with THS");
		rnaoLabels.put("0000330", "pairs with CHW");
		rnaoLabels.put("0000331", "pairs with THW");
		rnaoLabels.put("0000333", "pairs with CSH");
		rnaoLabels.put("0000334", "pairs with TSH");
		rnaoLabels.put("0000336", "pairs with CSS");
		rnaoLabels.put("0000337", "pairs with TSS");
		rnaoLabels.put("0000339", "pairs with CSW");
		rnaoLabels.put("0000340", "pairs with TSW");
		rnaoLabels.put("0000342", "pairs with CWH");
		rnaoLabels.put("0000343", "pairs with TWH");
		rnaoLabels.put("0000345", "pairs with CWS");
		rnaoLabels.put("0000346", "pairs with TWS");
		rnaoLabels.put("0000348", "pairs with CWW");
		rnaoLabels.put("0000349", "pairs with TWW");
		
		rnaoLabels.put("0000027", "adenine nuclebase");
		rnaoLabels.put("0000028", "guanine nuclebase");
		rnaoLabels.put("0000025", "cytosine nuclebase");
		rnaoLabels.put("0000026", "uracil nuclebase");
		
		rnaoLabels.put("0000094", "sugar edge");
		rnaoLabels.put("0000092", "Watson-Crick edge");
		rnaoLabels.put("0000093", "Hoogsteen edge");
		rnaoLabels.put("0000094", "sugar edge");
	}
	
	public final static HashMap<Property, Property> rnaoBasePairRelations = new HashMap<Property, Property>();
	static{
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCHH.property(), ObjectProperty.pairsWithCHH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTHH.property(), ObjectProperty.pairsWithTHH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCHS.property(), ObjectProperty.pairsWithCSH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTHS.property(), ObjectProperty.pairsWithTSH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCHW.property(), ObjectProperty.pairsWithCWH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTHW.property(), ObjectProperty.pairsWithTWH.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCSH.property(), ObjectProperty.pairsWithCHS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTSH.property(), ObjectProperty.pairsWithTHS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCSS.property(), ObjectProperty.pairsWithCSS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTSS.property(), ObjectProperty.pairsWithTSS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCSW.property(), ObjectProperty.pairsWithCWS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTSW.property(), ObjectProperty.pairsWithTWS.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCWH.property(), ObjectProperty.pairsWithCHW.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTWH.property(), ObjectProperty.pairsWithTHW.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCWS.property(), ObjectProperty.pairsWithCSW.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTWS.property(), ObjectProperty.pairsWithTSW.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithCWW.property(), ObjectProperty.pairsWithCWW.property());
		rnaoBasePairRelations.put(ObjectProperty.pairsWithTWW.property(), ObjectProperty.pairsWithTWW.property());

	}
	
	public static enum Class {
		BaseStackAdjacentBaseOrientation(RNAO_NS+"0000145"),
		BaseStackNonAdjacentBasePairOrientation(RNAO_NS+"0000146"),
		AntiNucleosideConformation(RNAO_NS +"0000123"),
		SynNucleosideConformation(RNAO_NS +"0000122"),
		CisOrientedBasePair(RNAO_NS+"0000116"),
		TransOrientedBasePair(RNAO_NS+"0000117"),
		NucleotideBasePair(RNAO_NS+"0000001");
	
		private final String uri;

		private Class(String uri) {
			this.uri = uri;
		}

		@Override
		public String toString() {
			return uri;
		}

		public String uri() {
			return uri;
		}

		public OntClass resource() {
			synchronized (model) {
				return model.createClass(uri);
			}
		}
	}
	
	public static enum ObjectProperty {
		weaklyInteractingWith(RNAO_NS+"0000315"),
		externallyConnectedTo(RNAO_NS2+"externally_connected_to"),
		hasPart(RO_NS +"has_part"),
		hasQuality(RO_NS +"has_quality"),
		hasBoundary(RNAO_NS+"0000352"),
		boundaryOf(RNAO_NS+"0000350"),
		partOf(RO_NS+"part_of"),
		pairsWithCHH(RNAO_NS+"0000324"),
		pairsWithTHH(RNAO_NS+"0000325"),
		pairsWithCHS(RNAO_NS+"0000327"),
		pairsWithTHS(RNAO_NS+"0000328"),
		pairsWithCHW(RNAO_NS+"0000330"),
		pairsWithTHW(RNAO_NS+"0000331"),
		pairsWithCSH(RNAO_NS+"0000333"),
		pairsWithTSH(RNAO_NS+"0000334"),
		pairsWithCSS(RNAO_NS+"0000336"),
		pairsWithTSS(RNAO_NS+"0000337"),
		pairsWithCSW(RNAO_NS+"0000339"),
		pairsWithTSW(RNAO_NS+"0000340"),
		pairsWithCWH(RNAO_NS+"0000342"),
		pairsWithTWH(RNAO_NS+"0000343"),
		pairsWithCWS(RNAO_NS+"0000345"),
		pairsWithTWS(RNAO_NS+"0000346"),
		pairsWithCWW(RNAO_NS+"0000348"),
		pairsWithTWW(RNAO_NS+"0000349");
		
		private final String uri;

		private ObjectProperty(String uri) {
			this.uri = uri;
		}

		@Override
		public String toString() {
			return uri;
		}

		public String uri() {
			return uri;
		}

		public com.hp.hpl.jena.ontology.ObjectProperty property() {
			synchronized (model) {
				return model.createObjectProperty(uri);
			}

		}
	};
	
	public static enum DataProperty {

		hasValue(DEFAULT_NAMESPACE + "hasValue"),
		hasStandardDeviation(DEFAULT_NAMESPACE + "hasStandardDeviation");

		private final String uri;

		private DataProperty(String uri) {
			this.uri = uri;
		}

		@Override
		public String toString() {
			return uri;
		}

		public String uri() {
			return uri;
		}

		public DatatypeProperty property() {
			synchronized (model) {
				return model.createDatatypeProperty(uri);
			}
		}
	};
	
	public static enum Annotation {
		details(DEFAULT_NAMESPACE + "details"), 
		description(DEFAULT_NAMESPACE + "description"), 
		experimentalMethod(DEFAULT_NAMESPACE + "experimentalMethod"), 
		modification(DEFAULT_NAMESPACE + "modification"), 
		mutation(DEFAULT_NAMESPACE + "mutation");

		private final String uri;

		private Annotation(String uri) {
			this.uri = uri;
		}

		@Override
		public String toString() {
			return uri;
		}

		public String uri() {
			return uri;
		}

		public AnnotationProperty property() {
			synchronized (model) {
				return model.createAnnotationProperty(uri);
			}
		}
	}
	
	public static OntModel getOntology() {
		for (Class c : Class.values()) {
			c.resource();
		}
		for (ObjectProperty p : ObjectProperty.values()) {
			p.property();
		}
		for (DataProperty p : DataProperty.values()) {
			p.property();
		}
		for (Annotation p : Annotation.values()) {
			p.property();
		}
		return model;
	}
	
	
}

