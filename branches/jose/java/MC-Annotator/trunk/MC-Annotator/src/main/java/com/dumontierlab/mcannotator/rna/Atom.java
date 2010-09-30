package com.dumontierlab.mcannotator.rna;

public class Atom {
	/**
	 * The atom label
	 */
	private String atomLabel;
	private double molecularWeight;
	

	/**
	 * Unique PDB id for atom
	 */
	private String atomId;
	
	public Atom(){
		this.setAtomId("-1");
		this.setAtomLabel("-1");
	}
	
	public Atom(String anAtomLabel){
		this.setAtomLabel(anAtomLabel);
	}
	
	public String getAtomLabel() {
		return atomLabel;
	}

	public void setAtomLabel(String atomLabel) {
		this.atomLabel = atomLabel;
	}

	public String getAtomId() {
		return atomId;
	}

	public void setAtomId(String atomId) {
		this.atomId = atomId;
	}

	/**
	 * @return the molecularWeight
	 */
	public double getMolecularWeight() {
		return molecularWeight;
	}

	/**
	 * @param molecularWeight the molecularWeight to set
	 */
	public void setMolecularWeight(double molecularWeight) {
		this.molecularWeight = molecularWeight;
	}
	
}
