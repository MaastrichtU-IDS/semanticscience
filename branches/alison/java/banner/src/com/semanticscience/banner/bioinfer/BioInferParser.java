package com.semanticscience.banner.bioinfer;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.ByteArrayInputStream;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.ListIterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class BioInferParser{

	DocumentBuilder builder;
	
	Document doc;
	
	public BioInferParser(){
		try {
			builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
		} catch (ParserConfigurationException e) {
			System.out.println("Builder problem");
			e.printStackTrace();
		}
	}
	
	/**
	 * This method parses BioInfer sentence XML to extract tokens labelled as "Individual_protein" 
	 * and generates BioInferSentence objects that specify the extracted Protein Mentions
	 * 
	 * @param sentenceXML a String containing the XML of a single sentence
	 * @param elementTag a String specifying the XML tag of the element containing the token IDs of potential protein mentions - in the case of BioInfer XML it is "entity"
	 * @param elementAttribute a String specifying the attribute containing the original text of the sentence - the case of BioInfer XML it is "origText"
	 * @return s a BioInferSentence
	 */
	public BioInferSentence parseSentenceXML(String sentenceXML, String elementTag, String elementAttribute) {
		InputStream is;
		try {
			is = new ByteArrayInputStream(sentenceXML.getBytes("UTF-8"));
			try {
				this.setDoc(this.getBuilder().parse(is));
			} catch (SAXException e) {
				System.out.println("SAX parser problem");
				e.printStackTrace();
			} catch (IOException e) {
				System.out.println("IO problem");
				e.printStackTrace();
			}
		} catch (UnsupportedEncodingException e1) {
			System.out.println("Unsupported encoding exception");
			e1.printStackTrace();
		}
		
		Element sentenceElement = this.getDoc().getDocumentElement();
		   
	    NodeList entities = sentenceElement.getElementsByTagName(elementTag);
	    
	    ArrayList<ArrayList<String>> pmTokenList = getProteinMentionSubTokenIdsFromList(entities);
	    
	    ArrayList<ProteinMention> pmList = getProteinMentionsFromTokenIds(pmTokenList, sentenceElement);
	      
		BioInferSentence s = new BioInferSentence(sentenceElement.getAttribute(elementAttribute), pmList);
		
		return s;
	}
	
	/**
	 * This method generates ProteinMention objects from a list of Token IDs specifying text labelled
	 * as "Individual_protein" in a single sentence
	 * 
	 * @param subTokenList an ArrayList of ArrayLists of Token IDs labeled as "Individual_protein" by BioInfer
	 * @param sentenceElement sentence XML in DOM
	 * @return tmpPms an ArrayList of ProteinMention objects
	 */
	public ArrayList<ProteinMention> getProteinMentionsFromTokenIds(ArrayList<ArrayList<String>> subTokenList, Element sentenceElement){
		
		ArrayList<ProteinMention> tmpPms = new ArrayList<ProteinMention>();
		ListIterator<ArrayList<String>> li = subTokenList.listIterator();
		
		while(li.hasNext()){
			ProteinMention pm = getProteinMentionFromTokenIds(li.next(), sentenceElement);
			if(pm != null){
				tmpPms.add(pm);
			}
		}//while
		return tmpPms;
	}
	
	/**
	 * This method generates a single ProteinMention from a list of Token IDs indicating
	 * a single "Individual_protein" annotated section of text from a single sentence
	 * 
	 * @param tokenIds an ArrayList of Strings specifying the Token IDs of a single protein mention from a single sentence
	 * @param sentenceElement sentence XML in DOM
	 * @return tmpPm a single ProteinMention
	 */
	public ProteinMention getProteinMentionFromTokenIds(ArrayList<String> tokenIds, Element sentenceElement){
		
		ArrayList<Integer> tokenList = getTokenNumbers(tokenIds);
		
		String tokenLabel = getTokenLabel(tokenIds, sentenceElement);
		
		ProteinMention tmpPm;
		
		if(!(tokenLabel.isEmpty())){
			tmpPm = new ProteinMention(tokenList, tokenLabel);
		} else {
			tmpPm = null;
		}
		return tmpPm;
	}
	
	/**
	 * This method generates a label for the set of tokens specifying a ProteinMention,
	 * using the text corresponding to the Token IDs
	 * 
	 * @param tokenIds an ArrayList of Token IDs indicating the location of text labelled as an "Individual_protein" by BioInfer
	 * @param sentenceElement sentence XML in DOM
	 * @return tmpLabel a String containing the tokens specified by the Token IDs indicated as an "Individual_protein"
	 */
	public String getTokenLabel(ArrayList<String> tokenIds, Element sentenceElement){
		
		StringBuffer tmpLabel = new StringBuffer();	
		
		NodeList subtokens = sentenceElement.getElementsByTagName("subtoken");
		
		for(int j=0;j<tokenIds.size();j++){
			for(int i=0;i<subtokens.getLength();i++){
				Element e = (Element) subtokens.item(i);
				if(e.getAttribute("id").equals(tokenIds.get(j))){
					String text = e.getAttribute("text");
					tmpLabel.append(text+" ");
				}//if
			}//for
		}//for
		
		return tmpLabel.toString().trim();
	}
	
	/**
	 * This method extracts the position of the tokens that specify a protein mention from the Token IDs
	 * 
	 * @param tokenIds an ArrayList of Token IDs specifying protein mentions, specified in the BioInfer XML
	 * @return tmpTokens an ArrayList of Integers specifying the position of the tokens that make up the protein mention in the sentence
	 */
	public ArrayList<Integer> getTokenNumbers(ArrayList<String> tokenIds){
		
		String pattern = "\\w+\\.\\d+\\.(\\d+)\\.\\d+";
		
		Pattern p = Pattern.compile(pattern);
		
		ArrayList<Integer> tmpTokens = new ArrayList<Integer>();
		
		ArrayList<Integer> tokens = new ArrayList<Integer>();
		
		for(int i=0;i<tokenIds.size();i++){
			Matcher matcher = p.matcher(tokenIds.get(i));
			while(matcher.find()){
				Integer tokenNumber =  Integer.parseInt(matcher.group(1));	
				if(!(tmpTokens.contains(tokenNumber))){
					tmpTokens.add(tokenNumber);
				}//if
			}//while
		}//for
		
		if(tmpTokens.size() == 1){
			tokens.add(tmpTokens.get(0));
			tokens.add(tmpTokens.get(0)+1);
		} else if(tmpTokens.size() > 1) {
			tokens.add(tmpTokens.get(0));
			tokens.add(tmpTokens.get(tmpTokens.size()-1)+1);
		}//elseif
		
		return tokens;
	}
	
	/**
	 * This method extracts all of the Token IDs specifying a protein mention from a single BioInfer sentence
	 * 
	 * @param entities a NodeList containing all "entity" XML from the BioInfer XML
	 * @return entitiesNstIds an ArrayList of ArrayLists of Strings specifying the Token IDs of text labelled as "Individual_protein" in the BioInfer corpus
	 */
	public ArrayList<ArrayList<String>> getProteinMentionSubTokenIdsFromList(NodeList entities){
		
		ArrayList<ArrayList<String>> entitiesNstIds = new ArrayList<ArrayList<String>>();
		
		for(int m=0;m<entities.getLength();m++){
			Element e = (Element) entities.item(m);
			ArrayList<String> elementNstIds = getProteinMentionSubTokenIds(e);
			entitiesNstIds.add(elementNstIds);
		}
		
		return entitiesNstIds;
	}
	
	/**
	 * This method extracts the Token IDs of all protein mentions labelled
	 * as "Individual_protein" in a single sentence from the BioInfer XML
	 * 
	 * @param entity a DOM Element specifying a single entity in a BioInfer sentence
	 * @return an ArrayList of Strings specifying the Token IDs of a single protein mention from a BioInfer sentence
	 */
	public ArrayList<String> getProteinMentionSubTokenIds(Element entity){
		
		ArrayList<String> nstIds = new ArrayList<String>();
		
		String type = entity.getAttribute("type");
		
		if(type.equals("Individual_protein")){
			NodeList nestedsubtokens = entity.getElementsByTagName("nestedsubtoken");
			for(int k=0;k<nestedsubtokens.getLength();k++){
				Element e = (Element) nestedsubtokens.item(k);
				String id = e.getAttribute("id");
				nstIds.add(id);
			}//for
		}//if
		return nstIds;
	}

	/**
	 * @return the builder
	 */
	public DocumentBuilder getBuilder() {
		return builder;
	}

	/**
	 * @param builder the builder to set
	 */
	public void setBuilder(DocumentBuilder builder) {
		this.builder = builder;
	}

	/**
	 * @return the doc
	 */
	public Document getDoc() {
		return doc;
	}

	/**
	 * @param doc the doc to set
	 */
	public void setDoc(Document doc) {
		this.doc = doc;
	}
	
	public static void main(String[] args){
		File f = new File("/home/alison/bioinfer_1.1.1_sentences_only.xml");
		SentenceListGenerator sgl = new SentenceListGenerator("</sentence>", f);
		BioInferParser bp = new BioInferParser();
		ArrayList<String> s = sgl.getSentenceList();
		for(int i=0;i<s.size();i++){
			BioInferSentence bis = bp.parseSentenceXML(s.get(i).toString(), "entity", "origText");
			System.out.println(bis);
		}
		
	}
	
	
}
