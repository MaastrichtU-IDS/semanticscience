package com.dumontierlab.nucleic_acid;


/**
 * This class describes an atom object
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

		
	/**
	 * @return the atomLabel
	 */
	public String getAtomLabel() {
		return atomLabel;
	}

	/**
	 * @param atomLabel the atomLabel to set
	 */
	public void setAtomLabel(String atomLabel) {
		this.atomLabel = atomLabel;
	}

	/**
	 * @return the atomId
	 */
	public String getAtomId() {
		return atomId;
	}

	/**
	 * @param atomId the atomId to set
	 */
	public void setAtomId(String atomId) {
		this.atomId = atomId;
	}

	public String toString(){
		return "Atom : "+ this.getAtomLabel()
			+" "+ this.getAtomId();
	}

}
