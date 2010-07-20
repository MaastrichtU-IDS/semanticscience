package com.dumontierlab.sequence_generator;

import java.util.HashMap;

public class SequenceCreator {
	/**
	 * Desired length of output sequence
	 */
	public int sequenceLength;
	
	/**
	 * 
	 */
	HashMap<String, Double> proportions;
	
	/**
	 * Molecule type (RNA|DNA)
	 */
	String moltype;
	
	/**
	 * Default constructor, assumes molecule type to be RNA
	 * and to have equal proportions for each nucleotide residue
	 * and an output length of 100 nucleotides
	 */
	public SequenceCreator(){
		//set molecule type
		this.moltype = "RNA";
		
		//set the proportions for each nucleotide
		this.proportions = new HashMap<String, Double>();
		proportions.put("A", 0.25);
		proportions.put("G", 0.25);
		proportions.put("U", 0.25);
		proportions.put("C", 0.25);
		
		//set the length of the output sequence
		this.sequenceLength = 100;
	}
	/**
	 * This constructor assumes a uniform distribution of nucleotide residues
	 * and a sequence length of 100
	 * @param molType
	 */
	public SequenceCreator(String molType){
		//set molecule type
		this.moltype = molType;
		//set the proportions for each nucleotide
		this.proportions = new HashMap<String, Double>();
		proportions.put("A", 0.25);
		proportions.put("G", 0.25);
		proportions.put("U", 0.25);
		proportions.put("C", 0.25);
		//set the length of the output sequence
		this.sequenceLength = 100;
		
	}
	
	/**
	 * 
	 * @param moltype
	 * @param props
	 * @param seqLen
	 */
	public SequenceCreator(String moltype, HashMap<String, Double> props, int seqLen){
		this.moltype = moltype;
		//before setting the input proportions check that they sum to 1
		if(checkProportions(props)){
			this.proportions = props;
		}
		//set sequence length
		this.sequenceLength = seqLen;
	}

	/**
	 * This method traverses the input HashMap and sums up the proportions for each letter
	 * and checks that the summation is 1
	 * @param props
	 * @return
	 */
	private boolean checkProportions(HashMap<String, Double> props) {
		Double summation = 0.0;
		for(String aKey: props.keySet()){
			if(aKey.equals("A") || aKey.equals("U")
			   || aKey.equals("T") || aKey.equals("G")
			   || aKey.equals("C")){
				Double d = props.get(aKey);
				summation += d;
			}
		}
		if(summation.compareTo(1.0) == 0){
			return true;
		}else{
			System.out.println("Incorrect proportions, please check your input parameters!");
			System.out.println("Error 12-77");
			System.exit(-1);
			return false;
		}
	}//checkProportions
	
	
	
	public int getSequenceLength() {
		return sequenceLength;
	}

	public void setSequenceLength(int sequenceLength) {
		this.sequenceLength = sequenceLength;
	}

	public HashMap<String, Double> getProportions() {
		return proportions;
	}

	public void setProportions(HashMap<String, Double> proportions) {
		this.proportions = proportions;
	}

	public String getMoltype() {
		return moltype;
	}

	public void setMoltype(String moltype) {
		this.moltype = moltype;
	}

	public static void main(String[] args){
		//SequenceCreator sc = new SequenceCreator();
		//sc.checkProportions(sc.getProportions());
		
		HashMap<String, Double> hm = new HashMap<String, Double>();
		hm.put("A", 0.3);
		hm.put("C",	0.2);
		hm.put("G", 0.30001);
		hm.put("U", 0.2);
		
		SequenceCreator sc2 = new SequenceCreator("RNA", hm, 65);
	}
	
}
