package com.molsurfgen.sadi;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.ResourceFactory;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.molsurfgen.io.FileIO;

public class MolSurfGenService extends SimpleSynchronousServiceServlet
{
	private static final boolean debug = false;
	
	private static final String BaseURL = "http://semanticscience.org/ontology/molecular_surface_generator.owl#";
	private static final String BroURL = "http://semanticscience.org/resource/";
	
	public static final Property hasAttribute = ResourceFactory.createProperty(BaseURL + "hasAttribute");
	public static final Property hasParameter = ResourceFactory.createProperty(BaseURL + "hasParameter");
	public static final Property hasValue = ResourceFactory.createProperty(BroURL + "hasValue");

	public MolSurfGenService()
	{
		super();
	}
	
	public void processInput(Resource input, Resource output)
	{
		try{
			StmtIterator iter = input.listProperties(hasAttribute);
			String id = "";
			
			while (iter.hasNext()) {
				Statement statement = iter.nextStatement();
				Resource pdbId = statement.getResource();
				id = pdbId.getProperty(hasValue).getString();
			}
			
			try {
				Runtime rt = Runtime.getRuntime();
				Process pr = rt.exec("./MolSurfaceGen32/chimera/bin/chimera --debug --script ./MolSurfaceGen32/chimera/bin/execMakeMeshes.py -- " + id + " 40 5.0");
				BufferedReader reader = new BufferedReader(new InputStreamReader(pr.getInputStream()));
				 
				if(debug){
		            String line = null;
		
		            while((line = reader.readLine()) != null) {
		                System.out.println(line);
		            }
				}
	
	            int exitVal = pr.waitFor();

			} catch (IOException e) {
				e.printStackTrace();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			FileIO fileIO = new FileIO();
			fileIO.parseAndAnnotate("./MolSurfaceGen32/chimera/bin/VertexAnno.txt", output);
			
			System.gc();
			
		}catch(Exception e){
			e.printStackTrace();
		}
		
	}
}
