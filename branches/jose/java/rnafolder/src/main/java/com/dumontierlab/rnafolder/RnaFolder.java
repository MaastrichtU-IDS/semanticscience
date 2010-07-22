package com.dumontierlab.rnafolder;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.dumontierlab.sequence_generator.SequenceGenerator;

/**
 * This class executes RNAfold. This class creates a shell script in /tmp with
 * the parameters and specifications to run RNAfold
 * as
 * @author Jose Cruz-Toledo
 */

public class RnaFolder {
	/**
	 * Sequence to be folded by RNAfold as generated by SequenceGenerator.java
	 */
	String randomSequence;

	/**
	 * Contents of the shell script to be executed
	 */
	String shellScriptContents;

	/**
	 * Sequence generator object which creates random sequences
	 */
	SequenceGenerator seqGenerator;

	/**
	 * Raw output from RNAfold
	 */
	String rawRnafoldOutput;

	/**
	 * Dot bracket notation for the predicted secondary structure
	 */
	String dotBracket;

	/**
	 * Minimum free energy of folded structure
	 */
	Double mfe;

	/**
	 * String holding the full path of the RNAfold shell script
	 */
	String scriptFullPath = "/tmp/rnafold.sh";

	/**
	 * String holding the full path to the generated sequence file
	 */
	String randomSequenceFullPath = "/tmp/randSeq.txt";

	/**
	 * Sting holding the full path of the output file from RNAfold
	 */
	String rawOutputFullPath = "/tmp/rnafold.out";

	/**
	 * Default constructor, assumes a default shell script to be run. - Creates
	 * the default shell script - Creates a default sequence (SequenceGenerator)
	 * - Executes the shell script and keeps the results
	 */
	public RnaFolder() {
		// set/create the shell script var
		setShellScript("#!/bin/bash\nRNAfold<$1");
		createShellScript(getShellScript());

		// create/set a new random sequence
		seqGenerator = new SequenceGenerator();
		this.setRandomSequence(seqGenerator.getRandomSequence());

		// create input sequence file
		this.createInputSequenceFile(this.getRandomSequence());

		// now we can execute the RNAfold
		String rawOutput = foldMe();
		this.setRawRnafoldOutput(rawOutput);

		//set the dot-braket and MFE vars
		parseRawOutput("default");
	}// RnaFolder

	
	public RnaFolder(String shellScript, String parserFlag){
		//set the shell script var
		setShellScript(shellScript);
		createShellScript(getShellScript());
		
		// create/set a new random sequence
		seqGenerator = new SequenceGenerator();
		this.setRandomSequence(seqGenerator.getRandomSequence());
		
		// create input sequence file
		this.createInputSequenceFile(this.getRandomSequence());
		
		// now we can execute the RNAfold
		String rawOutput = foldMe();
	
		this.setRawRnafoldOutput(rawOutput);
		System.out.println(this.getRawRnafoldOutput());
		//set the dot-braket and MFE vars
		parseRawOutput(parserFlag);
	}
	/**
	 * This method executes RNAfold as specified by the shell script and returns
	 * a string with the raw output from RNAfold
	 */
	public String foldMe() {
		String returnMe = "";
		String[] cmdArr = { "/bin/bash", getScriptFullPath(),
				getRandomSequenceFullPath() };
		try {
			Process p = Runtime.getRuntime().exec(cmdArr);
			p.waitFor();
			returnMe = RnaFolder.writeProcessOutput(p);
			
		} catch (IOException e) {
			System.out.println("Error while executing RNAfold!\nError 1423-22");
			e.printStackTrace();
			System.exit(-1);
		} catch (InterruptedException e) {
			System.out.println("Mystery error # 5593-1");
			e.printStackTrace();
			System.exit(-1);
		}
		return returnMe;
	}// foldMe

	/**
	 * This method parses the raw output of RNAfold and extracts both the dot bracket notation
	 * and the mfe
	 * @param type if set to default it assumes that you ran RNAfold with the default parameters
	 */
	public void parseRawOutput(String type){
		if(type.equals("default")){
			//first split the raw output by newline
			String[] tmp;
			String tmpRaw = getRawRnafoldOutput();
			tmp = tmpRaw.split("\\n");
			
			String defaultPattern = "(\\S+)\\s+\\((.*)\\)";
			Pattern dPattern = Pattern.compile(defaultPattern);
			Matcher m = dPattern.matcher(tmp[1]);
			if(m.matches()){
				this.setDotBracket(m.group(1).trim());
				this.setMfe(new Double(m.group(2)));
			}//if
			else{
				System.out.println("Really strange things are happening");
				System.exit(-1);
			}
		}//if
	}//parseRawOutput
	
	/**
	 * This method creates a simple shell script that allows the execution of
	 * RNAfold
	 * 
	 * @param aScript
	 *            String containing the script that is to be created
	 */
	public void createShellScript(String aScript) {
		String scriptContents = aScript;
		try {
			FileWriter fw = new FileWriter(getScriptFullPath());
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(scriptContents);
			bw.close();
		} catch (IOException e) {
			System.out.println("Could not write file!\nError 66-43");
			e.printStackTrace();
			System.exit(-1);
		}
	}// createShellScript

	/**
	 * This method creates the input sequence file that contains a random
	 * sequence to be folded by RNAfold
	 * 
	 * @param anInputSeq
	 */
	public void createInputSequenceFile(String anInputSeq) {
		try {
			FileWriter fw = new FileWriter(getRandomSequenceFullPath());
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(anInputSeq);
			bw.close();
		} catch (IOException e) {
			System.out.println("Could not write sequence file!\nError 45-22");
			e.printStackTrace();
			System.exit(-1);
		}
	}// createInputSequenceFile

	/**
	 * This static method fetches the input stream from a process reads it into
	 * a string
	 * 
	 * @param aProc
	 * @return the contents of the input stream of aProc
	 */
	public static String writeProcessOutput(Process aProc) {
		InputStreamReader tmpReader = new InputStreamReader(
				new BufferedInputStream(aProc.getInputStream()));
		BufferedReader reader = new BufferedReader(tmpReader);
		String returnMe = "";
		while (true) {
			String line = "";
			try {
				line = reader.readLine();
			} catch (IOException e) {
				System.out.println("Could not read input file!\nError 664-12");
				e.printStackTrace();
				System.exit(-1);
			}
			if (line == null)
				break;
			returnMe += line + "\n";
		}// while
		return returnMe;
	}// writeProcessOutput

	public String getRawRnafoldOutput() {
		return rawRnafoldOutput;
	}

	public void setRawRnafoldOutput(String rawRnafoldOutput) {
		this.rawRnafoldOutput = rawRnafoldOutput;
	}

	public String getDotBracket() {
		return dotBracket;
	}

	public void setDotBracket(String dotBracket) {
		this.dotBracket = dotBracket;
	}
	
	/**
	 * returns the minimum free energy as calculated by RNAfold
	 * @return minimum free energy
	 */
	public Double getMfe() {
		return mfe;
	}

	public void setMfe(Double mfe) {
		this.mfe = mfe;
	}

	public SequenceGenerator getSeqGenerator() {
		return seqGenerator;
	}

	public void setSeqGenerator(SequenceGenerator seqGenerator) {
		this.seqGenerator = seqGenerator;
	}

	public String getRandomSequence() {
		return randomSequence;
	}

	public void setRandomSequence(String randomSequence) {
		this.randomSequence = randomSequence;
	}

	public String getShellScript() {
		return shellScriptContents;
	}

	public void setShellScript(String tmpShellScript) {
		this.shellScriptContents = tmpShellScript;
	}

	public void setShellScriptContents(String shellScriptContents) {
		this.shellScriptContents = shellScriptContents;
	}

	public String getScriptFullPath() {
		return scriptFullPath;
	}

	public void setScriptFullPath(String scriptFullPath) {
		this.scriptFullPath = scriptFullPath;
	}

	public String getRawOutputFullPath() {
		return rawOutputFullPath;
	}

	public void setRawOutputFullPath(String rawOutputFullPath) {
		this.rawOutputFullPath = rawOutputFullPath;
	}

	public String getRandomSequenceFullPath() {
		return randomSequenceFullPath;
	}

	public void setRandomSequenceFullPath(String randomSequenceFullPath) {
		this.randomSequenceFullPath = randomSequenceFullPath;
	}

	public static void main(String[] args) {
		RnaFolder r = new RnaFolder();
		System.out.println(r.getDotBracket()+"\n"+r.getMfe());
		
		
		

	}

}
