package com.dumontierlab.mcannotator.rna;

public class Nucleobase {

	private String nucleosideConformation;
	private String chainID;
	private String edgeIdentifier;
	private String residueIdentifier;
	private String residuePosition;
	
	public Nucleobase(String aResidue, String anEdge, String aChain, String aPosition,
			String aConformation){
		nucleosideConformation = aConformation;
		chainID = aChain;
		
		if (anEdge.equals("+") || anEdge.equals("-")){
			anEdge = "W";
		}
		edgeIdentifier = anEdge;
		residueIdentifier = aResidue;
		residuePosition = aPosition;
	}
	
	public Nucleobase(String aResidue, String aChain, String aPosition, String aConformation){
		this(aResidue, null, aChain, aPosition, aConformation);
	}
	
	public String getNucleosideConformation(){
		return nucleosideConformation;
	}
	
	public String getChainID() {
		return chainID;
	}
	
	public String getEdgeIdentifier() {
		return edgeIdentifier;
	}

	public String getResidueIdentifier(){
		return residueIdentifier;
	}
	
	public String getResiduePosition() {		
		return residuePosition;
	}
	
	public String toString(){
		return "";
	}
}
