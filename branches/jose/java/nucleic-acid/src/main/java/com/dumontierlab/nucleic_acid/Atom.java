package com.dumontierlab.nucleic_acid;


/**
 * This class describes an atom
 * @author Jose Cruz-Toledo
 *
 */
public class Atom {
	/**
	 * The atom label
	 */
	private String atomLabel;
	
	/**
	 * Unique PDB id for atom
	 */
	private String atomId;
	
	/**
	 * Default constructor
	 */
	public Atom(){
		setAtomId("-1");
		setAtomLabel("-1");
	}
	
	/**
	 * Non default constructor allows user to set their own atom label
	 * @param anAtomLabel an atom label
	 */
	public Atom(String anAtomLabel){
		setAtomLabel(anAtomLabel);
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
	

}
