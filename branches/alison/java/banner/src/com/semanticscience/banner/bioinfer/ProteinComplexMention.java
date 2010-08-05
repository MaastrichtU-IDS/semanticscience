package com.semanticscience.banner.bioinfer;

import java.util.List;

public class ProteinComplexMention {

	private List<Integer> tokens;
	
	private String label;

	public ProteinComplexMention(){
		
	}
	
	public ProteinComplexMention(List<Integer> tokens, String label){
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
}
