package com.dumontierlab.mcannotator.rna;


public class BasePair {

	private String 	strandBPOrientation;
	private Nucleotide 	firstNucleotide;
	private Nucleotide	secondNucleotide;
	private String[] subEdgeArr;
	private String pdbId;
	private int modelNumber;
	
	
	public BasePair(Nucleotide nucleotide1, 
					Nucleotide nucleotide2, 
					String orientation
					){
		this.setStrandBpOrientation(orientation);
		this.setFirstNucleotide(nucleotide1);
		this.setSecondNucleotide(nucleotide2);
	}
	
	public BasePair(String nucleotide1, 
					String position1,
					String chain1,
					String nucleotide2,
					String position2, 
					String chain2,
					String strandBPOrient,
					String baseConformation
					){
		this(new Nucleotide(nucleotide1, position1, chain1, baseConformation), 
			 new Nucleotide(nucleotide2, position2, chain2, baseConformation), strandBPOrient);
	}
	
	public BasePair(String nucLabel1,
					String pos1,
					String chain1,
					String nucLabel2,
					String pos2,
					String chain2,
					String glycoOrientation
					){
		this(new Nucleotide(nucLabel1, pos1, chain1),
			 new Nucleotide(nucLabel2, pos2, chain2), glycoOrientation);
	}

	public String getPdbId() {
		return pdbId;
	}

	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public int getModelNumber() {
		return modelNumber;
	}

	public void setModelNumber(int modelNumber) {
		this.modelNumber = modelNumber;
	}

	public String[] getSubEdgeArr() {
		return subEdgeArr;
	}

	public void setSubEdgeArr(String[] subEdgeArr) {
		this.subEdgeArr = subEdgeArr;
	}

	public String getStrandBPOrientation(){
		return this.strandBPOrientation;
	}
	public Nucleotide getFirstNucleotide() {
		return firstNucleotide;
	}
	public Nucleotide getSecondNucleotide() {
		return secondNucleotide;
	}
	
	public void setStrandBpOrientation(String str){
		this.strandBPOrientation = str;
	}

	public void setFirstNucleotide(Nucleotide nb){
		this.firstNucleotide = nb;
	}
	
	public void setSecondNucleotide(Nucleotide nb){
		this.secondNucleotide = nb;
	}
	
	public String toString(){
		String returnMe = "Nucleotide base pair: ("+firstNucleotide.getResidueLabel()+"-"+secondNucleotide.getResidueLabel()+")["+
			strandBPOrientation+"] residues: "+firstNucleotide.getChainID()+
			firstNucleotide.getResiduePosition()+"-"+secondNucleotide.getChainID()+secondNucleotide.getResiduePosition();
		String [] subedges = this.getSubEdgeArr();
		for(int i=0;i<subedges.length;i++){
			returnMe += " "+subedges[i];
		}
		return returnMe;
	}
	
}

