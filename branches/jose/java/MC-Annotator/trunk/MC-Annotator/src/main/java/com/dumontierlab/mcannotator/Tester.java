package com.dumontierlab.mcannotator;

import com.dumontierlab.mcannotator.vocabulary.McaOwlVocabulary;
import com.dumontierlab.mcannotator.vocabulary.Owl2Vocabulary;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.OWL;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class Tester {

	/**
	 * @param args
	 */
	public Model model;

	public Tester() {
		model = ModelFactory.createDefaultModel();
	}

	public Model getRdfModel() {
		return model;
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Tester t = new Tester();
		Model m = t.getRdfModel();
		Resource bob = m.createResource("http://test.org/ns:bob");
		Resource arm = m.createResource("http://test.org/ns:arm");
		Resource arm2 = m.createResource("http://test.org/ns:arm2");
		
		m.add(bob, McaOwlVocabulary.ObjectProperty.hasPart.property(), arm);
		

		// Axiom
		//Resource rnao348 = m.createResource("http://obo/RNAO_000348");
		//Resource mvo2 = m.createResource("http://mvo/MVO_000002");
		//Resource mvo3 = m.createResource("http://mvo/MVO_000003");
		
		Resource axiom = m.createResource();
		m.add(axiom, RDF.type, Owl2Vocabulary.Class.OwlAxiom.resource());
		m.add(axiom, RDFS.seeAlso, "bobby123");
		m.add(axiom, OWL.sameAs, arm2);
		m.add(axiom, Owl2Vocabulary.ObjectProperty.annotatedProperty.property(), McaOwlVocabulary.ObjectProperty.hasPart.property());
		m.add(axiom, Owl2Vocabulary.ObjectProperty.annotatedSource.property(), bob);
		m.add(axiom, Owl2Vocabulary.ObjectProperty.annotatedTarget.property(), arm);
		
		m.write(System.out);
	}
}
