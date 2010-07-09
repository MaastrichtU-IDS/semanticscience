/**
 * This class generates RDF from the parsed output from MC-Annotate
 */

package com.dumontierlab.mcannotator.bin;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.FileUtils;

import com.dumontierlab.mcannotator.rna.BasePair;
import com.dumontierlab.mcannotator.rna.Nucleotide;
import com.dumontierlab.mcannotator.rna.Stack;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;

public class ParseMCAnnotate {
	private LinkedList<BasePair> basePairs;// base pairs
	private LinkedList<Stack> stacks;// adjacent and non-adjacent stacks
	private LinkedList<Nucleotide> nucleotides; // nucleotide conformations
												// anti|syn
	
	File inputFile;
	private String pdbId = "";
	private int modelNumber = 1;// always start at 1?
	private HashMap<String, String> mcaSections;

	public ParseMCAnnotate(File file) {
		this(file, "", 0);
	}

	public ParseMCAnnotate(File file, String aPdbId, int aModelNumber) {
		basePairs = new LinkedList<BasePair>();
		nucleotides = new LinkedList<Nucleotide>();
		stacks = new LinkedList<Stack>();

		if (aPdbId.equals("")) {
			pdbId = findPDBId(file);
		} else {
			pdbId = aPdbId;
		}
		if (aModelNumber < 1) {
			modelNumber = findModelNumber(file);
		} else {
			modelNumber = aModelNumber;
		}

		this.setMCASections(file);

		// now we can create the top level statements
		// createTopLevelStatements();

		// now we can get each section and populate our Base Pair Linked List
		if (this.getMcaSections().get("Base pairs") != null) {
			String bp = this.getMcaSections().get("Base pairs");
			basePairs = parseBasePairs(bp);
		}
		// nucleotides
		if (this.getMcaSections().get("Residue Conformations") != null) {
			String resConfors = this.getMcaSections().get(
					"Residue Conformations");
			nucleotides = parseResidueConformations(resConfors);
		}
		if (this.getMcaSections().get("Adjacent Stackings") != null) {
			String adjStackings = this.getMcaSections().get(
					"Adjacent Stackings");
			stacks = parseAdjacentStackings(adjStackings);
		}
		if (this.getMcaSections().get("Non-Adjacent Stackigns") != null) {
			String nonAdjStackings = this.getMcaSections().get(
					"Non-Adjacent Stackings");
			stacks = parseNonAdjacentStackings(nonAdjStackings);
		}
		
		/*
		 * Now that we have the basepair, nucleotides and stacks
		 * lists populated we can rdfize their contents.
		 */
		
		
	}// constructor

	

	public LinkedList<Stack> getStacks() {
		return stacks;
	}

	public void setStacks(LinkedList<Stack> stacks) {
		this.stacks = stacks;
	}

	public LinkedList<Nucleotide> getNucleotides() {
		return nucleotides;
	}

	public void setNucleotides(LinkedList<Nucleotide> nucleotides) {
		this.nucleotides = nucleotides;
	}

	public void setBasePairs(LinkedList<BasePair> basePairs) {
		this.basePairs = basePairs;
	}



	public LinkedList<BasePair> getBasePairs() {
		return basePairs;
	}

	public HashMap<String, String> getMcaSections() {
		return mcaSections;
	}

	public void setMcaSections(HashMap<String, String> mcaSections) {
		this.mcaSections = mcaSections;
	}

	private LinkedList<BasePair> parseBasePairs(String val) {
		/* This method parses the base pair section of the MCA output */
		/* this method should add the base pair information into the hash Map */
		// create the base pair object and add it
		// A6-A35 : G-C Ww/Ww pairing antiparallel cis XIX

		String[] lineArr = val.split("\\n");
		String firstPattern = "(\\S+)\\s:\\s(\\S+)\\spairing\\s(antiparallel|parallel)\\s(cis|trans)(.*)";
		String secondPattern = "(\\S+)\\s:\\s(\\S+)(.+)pairing\\s(antiparallel|parallel)\\s(cis|trans)(.*)";
		Pattern firstBpPattern = Pattern.compile(firstPattern);
		Pattern secondBpPattern = Pattern.compile(secondPattern);
		for (String aLine : lineArr) {
			Matcher secondMatch = secondBpPattern.matcher(aLine.trim());
			if (secondMatch.matches()) {
				if (secondMatch.group(3).length() != 0) { //grabbing only base pairs that specify the normal direction for the basepair
					
					String participants = secondMatch.group(1).trim();// A6-A35
					String participantNames = secondMatch.group(2).trim();// G-C
					String[] chainPos = participants.split("-");
					String[] residueLabels = participantNames.split("-");
					String res1Label = residueLabels[0];// G
					String res2Label = residueLabels[1];// C
					String subEdgesTmp = secondMatch.group(3).trim();// Ww/Ww || Ww/Ww
																// Hh/O2'
					String strandOrientation = secondMatch.group(4).trim();// antiparallel
					String glycosidicOrient = "";
					if ((secondMatch.group(5).trim()).equals("cis")
							|| (secondMatch.group(5).trim()).equals("trans")) {
						glycosidicOrient = secondMatch.group(5).trim();
					}// if
					String[] subEdgeArr = subEdgesTmp.split(" ");
					// consider the Ww/Ww Hh/O2' case
					//A6-A35
					Pattern p = Pattern.compile("(\\w)(\\d+)-(\\w)(\\d+)");
					Matcher match2 = p.matcher(secondMatch.group(1));
					if (match2.matches()) {
						if (match2.group(1).length() != 0) {
							String res1chain = match2.group(1).trim();
							String res2chain = match2.group(3).trim();
							String res1Pos = match2.group(2).trim();
							String res2Pos = match2.group(4).trim();
							
							BasePair bp = new BasePair(res1Label,
									res1Pos, res1chain, res2Label,
									res2Pos, res2chain, glycosidicOrient);
							bp.setSubEdgeArr(subEdgeArr);
							bp.setPdbId(getPdbId());
							bp.setModelNumber(getModelNumber());
							this.basePairs.add(bp);
						}// if
					}// if
				}// if
			}// if
			else{
				//deal with the weird ones here
				// i.e : A11-A12 : G-A O2'/Hh adjacent_5p pairing 
				System.out.println("****"+aLine);
			}
		}// for
		return this.getBasePairs();

	}// basePairs

	private LinkedList<Stack> parseNonAdjacentStackings(String val) {
		/* This method parses the non adjacent stackings section of the MCA output */
		//A11-A35 : upward pairing
		String [] lineArr = val.split("\\n");
		Pattern nasPattern = Pattern.compile("(\\S+)\\s\\:\\s(\\S+).*");
		for(String aLine : lineArr){
			Matcher m = nasPattern.matcher(aLine.trim());
			if(m.matches()){
				if(m.group(2).length() != 0){
					String participants = m.group(1).trim();
					String direction = m.group(2).trim();
					String[] chainTmp = participants.split("-");
					Pattern p = Pattern.compile("^([A-Z]+)(\\d+)$");//A11-A35
					Matcher matches = p.matcher(chainTmp[0]);
					Matcher matches2 = p.matcher(chainTmp[1]);
					String chainId1 = "";
					String residueNum1 = "";
					String chainId2 = "";
					String residueNum2 = "";
					if(matches.matches()){
						chainId1 = matches.group(1).trim();
						residueNum1 = matches.group(2).trim();
					}//if
					if(matches2.matches()){
						chainId2 = matches2.group(1).trim();
						residueNum1 = matches2.group(2).trim();
					}//if
					Stack s = new Stack(residueNum1, chainId1, residueNum2, chainId2, false, direction);
					s.setPdbId(this.getPdbId());
					this.getStacks().add(s);
				}//if
			}//if
			else{
				//System.out.println(aLine);
			}
		}//for
		return this.getStacks();
	}

	private LinkedList<Stack> parseAdjacentStackings(String val) {
		/* This method parses the adjacent stackings section of the MCA output */
		//A6-A7 : adjacent_5p upward
		String [] lineArr = val.split("\\n");
		Pattern aSPattern = Pattern.compile("(\\S+)\\s\\:\\s(\\S+)\\s(\\S+)(.*)");
		for(String aLine : lineArr){
			Matcher m = aSPattern.matcher(aLine.trim());
			if(m.matches()){
				if(m.group(3).length() != 0){
					String participants = m.group(1).trim();//A6-A7
					String [] chainTmp = participants.split("-");
					Pattern p = Pattern.compile("^([A-Z]+)(\\d+)$");
					Matcher matches = p.matcher(chainTmp[0]);
					Matcher matches2 = p.matcher(chainTmp[1]);
					String chainId1 = "";
					String residueNum1 = "";
					String chainId2 ="";
					String residueNum2 ="";
					String stackingDirection = m.group(3);
					if(matches.matches()){
						chainId1 = matches.group(1).trim();
						residueNum1 = matches.group(2).trim();					
					}//if
					if(matches2.matches()){
						chainId2 = matches2.group(1);
						residueNum2 = matches2.group(2);
					}//if
					
					Stack s = new Stack(residueNum1, chainId1, residueNum2, chainId2, true,stackingDirection);
					s.setPdbId(this.getPdbId());
					this.getStacks().add(s);
				}//if
			}//if
			else{
				//System.out.println(aLine);
			}
		}//for
		return this.getStacks();
	}

	private LinkedList<Nucleotide> parseResidueConformations(String val) {
		/* This method parses the residue conformations section of the MCA output */
		String [] lineArr = val.split("\\n");
		//A8 : G C2p_exo anti
		Pattern rcPattern = Pattern.compile("(\\S+)\\s\\:\\s(\\S+)\\s(\\S+)\\s(\\S+)");
		for(String aLine: lineArr){
			Matcher m = rcPattern.matcher(aLine.trim());
			if(m.matches()){
				if((m.group(4)).equals("anti") || (m.group(4)).equals("syn")){
					//split the chain from the residue
					Pattern chainResPatt = Pattern.compile("(\\w)(\\d+)");
					Matcher m2 = chainResPatt.matcher(m.group(1).trim());
					//split puckering line
					Pattern puckerPatt = Pattern.compile("(\\S+)\\_(\\S+)");
					Matcher m3 = puckerPatt.matcher(m.group(3).trim());
					//A8 : G C2p_exo anti
					if(m3.matches() && m2.matches()){
						String puckerAtom = m3.group(1); //C2p
						String puckerQual = m3.group(2); //exo
						String chainId = m2.group(1); //A
						String residueNum = m2.group(2);//8
						String residueName = m.group(2); //G
						String resConformation = m.group(4);//anti
						//create a nucleotide obj
						Nucleotide nuc = new Nucleotide(residueName, residueNum, chainId);
						nuc.setPuckerAtom(puckerAtom);
						nuc.setPuckerQuality(puckerQual);
						nuc.setPdbId(this.getPdbId());
						nuc.setNucleotideConformation(resConformation);
						this.getNucleotides().add(nuc);
					}//if
				}//ifbasePairs
			}//if
			else{
				//System.out.println(aLine);
			}
		}//for
		return this.getNucleotides();
	}

	public String getPdbId() {
		return pdbId;
	}

	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public int getModelNumber() {
		return modelNumber;
	}

	public void setModelNumber(int modelNumber) {
		this.modelNumber = modelNumber;
	}

	private void setMCASections(File file) {
		/*
		 * This method populates the mcaSections hashmap with each section of
		 * the MC-Annotate output
		 */
		this.mcaSections = new HashMap<String, String>();

		try {
			String fc = FileUtils.readFileToString(file);
			String[] tmp = fc.split("\\nAdjacent stackings\\s\\S+");
			if (tmp.length == 2) {
				String[] tmp2 = tmp[0].split("Residue conformations\\s\\S+");
				String[] tmp3 = tmp[1]
						.split("\\nNon-Adjacent stackings\\s\\S+");
				String[] tmp4 = tmp3[1].split("\\nBase-pairs\\s\\S+");
				String adjacentStackings = tmp3[0].trim();
				String residueConformations = tmp2[1].trim();
				String nonAdjacentStackings = tmp4[0].trim();
				String basePairs = tmp4[1].trim();
				this.mcaSections.put("Residue Conformations",
						residueConformations);
				this.mcaSections.put("Adjacent Stackings", adjacentStackings);
				this.mcaSections.put("Non-Adjacent Stackings",
						nonAdjacentStackings);
				this.mcaSections.put("Base pairs", basePairs);
			}
		} catch (IOException e) {
			System.out.println("Cyborg assimilation is about to conclude");
			e.printStackTrace();
		}
	}

	private int findModelNumber(File file) {
		Pattern aPat = Pattern.compile(".*_M_(\\d*).*");
		Matcher m = aPat.matcher(file.getName().trim());
		if (m.matches()) {
			return Integer.parseInt(m.group(1));
		}

		return 1;
	}// findModelNumber

	private String findPDBId(File file) {
		String filename = file.getName();
		if (filename.toLowerCase().startsWith("pdb")) {
			filename = filename.substring(3);
		}
		return filename.substring(0, 4).toUpperCase();
	}
	public String toString(){
		return "A MCAParsed obj : "+this.getPdbId()+"_M_"+this.getModelNumber();
	}


	public static void main(String[] args) {
	//	File f = new File("/home/pelon/tmp/in/raw/1Y26_M_1.out");
	//	ParseMCAnnotate r = new ParseMCAnnotate(f);

	}

}
