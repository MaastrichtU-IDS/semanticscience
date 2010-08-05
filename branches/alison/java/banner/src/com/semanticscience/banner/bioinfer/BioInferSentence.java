package com.semanticscience.banner.bioinfer;

import java.util.ArrayList;

public class BioInferSentence {

	private String sentence;

	private ArrayList<ProteinMention> pmList;
	
	public BioInferSentence(){
		
	}
	
	public BioInferSentence(String sentence, ArrayList<ProteinMention> pmList) {
		this.sentence = sentence;
		this.pmList = pmList;	
	}

	/**
	 * @return the pmList
	 */
	public ArrayList<ProteinMention> getPmList() {
		return pmList;
	}

	/**
	 * @param pmList the pmList to set
	 */
	public void setPmList(ArrayList<ProteinMention> pmList) {
		this.pmList = pmList;
	}

	public String getSentence() {
		return sentence;
	}

	public void setSentence(String sentence) {
		this.sentence = sentence;
	}
	
	public String toString() {
		StringBuffer sb = new StringBuffer();
		
		sb.append("Sentence details - ");
		sb.append("Sentence:" + getSentence());
		sb.append(", ");
		sb.append("Protein mention:" + getPmList());
		sb.append(".");
		
		return sb.toString();
	}
	
}
