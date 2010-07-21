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
	private String residueId;
	/**
	 * Position in the PDB chain of this particular nucleobase
	 */
	private int residuePosition;
	
	/**
	 * Default constructor
	 */
	public Nucleobase(){
		edgeIdentifier ="-1";
		nucleosideConformation = "-1";
		chainId = "-1";
		residueId = "-1";
		residuePosition = -1;
	}
	
		
	/**
	 * Non default constructor
	 * @param aResidue the residue Id
	 * @param anEdge the edge identifier
	 * @param aChain the chain id
	 * @param aPosition position in chain
	 * @param aConformation anti or syn conformation
	 */
	public Nucleobase(String aResidue, String anEdge, String aChain, int aPosition, String aConformation){
		nucleosideConformation = aConformation;
		chainId = aChain;
		if(anEdge.equals("+") || anEdge.equals("-")){
			anEdge = "W";
		}
		edgeIdentifier = anEdge;
		residueId = aResidue;
		residuePosition = aPosition;
		
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
	 * @return the residueId
	 */
	public String getResidueId() {
		return residueId;
	}

	/**
	 * @param residueId the residueId to set
	 */
	public void setResidueId(String residueId) {
		this.residueId = residueId;
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

	
}
