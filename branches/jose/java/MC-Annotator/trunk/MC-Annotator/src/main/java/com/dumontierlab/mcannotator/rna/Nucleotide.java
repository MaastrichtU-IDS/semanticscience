package com.dumontierlab.mcannotator.rna;

public class Nucleotide {
	// A11 : G C3p_endo syn
	private String nucleotideConformation;// syn || anti
	private String chainID;// A
	private String residueLabel;// G
	private String residuePosition;// 11
	private String puckerAtom;// C3p
	private String puckerQuality;// endo
	private String pdbId;

	public String getPdbId() {
		return pdbId;
	}

	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public Nucleotide(String aPos, String aChain) {
		this.setResiduePosition(aPos);
		this.setChainID(aChain);
	}

	public Nucleotide(String aRes, String aPos, String aChain) {
		this.setChainID(aChain);
		this.setResidueLabel(aRes);
		this.setResiduePosition(aPos);
	}

	public Nucleotide(String aResidue, String aPosition, String aChain,
			String aConformation) {
		this.setNucleotideConformation(aConformation);
		this.setChainID(aChain);
		this.setResidueLabel(aResidue);
		this.setResiduePosition(aPosition);
	}

	public String getPuckerAtom() {
		return puckerAtom;
	}

	public void setPuckerAtom(String puckerAtom) {
		this.puckerAtom = puckerAtom;
	}

	public String getPuckerQuality() {
		return puckerQuality;
	}

	public void setPuckerQuality(String puckerQuality) {
		this.puckerQuality = puckerQuality;
	}

	public String getNucleotideConformation() {
		return nucleotideConformation;
	}

	public String getChainID() {
		return chainID;
	}

	public String getResidueLabel() {
		return residueLabel;
	}

	public String getResiduePosition() {
		return residuePosition;
	}

	public void setNucleotideConformation(String nucleotideConformation) {
		this.nucleotideConformation = nucleotideConformation;
	}

	public void setChainID(String chainID) {
		this.chainID = chainID;
	}

	public void setResidueLabel(String aResLabel) {
		this.residueLabel = aResLabel;
	}

	public void setResiduePosition(String residuePosition) {
		this.residuePosition = residuePosition;
	}

	public String toString() {
		return "Nucleotide residue: " + this.getPdbId() + "_chain"
				+ this.getChainID() + "_label" + this.getResidueLabel()
				+ "_residuePos" + this.getResiduePosition() + " PA:"
				+ this.getPuckerAtom() + " PQ:" + this.getPuckerQuality()
				+ " RC"+this.getNucleotideConformation();
	}
}
