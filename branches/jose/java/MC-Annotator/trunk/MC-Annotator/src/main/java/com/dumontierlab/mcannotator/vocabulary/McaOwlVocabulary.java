package com.dumontierlab.mcannotator.vocabulary;


import java.util.HashMap;

import com.hp.hpl.jena.ontology.AnnotationProperty;
import com.hp.hpl.jena.ontology.DatatypeProperty;
import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.vocabulary.OWL;

public class McaOwlVocabulary {
	public static final String DEFAULT_NAMESPACE = "http://bio2rdf.org/pdb:";
	public static final String PDB_NS = "http://bio2rdf.org/pdb:";
	public static final String MCA_NS = "http://bio2rdf.org/mcannotate:";
	public static final String CHEBI_NS = "http://bio2rdf.org/chebi:";
	public static final String RKB_NS = "http://semanticscience.org/rkb:RKB_";
	public static final String RKB_NS2 = "http://semanticscience.org/rkb:";
	public static final String RNAO_NS = "http://purl.obofoundry.org/obo/rnao/RNAO_";
	public static final String RNAO_NS2 = "http://purl.obofoundry.org/obo/rnao/";
	public static final String NULO = "http://semanticscience.org/resource/";
	public static final String BIO2RDF = "http://bio2rdf.org/";
	public static final String SS = "http://semanticscience.org/resource/";
	
	private static final OntModel model = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
	static {
		model.setNsPrefix("pdb", McaOwlVocabulary.DEFAULT_NAMESPACE);
	}
	
	public final static HashMap<String, String> rkbClasses = new HashMap<String, String>();
	static{
		rkbClasses.put("000000", "structure model");
		rkbClasses.put("000111", "molecular structure file");
		rkbClasses.put("000001", "nucleotide base pair");
		rkbClasses.put("000126", "sub edge interaction");
		rkbClasses.put("000015", "chemical");
		rkbClasses.put("000115", "downward stacking");
		rkbClasses.put("000116", "inward stacking");
		rkbClasses.put("000117", "outward stacking");
		rkbClasses.put("000118", "upward stacking");
		rkbClasses.put("000089", "nucleotide sub edge");
		rkbClasses.put("000100", "watson watson sub edge");
		rkbClasses.put("000099", "watson sugar sub edge");
		rkbClasses.put("000098", "watson hoogsteen sub edge");
		rkbClasses.put("000097", "sugar watson sub edge");
		rkbClasses.put("000096", "sugar sugar sub edge");
		rkbClasses.put("000095", "o2 prime sub edge");
		rkbClasses.put("000094", "hoogsteen watson sub edge");
		rkbClasses.put("000093", "hoogsteen hoogsteen sub edge");
		rkbClasses.put("000091", "c8 sub edge");
		rkbClasses.put("000102", "bifurcated sugar sub edge");
		rkbClasses.put("000101", "bifurcated hoogsteen sub edge");
		rkbClasses.put("000107", "c1 prime endo");
		rkbClasses.put("000108", "c2 prime endo");
		rkbClasses.put("000109", "c3 prime endo");
		rkbClasses.put("000110", "c4 prime endo");
		rkbClasses.put("000134", "o4 prime endo");
		rkbClasses.put("000135", "c1 prime exo");
		rkbClasses.put("000136", "c2 prime exo");
		rkbClasses.put("000137", "c3 prime exo");
		rkbClasses.put("000138", "c4 prime exo");
		rkbClasses.put("000139", "o4 prime exo");
		rkbClasses.put("000129", "antiparallel base pair");
		rkbClasses.put("000130", "parallel base pair");
	}
	
	
	public final static HashMap<String, String> chebiClasses = new HashMap<String, String>();
	static{
		chebiClasses.put("50308", "CMP residue");
		chebiClasses.put("50324", "GMP residue");
		chebiClasses.put("46470", "UMP residue");
		chebiClasses.put("50306", "AMP residue");
	}
	
	public static enum Class {
		StructureModel(RKB_NS + "000000"),
		MolecularStructureFile(RKB_NS +"000111"),
		Chemical(RKB_NS +"000015"),
		NucleotideBasePair(RKB_NS+"000001"),
		SubEdgeInteraction(RKB_NS+"000126");
	
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
		isRepresentedBy(SS + "isRepresentedBy"),
		hasProperPart(SS+ "hasProperPart"),
		hasPart(SS+ "hasPart"),
		isDenotedBy(SS + "isDenotedBy"),
		hasQuality(SS + "hasQuality"),
		isSubjectOf(SS +"isSubjectOf"),
		isQualityOf(SS +"isQualityOf"),
		isConcretizedBy(SS +"isConcretizedBy"),
		isAbout(SS+"isAbout"),
		hasSource(SS+"hasSource"),
		generatedBy(SS+"generatedBy");
		
		
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
	
	public static void main(String[] args) {
		System.out.println("Classes: " + Class.values().length);
		System.out.println("Object Properties: " + ObjectProperty.values().length);
		System.out.println("Data Properties: " + DataProperty.values().length);
		System.out.println("Annotations: " + Annotation.values().length);
	}
}
