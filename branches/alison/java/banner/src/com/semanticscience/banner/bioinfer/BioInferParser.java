package com.semanticscience.banner.bioinfer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

public class BioInferParser extends DefaultHandler {

	List<BioInferSentence> bioInferSentences;
	
	private String tempString;
	
	private BioInferSentence tempSentence;
	
	public BioInferParser(){
		bioInferSentences = new ArrayList();
	}
	
	public void runExample() {
		parseDocument();
		//printData();
	}

	private void parseDocument() {
		
		//get a factory
		SAXParserFactory spf = SAXParserFactory.newInstance();
		try {
		
			//get a new instance of parser
			SAXParser sp = spf.newSAXParser();
			
			//parse the file and also register this class for call backs
			sp.parse("bioinfer_1.1.1.xml", this);
			
		}catch(SAXException se) {
			se.printStackTrace();
		}catch(ParserConfigurationException pce) {
			pce.printStackTrace();
		}catch (IOException ie) {
			ie.printStackTrace();
		}
	}

	//Event Handlers
	public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		//reset
		tempString = "";
		if(qName.equalsIgnoreCase("Sentence")) {
			//create a new instance of employee
			tempSentence = new BioInferSentence();
			tempSentence.setType(attributes.getValue("type"));
		}
	}
	

	public void characters(char[] ch, int start, int length) throws SAXException {
		tempString = new String(ch,start,length);
	}
	
	public void endElement(String uri, String localName, String qName) throws SAXException {

		if(qName.equalsIgnoreCase("Sentence")) {
			//add it to the list
			bioInferSentences.add(tempSentence);
			
		}/**else if (qName.equalsIgnoreCase("Token")) {
			tempSentence.setToken(tempString);
		}**/
		
	}
	
	public static void main(String[] args){
		BioInferParser bip = new BioInferParser();
		bip.runExample();
	}
	
}
