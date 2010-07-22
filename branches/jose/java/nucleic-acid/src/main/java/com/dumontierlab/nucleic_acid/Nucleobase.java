package com.dumontierlab.nucleic_acid;
/**
 * An object used to represent the nucleobase component of a 
 * nucleotide
 * @author Jose Cruz-Toledo
 * @author William GreenWood
 */
public class Nucleobase {
	/**
	 * The interacting edge for which a (potential) base pairing interaction
	 * is occurring for this nucleobase 
	 */
	private String edgeIdentifier;
	/**
	 * Glycosidic bond rotation parameter takes anti or syn values only
	 */
	private String nucleosideConformation;
	/**
	 * PDB chain to which this nucleobase corresponds to
	 */
	private String chainId;
	/**
	 * One letter code for the nucleotide residue to which this nucleobase 
	 * corresponds to
	 */
	private String residueLabel;
	/**
	 * Position in the PDB chain of this particular nucleobase
	 */
	private int residuePosition;
	/**
	 * Four letter PDB code for which this nucleotide belongs to
	 */
	private String pdbId;
	/**
	 * Model number in which this nucleobase is found
	 */
	private int modelNumber;
	
	/**
	 * Default constructor
	 */
	public Nucleobase(){
		setEdgeIdentifier("-1");
		setNucleosideConformation("-1");
		setChainId("-1");
		setResidueLabel("-1");
		setResiduePosition(-1);
	}
		
	/**
	 * Non default constructor
	 * @param aResLabel the residue Id
	 * @param anEdge the edge identifier
	 * @param aChain the chain id
	 * @param aPosition position in chain
	 * @param aConformation anti or syn conformation
	 */
	public Nucleobase(String aResLabel, String anEdge, String aChain, int aPosition, String aConformation){
		setNucleosideConformation(aConformation);
		setChainId(aChain);
		if(anEdge.equals("+") || anEdge.equals("-")){
			setEdgeIdentifier("W");
		}
		setEdgeIdentifier(anEdge);
		setResidueLabel(aResLabel);
		setResiduePosition(aPosition);
	}
	
	/**
	 * Non default constructor
	 * @param aResidue the residue Id
	 * @param aChain the chain id
	 * @param aPosition position in chain
	 * @param aConformation anti or syn conformation
	 */
	public Nucleobase(String aResidue, String aChain, int aPosition, String aConformation){
		this(aResidue, null, aChain, aPosition, aConformation);
	}
	/**
	 * @return the edgeIdentifier
	 */
	public String getEdgeIdentifier() {
		return edgeIdentifier;
	}

	/**
	 * @param edgeIdentifier the edgeIdentifier to set
	 */
	public void setEdgeIdentifier(String edgeIdentifier) {
		this.edgeIdentifier = edgeIdentifier;
	}

	/**
	 * @return the nucleosideConformation
	 */
	public String getNucleosideConformation() {
		return nucleosideConformation;
	}

	/**
	 * @param nucleosideConformation the nucleosideConformation to set
	 */
	public void setNucleosideConformation(String nucleosideConformation) {
		this.nucleosideConformation = nucleosideConformation;
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
	 * @return the residueLabel
	 */
	public String getResidueLabel() {
		return residueLabel;
	}

	/**
	 * @param residueLabel the residueLabel to set
	 */
	public void setResidueLabel(String residueLabel) {
		this.residueLabel = residueLabel;
	}

	/**
	 * @return the residuePosition
	 */
	public int getResiduePosition() {
		return residuePosition;
	}

	/**
	 * @param residuePosition the residuePosition to set
	 */
	public void setResiduePosition(int residuePosition) {
		this.residuePosition = residuePosition;
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
		return "Nucleobase : "+this.getResidueLabel()+"_chain"
			+this.getChainId()+"_position"+this.getResiduePosition()
			+"_conformation"+this.getNucleosideConformation();
	}

	
}
