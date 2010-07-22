package com.dumontierlab.nucleic_acid;

/**
 * An object used to represent a stacking interaction between two 
 * nucleotide residues (nucleobases)
 * @author Jose Cruz-Toledo
 * @author William GreenWood
 */
public class BaseStack {
	/**
	 * Four letter PDB code for which this nucleotide belongs to
	 */
	private String pdbId;
	/**
	 * PDB chain to which this nucleobase corresponds to
	 */
	private String chainId;
	/**
	 * Model number in which this nucleobase is found
	 */
	private int modelNumber;
	/**
	 * Set to true if the described stack is adjacent, false otherwise
	 */
	private boolean stackAdjacency;
	/**
	 * Refers to the directionality of the normal vectors on the nucleobase
	 * components of the participating nucleotide residues (upward,inward,etc)
	 */
	private String stackOrientation;
	/**
	 * First participating nucleotide residue that forms part of the stack
	 */
	private Nucleotide firstNucleotide;
	/**
	 * Second participating nucleotide residue that forms part of the stack
	 */
	private Nucleotide secondNucleotide;
	
	/**
	 * Create a BaseStack with 2 nucleotide objects, the adjacency boolean and the orientation
	 */
	public BaseStack(Nucleotide nuc1, Nucleotide nuc2, 
				boolean adjacency, String orientation){
		setFirstNucleotide(nuc1);
		setSecondNucleotide(nuc2);
		setStackAdjacency(adjacency);
		setStackOrientation(orientation);
	}
	
	/**
	 * Create a Base stack using the String based constructors for the participating nucleotides
	 */
	public BaseStack(String pos1, String chain1, String pos2, String chain2,
				boolean adjacency, String orientation){
		this(new Nucleotide(pos1, chain1),
				new Nucleotide(pos2, chain2), 
				adjacency, orientation);
	}
	
	/**
	 * Create a BaseStack with information about only two nucleotides
	 * @param nuc1
	 * @param nuc2
	 */
	public BaseStack(Nucleotide nuc1, Nucleotide nuc2){
		setFirstNucleotide(nuc1);
		setSecondNucleotide(nuc2);
	}
	
	/**
	 * Create a BaseStack with String information about the nucleotide
	 * @param nuc1
	 * @param chain1
	 * @param position1
	 * @param nuc2
	 * @param chain2
	 * @param position2
	 * @param conformation
	 */
	public BaseStack(String nuc1, String chain1, int position1, 
				String nuc2, String chain2, int position2, String conformation){
		this(new Nucleotide(nuc1, chain1, position1, conformation),
			 new Nucleotide(nuc2, chain2, position2, conformation));
	}
	
	/**
	 * @return the pdbId
	 */
	public String getPdbId() {
		return pdbId;
	}
	/**
	 * @param pdbId the pdbId to set
	 */
	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}
	/**
	 * @return the chainId
	 */
	public String getChainId() {
		return chainId;
	}
	/**
	 * @param chainId the chainId to set
	 */
	public void setChainId(String chainId) {
		this.chainId = chainId;
	}
	/**
	 * @return the modelNumber
	 */
	public int getModelNumber() {
		return modelNumber;
	}
	/**
	 * @param modelNumber the modelNumber to set
	 */
	public void setModelNumber(int modelNumber) {
		this.modelNumber = modelNumber;
	}
	/**
	 * @return the stackAdjacency
	 */
	public boolean isStackAdjacency() {
		return stackAdjacency;
	}
	/**
	 * @param stackAdjacency the stackAdjacency to set
	 */
	public void setStackAdjacency(boolean stackAdjacency) {
		this.stackAdjacency = stackAdjacency;
	}
	/**
	 * @return the stackOrientation
	 */
	public String getStackOrientation() {
		return stackOrientation;
	}
	/**
	 * @param stackOrientation the stackOrientation to set
	 */
	public void setStackOrientation(String stackOrientation) {
		this.stackOrientation = stackOrientation;
	}
	/**
	 * @return the firstNucleotide
	 */
	public Nucleotide getFirstNucleotide() {
		return firstNucleotide;
	}
	/**
	 * @param firstNucleotide the firstNucleotide to set
	 */
	public void setFirstNucleotide(Nucleotide firstNucleotide) {
		this.firstNucleotide = firstNucleotide;
	}
	/**
	 * @return the secondNucleotide
	 */
	public Nucleotide getSecondNucleotide() {
		return secondNucleotide;
	}
	/**
	 * @param secondNucleotide the secondNucleotide to set
	 */
	public void setSecondNucleotide(Nucleotide secondNucleotide) {
		this.secondNucleotide = secondNucleotide;
	}
	
	
	
}
