package com.dumontierlab.nucleic_acid;

/**
 * An object used to represent the faces (sub-edges) described
 * by the LW+ nomenclature scheme.
 * @author Jose Cruz-Toledo
 */
public class SubEdge {
	/**
	 * The sub edge label i.e.: Ww, Wh, Ss, etc
	 */
	private String subEdgeLabel;
	/**
	 * The atom which is fully contained by the physical boundaries of the subedge
	 */
	private Atom firstAtom;
	/**
	 * (Optional) some subedges extend into multiple atoms
	 */
	private Atom secondAtom;
	
	/**
	 * Default constructor, intializes everything 
	 */
	public SubEdge(){
		setSubEdgeLabel("-1");
		setFirstAtom(new Atom());
		setSecondAtom(new Atom());		
	}
	
	/**
	 * Creates a SubEdge by specifying the subedge label
	 */
	public SubEdge(String aLabel){
		setSubEdgeLabel(aLabel);
		setFirstAtom(new Atom());
		setSecondAtom(new Atom());
	}
	
	/**
	 * Creates a SubEdge by specifying the subedge label and the first-atom label
	 */
	public SubEdge(String aLabel, String firstAtomLabel){
		setSubEdgeLabel(aLabel);
		setFirstAtom(new Atom(firstAtomLabel));
		setSecondAtom(new Atom());
	}
	
	/**
	 * Creates a SubEdge by specifying the subedge label, the first-atom label
	 * and the second-atom label
	 */
	public SubEdge(String aLabel, String firstAtomLabel, String secondAtomLabel){
		setSubEdgeLabel(aLabel);
		setFirstAtom(new Atom(firstAtomLabel));
		setSecondAtom(new Atom(secondAtomLabel));
	}

	
	/**
	 * Creates a SubEdge by specifying the subedge label and the first-atom object
	 */
	public SubEdge(String aLabel, Atom firstAtom){
		setSubEdgeLabel(aLabel);
		setFirstAtom(firstAtom);
		setSecondAtom(new Atom());
	}
	
	/**
	 * Creates a SubEdge by specifying the subedge label, the first-atom object
	 * and the second-atom object
	 */
	public SubEdge(String aLabel, Atom firstAtom, Atom secondAtom){
		setSubEdgeLabel(aLabel);
		setFirstAtom(firstAtom);
		setSecondAtom(secondAtom);
	}
	
	/**
	 * @return the subEdgeLabel
	 */
	public String getSubEdgeLabel() {
		return subEdgeLabel;
	}

	/**
	 * @param subEdgeLabel the subEdgeLabel to set
	 */
	public void setSubEdgeLabel(String subEdgeLabel) {
		this.subEdgeLabel = subEdgeLabel;
	}

	/**
	 * @return the firstAtom
	 */
	public Atom getFirstAtom() {
		return firstAtom;
	}

	/**
	 * @param firstAtom the firstAtom to set
	 */
	public void setFirstAtom(Atom firstAtom) {
		this.firstAtom = firstAtom;
	}

	/**
	 * @return the secondAtom
	 */
	public Atom getSecondAtom() {
		return secondAtom;
	}

	/**
	 * @param secondAtom the secondAtom to set
	 */
	public void setSecondAtom(Atom secondAtom) {
		this.secondAtom = secondAtom;
	}
	
	public String toString(){
		return "SubEdge : "+this.getSubEdgeLabel()+" on atom(s): "+
			" firstAtom:"+ this.getFirstAtom() +"  "+"secondAtom: " + this.getSecondAtom();
	}
	
	
}
