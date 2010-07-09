package com.dumontierlab.mcannotator.vocabulary;

import java.util.HashMap;

import com.hp.hpl.jena.ontology.AnnotationProperty;
import com.hp.hpl.jena.ontology.DatatypeProperty;
import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.ModelFactory;

public class PdbOwlVocabulary {
	public static final String DEFAULT_NAMESPACE = "http://bio2rdf.org/pdb:";
	public static final String PDB_NS = "http://bio2rdf.org/pdb:";
	public static final String SS = "http://semanticscience.org/resource/";
	
	private static final OntModel model = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
	
	static {
		model.setNsPrefix("pdb", PdbOwlVocabulary.DEFAULT_NAMESPACE);
	}

	public final static HashMap<String, String> pdbLabels = new HashMap<String, String>();
	static{

	}

	public static enum Class {
		PDB_HOLDER(PDB_NS);
	
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
		isAbout(SS+"isAbout");
		
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
