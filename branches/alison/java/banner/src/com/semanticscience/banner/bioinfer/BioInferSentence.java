package com.semanticscience.banner.bioinfer;

public class BioInferSentence {

	private String sentence;

	private ProteinMention pm;
	
	private ProteinComplexMention pcm;

	private String type;
	
	public BioInferSentence(){
		
	}
	
	public BioInferSentence(String sentence, ProteinMention pm, ProteinComplexMention pcm, String type) {
		this.sentence = sentence;
		this.pm = pm;
		this.pcm  = pcm;
		this.type = type;
		
	}

	public String getSentence() {
		return sentence;
	}

	public void setSentence(String sentence) {
		this.sentence = sentence;
	}

	public ProteinMention getPm() {
		return pm;
	}

	public void setPm(ProteinMention pm) {
		this.pm = pm;
	}

	public ProteinComplexMention getPcm() {
		return pcm;
	}

	public void setPcm(ProteinComplexMention pcm) {
		this.pcm = pcm;
	}

	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}	
	
	
	public String toString() {
		StringBuffer sb = new StringBuffer();
		
		sb.append("Sentence details - ");
		sb.append("Sentence:" + getSentence());
		sb.append(", ");
		sb.append("Type:" + getType());
		sb.append(", ");
		sb.append("Protein mention:" + getPm());
		sb.append(", ");
		sb.append("Protein complex mention:" + getPcm());
		sb.append(".");
		
		return sb.toString();
	}
	
}
