package com.dumontierlab.sequence_generator;

import java.util.HashMap;
import java.util.Random;

/**
 * SequenceGenerator creates a random nucleotide sequence of a desired length
 * 
 * @author Jose Cruz-Toledo
 */
public class SequenceGenerator {
	/**
	 * Desired length of output sequence
	 */
	public int sequenceLength;

	/**
	 * Desired probabilities for each nucleotide residue
	 */
	HashMap<String, Double> probabilities;

	/**
	 * Molecule type (RNA|DNA)
	 */
	String moltype;

	/**
	 * String containing all four (A,C,U(T),G) characters in the desired
	 * probabilities from where a random draw will be made to create random
	 * sequences
	 */
	String nucleotidePool;

	/**
	 * Length of the sequence-pool
	 */
	int poolLength = 10000;

	/**
	 * A random nucleotide sequence that follows the required probabilities and
	 * length
	 */
	String randomSequence;

	/**
	 * Default constructor, assumes molecule type to be RNA and to have equal
	 * probabilities for each nucleotide residue and an output length of 100
	 * nucleotides
	 */
	public SequenceGenerator() {
		// set molecule type
		this.moltype = "RNA";

		// set the probabilities for each nucleotide
		this.probabilities = new HashMap<String, Double>();
		probabilities.put("A", 0.25);
		probabilities.put("G", 0.25);
		probabilities.put("U", 0.25);
		probabilities.put("C", 0.25);

		// set the length of the output sequence
		this.sequenceLength = 100;

		// set the nucleotide pool
		this.createPool(probabilities);

		// create the random sequence
		this.createRandomSequence();
	}

	/**
	 * This constructor assumes a uniform distribution of nucleotide residues
	 * and a sequence length of 100
	 * 
	 * @param molType
	 *            specifies the type of molecule RNA|DNA
	 */
	public SequenceGenerator(String molType) {
		// set molecule type
		this.moltype = molType;
		// set the probabilities for each nucleotide
		this.probabilities = new HashMap<String, Double>();
		probabilities.put("A", 0.25);
		probabilities.put("G", 0.25);
		probabilities.put("U", 0.25);
		probabilities.put("C", 0.25);

		// set the length of the output sequence
		this.sequenceLength = 100;

		// set the nucleotide pool
		this.createPool(probabilities);

		// create the random sequence
		this.createRandomSequence();
	}

	/**
	 * Non default constructor
	 * 
	 * @param molType
	 *            specifies the type of molecule RNA|DNA
	 * @param props
	 *            HashMap that specifies the desired probabilities of the
	 *            generated sequence
	 * @param seqLen
	 *            length of the output sequence
	 */
	public SequenceGenerator(String moltype, HashMap<String, Double> props,
			int seqLen) {
		this.moltype = moltype;
		// before setting the input probabilities check that they sum to 1
		if (checkProportions(props)) {
			this.probabilities = props;
		}
		// set sequence length
		this.sequenceLength = seqLen;

		// set the nucleotide pool
		this.createPool(probabilities);

		// create the random sequence
		this.createRandomSequence();
	}

	/**
	 * This method traverses the input HashMap and sums up the probabilities for
	 * each letter and checks that the summation is 1
	 * 
	 * @param props
	 *            HashMap that specifies the desired probabilities of the
	 *            generated sequence
	 * @return returns true if probabilities add to 1
	 */
	private boolean checkProportions(HashMap<String, Double> props) {
		Double summation = 0.0;
		for (String aKey : props.keySet()) {
			if (aKey.equals("A") || aKey.equals("U") || aKey.equals("T")
					|| aKey.equals("G") || aKey.equals("C")) {
				Double d = props.get(aKey);
				summation += d;
			}
		}
		if (summation.compareTo(1.0) == 0) {
			return true;
		} else {
			System.out
					.println("Incorrect probabilities, please check your input parameters!");
			System.out.println("Error 12-77");
			System.exit(-1);
			return false;
		}
	}// checkProportions

	public String getNucleotidePool() {
		return nucleotidePool;
	}

	public void setNucleotidePool(String nucleotidePool) {
		this.nucleotidePool = nucleotidePool;
	}

	public int getPoolLength() {
		return poolLength;
	}

	public void setPoolLength(int poolLength) {
		this.poolLength = poolLength;
	}

	public int getSequenceLength() {
		return sequenceLength;
	}

	public void setSequenceLength(int sequenceLength) {
		this.sequenceLength = sequenceLength;
	}

	public HashMap<String, Double> getProportions() {
		return probabilities;
	}

	public void setProportions(HashMap<String, Double> proportions) {
		this.probabilities = proportions;
	}

	public String getMoltype() {
		return moltype;
	}

	public void setMoltype(String moltype) {
		this.moltype = moltype;
	}

	public String getRandomSequence() {
		return randomSequence;
	}

	public void setRandomSequence(String randomSequence) {
		this.randomSequence = randomSequence;
	}

	/**
	 * This method will populate nucleotidePool according to the probabilities
	 * specified in probabilities
	 */
	public void createPool(HashMap<String, Double> someProportions) {
		HashMap<String, Integer> returnMe = new HashMap<String, Integer>();
		String tmpNucPool = "";
		for (String aKey : someProportions.keySet()) {
			if (aKey.equals("A") || aKey.equals("U") || aKey.equals("T")
					|| aKey.equals("G") || aKey.equals("C")) {

				double d = someProportions.get(aKey);
				int nucleotideRepetitions = (int) (d * this.getPoolLength());

				for (int i = 0; i < nucleotideRepetitions; i++) {
					tmpNucPool += aKey;
				}// for

			}// if
		}// for
		this.setNucleotidePool(tmpNucPool);
	}// createPool

	/**
	 * This method sets a random sequence that follows the same probabilities as
	 * the nucleotide pool
	 */
	public void createRandomSequence() {
		String tmpSeq = "";
		Random randomGenerator = new Random();
		for (int i = 0; i < this.getSequenceLength(); i++) {
			int randomInt = randomGenerator.nextInt(this.getPoolLength());
			tmpSeq += this.getNucleotidePool().charAt(randomInt);
		}
		this.setRandomSequence(tmpSeq);
	}

	public static void main(String[] args) {

		/* Tester */
		
		/*
		 HashMap<String, Double> hm = new HashMap<String, Double>();
		 hm.put("A", 0.4); hm.put("C", 0.2); hm.put("G", 0.3); hm.put("U",0.1);
		 
		 SequenceGenerator sc2 = new SequenceGenerator("RNA", hm, 100);
		 System.out.println(sc2.getRandomSequence());
		 */
	}

}
