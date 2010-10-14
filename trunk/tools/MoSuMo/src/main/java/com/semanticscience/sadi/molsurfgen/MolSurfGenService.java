package com.semanticscience.sadi.molsurfgen;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Properties;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import ca.wilkinsonlab.sadi.service.simple.SimpleAsynchronousServiceServlet;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.ResourceFactory;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.semanticscience.sadi.molsurfgen.io.FileIO;

public class MolSurfGenService extends SimpleSynchronousServiceServlet
{
	private static final boolean debug = false;
	private String MSMG_PATH = "./MolSurfaceGen64/chimera/bin/";//opt/bin";
	
	private static final String BaseURL = "http://semanticscience.org/ontology/molecular_surface_generator.owl#";
	private static final String SioURL = "http://semanticscience.org/resource/";
	
	public static final Property hasProperty = ResourceFactory.createProperty(SioURL + "SIO_000008");
	public static final Property hasValue = ResourceFactory.createProperty(SioURL + "SIO_000300");

	public MolSurfGenService()
	{
		super();
		
		Properties props = new Properties();

        try {

           props.load(new FileInputStream("MoSuMo.prop"));

           String dir = props.getProperty("chimeraDir");

           MSMG_PATH = dir;
        }
        catch(IOException e)
        {
        	e.printStackTrace();
        }
	}
	
	public void processInput(Resource input, Resource output)
	{
		long timeStamp = System.currentTimeMillis();
		
		try{
			StmtIterator iter = input.listProperties(hasProperty);
			String id = "";
			
			while (iter.hasNext()) {
				Statement statement = iter.nextStatement();
				Resource pdbId = statement.getResource();
				id = pdbId.getProperty(hasValue).getString();
			}
			
			try {
				Runtime rt = Runtime.getRuntime();
				Process pr = rt.exec(MSMG_PATH + "chimera --debug --script " + MSMG_PATH + "execMakeMeshes.py -- " + id + " " + timeStamp + " 40 5.0");
				BufferedReader reader = new BufferedReader(new InputStreamReader(pr.getInputStream()));
				 
				if(debug){
		            String line = null;
		
		            while((line = reader.readLine()) != null) {
		                System.out.println(line);
		            }
				}
	
	            int exitVal = pr.waitFor();
	            
	            File file = new File(MSMG_PATH + "Output-" + timeStamp + ".txt");
	            
	            if(exitVal != 0 || !file.exists()){
		            try {
		            	BufferedReader in = new BufferedReader(new FileReader(MSMG_PATH + "ErrorLog" + timeStamp + ".txt"));
						
						String line = new String();
						
						if(line == null || line.equals("")){
							System.err.println("Chimera error.");
						}
						
					    while ((line = in.readLine()) != null){
					    	System.err.println(line);
					    }
					    
					    in.close();
					} catch (FileNotFoundException e1) {
						System.err.println("Unknown error.");
					} catch (IOException e2) {
						e2.printStackTrace();
					}
	            }

			} catch (IOException e) {
				e.printStackTrace();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			FileIO fileIO = new FileIO();
			fileIO.parseAndAnnotate(MSMG_PATH + "Output-" + timeStamp + ".txt", output);
			
			System.gc();
			
		}catch(Exception e){
			e.printStackTrace();
		}
		
	}
}
