package com.dumontierlab.nucleic_acid;
/**
 * An object used to represent the nucleotide residue component of a 
 * nucleic acid
 * @author Jose Cruz-Toledo
 * @author William GreenWood
 */
public class Nucleotide {
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
	 * temporary house-keeping residue position (for melding chains together) 
	 * @See {@link #residueLabel}
	 */
	private int residuePositionTemp;
	/**
	 * Puckering atom of this nucleotide residue
	 */
	private String puckerAtom;//C3p
	/**
	 * Quality of puckering atom endo | exo
	 */
	private String puckerQuality;

	/**
	 * Default constructor, initialize everything
	 */
	public Nucleotide(){
		setNucleosideConformation("-1");
		setChainId("-1");
		setResidueLabel("-1");
		setResiduePosition(-1);
		setResiduePositionTemp(-1);
		setPuckerAtom("-1");
		setPuckerQuality("-1");
	}
	
	/**
	 * Non default constructor
	 * @param residueLabel
	 * @param chain
	 * @param position
	 * @param conformation
	 */
	public Nucleotide(String residueLabel, String chain, int position, String conformation){
		setChainId(chain);
		setNucleosideConformation(conformation);
		setResidueLabel(residueLabel);
		setResiduePosition(position);
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
	 * @return the residuePositionTemp
	 */
	public int getResiduePositionTemp() {
		return residuePositionTemp;
	}

	/**
	 * @param residuePositionTemp the residuePositionTemp to set
	 */
	public void setResiduePositionTemp(int residuePositionTemp) {
		this.residuePositionTemp = residuePositionTemp;
	}

	/**
	 * @return the puckerAtom
	 */
	public String getPuckerAtom() {
		return puckerAtom;
	}

	/**
	 * @param puckerAtom the puckerAtom to set
	 */
	public void setPuckerAtom(String puckerAtom) {
		this.puckerAtom = puckerAtom;
	}

	/**
	 * @return the puckerQuality
	 */
	public String getPuckerQuality() {
		return puckerQuality;
	}

	/**
	 * @param puckerQuality the puckerQuality to set
	 */
	public void setPuckerQuality(String puckerQuality) {
		this.puckerQuality = puckerQuality;
	}
	
	

}
