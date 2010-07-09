package com.dumontierlab.mcannotator.rna;


public class Stack {
	private String pdbId;
	private String modelNumber;
	private boolean stackAdjacency;
	private String stackOrientation;
	private Nucleotide firstNucleotide;
	private Nucleotide secondNucleotide;
	
	public Stack(Nucleotide nuc1, 
				 Nucleotide nuc2,
				 boolean adjacency,
				 String orientation){
		this.setFirstNucleotide(nuc1);
		this.setSecondNucleotide(nuc2);
		this.setStackAdjacency(adjacency);
		this.setStackOrientation(orientation);
	}
	
	public Stack(String pos1,
			 	 String chain1,
			 	 String pos2,
			 	 String chain2,
			 	 boolean adjacency,
			 	 String orientation){
		this(new Nucleotide(pos1, chain1),
			 new Nucleotide(pos2, chain2),
			 adjacency,
			 orientation);
	}

	public Nucleotide getFirstNucleotide() {
		return firstNucleotide;
	}

	public void setFirstNucleotide(Nucleotide firstNucleotide) {
		this.firstNucleotide = firstNucleotide;
	}

	public Nucleotide getSecondNucleotide() {
		return secondNucleotide;
	}

	public void setSecondNucleotide(Nucleotide secondNucleotide) {
		this.secondNucleotide = secondNucleotide;
	}

	public String getPdbId() {
		return pdbId;
	}

	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public String getModelNumber() {
		return modelNumber;
	}

	public void setModelNumber(String modelNumber) {
		this.modelNumber = modelNumber;
	}

	public boolean isStackAdjacency() {
		return stackAdjacency;
	}

	public void setStackAdjacency(boolean stackAdjacency) {
		this.stackAdjacency = stackAdjacency;
	}

	public String getStackOrientation() {
		return stackOrientation;
	}

	public void setStackOrientation(String stackOrientation) {
		this.stackOrientation = stackOrientation;
	}
	public String toString(){
		return "Stack :"+this.getPdbId()+"_m"+this.getModelNumber()+"_r1"+this.getFirstNucleotide()+"_r2"+this.getSecondNucleotide()+"_dir"+this.getStackOrientation();
	}

}
