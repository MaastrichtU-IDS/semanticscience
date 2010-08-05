package com.semanticscience.banner.bioinfer;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

public class SentenceListGenerator {
	/**
	 * Delimiter
	 */
	String delimiter;
	
	/**
	 * ArrayList with all the sentences in the file
	 */
	ArrayList<String> sentenceList;
	
	/**
	 * File that is being parsed
	 */
	File aFile;
	
	/**
	 * Pass in the delimiter string for the separation
	 * @param aDelimiter
	 */
	public SentenceListGenerator(String aDelimiter, File aFile){
		delimiter = aDelimiter;
		sentenceList = new ArrayList<String>();
		this.setSentenceList(this.parseSentences(aDelimiter , aFile));
	}
	
	public ArrayList<String> parseSentences(String aDelimiter, File file){

		Scanner s;
		try {
			s = new Scanner(file).useDelimiter(aDelimiter);
		 
			while(s.hasNext()){
				String tmp = s.next()+aDelimiter;
				this.sentenceList.add(tmp.trim());
			}
		}
		catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			System.out.println("Error happened");
			e.printStackTrace();
			System.exit(-1);
		}
		
		return this.sentenceList;
	}
	/**
	 * @return the aFile
	 */
	public File getaFile() {
		return aFile;
	}

	/**
	 * @param aFile the aFile to set
	 */
	public void setaFile(File aFile) {
		this.aFile = aFile;
	}

	/**
	 * @return the delimiter
	 */
	public String getDelimiter() {
		return delimiter;
	}

	/**
	 * @param delimiter the delimiter to set
	 */
	public void setDelimiter(String delimiter) {
		this.delimiter = delimiter;
	}

	/**
	 * @return the sentenceList
	 */
	public ArrayList<String> getSentenceList() {
		return sentenceList;
	}

	/**
	 * @param sentenceList the sentenceList to set
	 */
	public void setSentenceList(ArrayList<String> sentenceList) {
		this.sentenceList = sentenceList;
	}

	/**
	 * @param args
	 */
/*	public static void main(String[] args) {
		// TODO Auto-generated method stub
		File f = new File("/home/alison/bioinfer_1.1.1_sentences_only.xml");
		SentenceListGenerator slg = new SentenceListGenerator("</sentence>", f);
		ArrayList<String> s = slg.getSentenceList();
		for(int i=0;i<s.size();i++){
			System.out.println("************");
			System.out.println(s.get(i).toString());
		}
		
	}
*/
}
