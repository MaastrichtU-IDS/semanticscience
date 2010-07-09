package com.dumontierlab.mcannotator;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedList;

import org.apache.commons.cli.*;


import com.dumontierlab.mcannotator.bin.ParseMCAnnotate;
import com.dumontierlab.mcannotator.bin.RDFizeMCAnnotate;
import com.dumontierlab.mcannotator.bin.RunMCAnnotate;
import com.dumontierlab.mcannotator.rna.BasePair;
import com.dumontierlab.mcannotator.rna.Nucleotide;
import com.hp.hpl.jena.rdf.model.Model;
public class MCAnnotateMain {
	/**
	 * From here the entire program starts :)
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException {
		CommandLineParser parser = new PosixParser();
		File inputDirectory = new File(""), outputDirectory = new File("");
		boolean makeRdf = true;
		boolean fredFormat = false;
		
		Option inputDir = new Option("i", "input", true, "input directory where PDB files are stored");
		inputDir.setArgs(1);
		inputDir.setRequired(true);
		inputDir.setArgName("directory");

		
		Option outputDir = new Option("o", "output", true, "output directory where the raw MC-Annotate files"+
			"and RDF files will be created");
		outputDir.setArgs(1);
		outputDir.setRequired(true);
		outputDir.setArgName("directory");
		
		Option rnaview = new Option("r", "mc-annotate", false, "only run MC-Annotate on PDB files (does "+
			"not RDFize the PDB files)");
		rnaview.setArgs(0);
		rnaview.setRequired(false);		
		
		Option fred = new Option("f", "fr3d", false, "RDFize files to suit the format used "+
			"by FR3D");
		rnaview.setArgs(0);
		rnaview.setRequired(false);		
		
		Options options = new Options();
		options.addOption(inputDir);
		options.addOption(outputDir);
		options.addOption(rnaview);
		options.addOption(fred);
		
		HelpFormatter formatter = new HelpFormatter();
		
		try {
		    CommandLine line = parser.parse( options, args );
		    
		    if (line.hasOption("r") && line.hasOption("f")){
		    	System.out.println("Can only have one of these options: r f");
		    	formatter.printHelp("RDFize MC-Annotate", options);
				System.exit(-1);    	
		    }
		    
		    if (line.hasOption("i")){
		    	inputDirectory = new File(line.getOptionValue("i"));
		    }
		    if (line.hasOption("o")){
		    	outputDirectory = new File(line.getOptionValue("o"));
		    } 
		    if (line.hasOption("r")){
		    	makeRdf = false;
		    }
		    if (line.hasOption("f")){
		    	fredFormat = true;
		    }
		}
		catch (ParseException e) {
			System.out.println(e.getMessage());
			formatter.printHelp("RDFize MC-Annotate", options);
			System.exit(-1);
		}
		
		//RunMCA and get a Linked list of Files containing the raw output :)
		RunMCAnnotate r = new RunMCAnnotate(inputDirectory, outputDirectory);
		LinkedList<File> outputFiles = r.run();
		
		/*
		 * Iterate through  the Linked List of Files to generate a Linked List of Parsed
		 * MCA objects
		 */
		System.out.println("Starting to parse the MC-Annotate output...");
		LinkedList<ParseMCAnnotate> parsedMCAFiles = new LinkedList<ParseMCAnnotate>();
		for(File file : outputFiles){
			System.out.println("Now parsing:" + file.getAbsolutePath());
			ParseMCAnnotate parsedFile = new ParseMCAnnotate(file);
			parsedMCAFiles.add(parsedFile);		
			System.out.println("ockjash");
			System.exit(1);
		}
		System.out.println("Done parsing MC-Annotate...");
		
		/*
		 * Now that we have a Linked List of Parsed MCA objects we can
		 * RDFize them 
		 */
		System.out.println("Starting to RDFize MC-Annotate...");
		for(ParseMCAnnotate aP : parsedMCAFiles){
			RDFizeMCAnnotate rdf = new  RDFizeMCAnnotate(aP, "fr3d");
			Model m = rdf.getRdfModel();
			m.write(System.out);
			System.exit(1);
		}
		System.out.println("Done RDFizing MC-Annotate...");
		
		
		if(makeRdf){
		/*	for(File file:outputFiles){
				ParseMCAnnotate rdf = new ParseMCAnnotate(file);
				System.out.println("Now RDFizing: "+ file.getAbsolutePath());
				//File rdfFile = new File(outputDirectory+/rdf/+)
				String outputPath = r.getRdfMcaOutputDirectory()+"/rdf/"+r.getPDBFromFile(file)+"_M_"+j+".out
			}
			*/
		}else{
			//Do Nothing
		}
		System.exit(-1);
	}

}//Mcannotate