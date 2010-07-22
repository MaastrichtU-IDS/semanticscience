package com.dumontierlab.nucleic_acid;
/**
 * An object used to represent a nucleotide base pair component of a 
 * nucleic acid
 * @author Jose Cruz-Toledo
 * @author William GreenWood
 */
public class BasePair {
	/**
	 * Strand orientation of the base pair (parallel|antiparallel)
	 */
	private String strandBPOrientation;
	/**
	 * Nucleotide residue #1 participating in the base pair
	 */
	private Nucleotide firstNucleotide;
	/**
	 * Nucleotide residue #2 participating in the base pair
	 */
	private Nucleotide secondNucleotide;
	/**
	 * An array of participating subEdges
	 */
	private String[] subEdgeArr;
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
	 * Create a base pair by specifying both Nucleotides and the base pair orientation
	 * @param nuc1 first Nucleotide
	 * @param nuc2 second Nucleotide
	 * @param orientation base pair orientation
	 */
	public BasePair(Nucleotide nuc1, Nucleotide nuc2, String orientation){
		setStrandBPOrientation(orientation);
		setFirstNucleotide(nuc1);
		setSecondNucleotide(nuc2);
	}
	
	/**
	 * Create a base pair by specifying nucleotide info as strings
	 * @param nuc1 first Nucleotide label
	 * @param pos1 first Nucleotide position
	 * @param chain1 chain belonging to the first nucleotide
	 * @param nuc2 second Nucleotide label
	 * @param pos2 second Nucleotide position
	 * @param chain2 chain belonging to the second nucleotide
	 * @param strandBPOrientation directionality of base pair (parallel|antiparallel)
	 * @param baseConformation
	 */
	public BasePair(String nuc1, String pos1, String chain1,
				String nuc2, String pos2, String chain2, 
				String strandBPOrientation, String baseConformation){
		this(new Nucleotide(nuc1, pos1, chain1, baseConformation),
			 new Nucleotide(nuc2, pos2, chain2, baseConformation),
			 strandBPOrientation);
	}
	
	/**
	 * Create a base pair by specifying nucleotide info as strings
	 * @param nuc1 first Nucleotide label
	 * @param pos1 first Nucleotide position
	 * @param chain1 chain belonging to the first nucleotide
	 * @param nuc2 second Nucleotide label
	 * @param pos2 second Nucleotide position
	 * @param chain2 chain belonging to the second nucleotide
	 * @param strandBPOrientation directionality of base pair (parallel|antiparallel)
	 * @param baseConformation
	 */
	public BasePair(String nuc1, String pos1, String chain1,
					String nuc2, String pos2, String chain2,
					String glycoOrient){
		this(new Nucleotide(nuc1, pos1, chain1, ""), 
				new Nucleotide(nuc2, pos2, chain2,""), glycoOrient);
	}
	
	/**
	 * @return the strandBPOrientation
	 */
	public String getStrandBPOrientation() {
		return strandBPOrientation;
	}
	/**
	 * @param strandBPOrientation the strandBPOrientation to set
	 */
	public void setStrandBPOrientation(String strandBPOrientation) {
		this.strandBPOrientation = strandBPOrientation;
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
	/**
	 * @return the subEdgeArr
	 */
	public String[] getSubEdgeArr() {
		return subEdgeArr;
	}
	/**
	 * @param subEdgeArr the subEdgeArr to set
	 */
	public void setSubEdgeArr(String[] subEdgeArr) {
		this.subEdgeArr = subEdgeArr;
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

	public String toString(){
		String returnMe = "Nucleotide base pair: ("+this.getFirstNucleotide().getResidueLabel()+
						  "-"+this.getSecondNucleotide().getResidueLabel()+")["+
						  this.getStrandBPOrientation()+"] residues: "+this.getFirstNucleotide().getChainId()+
						  this.getFirstNucleotide().getResiduePosition()+"-"+
						  this.getSecondNucleotide().getChainId()+secondNucleotide.getResiduePosition();
		
		String [] subedges = this.getSubEdgeArr();
		for(int i=0;i<subedges.length;i++){
			returnMe += " "+subedges[i];
		}
		return returnMe;
	}

}
