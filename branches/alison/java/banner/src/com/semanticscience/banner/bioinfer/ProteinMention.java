package com.semanticscience.banner.bioinfer;

import java.util.List;

public class ProteinMention {
	
	private List<Integer> tokens;
	private String label;
	
	public ProteinMention(){
		
	}
	
	public ProteinMention(List<Integer> tokens, String label){
		this.tokens = tokens;
		this.label = label;	
	}

	public List<Integer> getTokens() {
		return tokens;
	}
	
	public void setTokens(List<Integer> tokens) {
		this.tokens = tokens;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}
	
	public String toString(){
		
		StringBuffer sb = new StringBuffer();
		
		sb.append("ProteinMention details - ");
		sb.append("Label:" + getLabel());
		sb.append(", ");
		sb.append("Tokens:" + getTokens());
		sb.append(".");
		
		return sb.toString();
	}//toString
}
