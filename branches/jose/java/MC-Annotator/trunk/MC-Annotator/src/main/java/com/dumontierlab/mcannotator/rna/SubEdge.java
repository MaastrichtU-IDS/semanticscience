package com.dumontierlab.mcannotator.rna;

public class SubEdge {
	/**
	 * The sub edge label
	 */
	private String seLabel;
	/**
	 * The "first" atom for this sub edge
	 */
	private Atom firstAtom;
	/**
	 * The "second" atom for this sub edge (optional)
	 */
	private Atom secondAtom;
	
	/**
	 * Default constructor
	 */
	public SubEdge(){
		this.setSelabel("null");
	}
	
	public SubEdge(String seLabel, String firstAtomLabel, String secondAtomLabel){
		this.setFirstAtom(new Atom(firstAtomLabel));
		this.setSecondAtom(new Atom(secondAtomLabel));
		this.setSelabel(seLabel);
	}
	
	public SubEdge(String seLabel){
		this.setFirstAtom(new Atom("-1"));
		this.setSecondAtom(new Atom("-1"));
		this.setSelabel(seLabel);
	}
	
	public SubEdge(String seLabel, String firstAtomLabel){
		this.setSelabel(seLabel);
		this.setFirstAtom(new Atom(firstAtomLabel));
		this.setSecondAtom(new Atom("-1"));
	}
	
	public SubEdge(String seLabel, Atom firstAtom){
		this.setSelabel(seLabel);
		this.setFirstAtom(firstAtom);
		this.setSecondAtom(new Atom("-1"));
	}
	
	public SubEdge(String seLabel, Atom firstAtom, Atom secondAtom){
		this.setSelabel(seLabel);
		this.setFirstAtom(firstAtom);
		this.setSecondAtom(secondAtom);
	}
	
	public void setSelabel(String aLabel){
		seLabel = aLabel;
	}
	
	public void setFirstAtom(Atom anAtom){
		firstAtom = anAtom;
	}
	
	public void setSecondAtom(Atom anAtom){
		secondAtom = anAtom;
	}
	
	public String getSelabel(){
		return seLabel;
	}

	public Atom getFirstAtom() {
		return firstAtom;
	}

	public Atom getSecondAtom() {
		return secondAtom;
	}
	
	
}
