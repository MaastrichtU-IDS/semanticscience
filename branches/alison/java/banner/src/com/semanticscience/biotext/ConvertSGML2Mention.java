/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.biotext;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tagging.MentionType;
import com.semanticscience.banner.tokenization.Token;

public class ConvertSGML2Mention  {

	/**
     * @param id
     * @param sentence
     * @param tagger
     * @param mentionOutputFile
     */
	private static void outputMentions(Sentence sentence,
			PrintWriter diseaseMentionOutputFile, PrintWriter treatmentMentionOutputFile) {
		List<Token> tokens = sentence.getTokens();
		int charCount = 0;
		for (int i = 0; i < tokens.size(); i++) {
			List<Mention> mentions = sentence.getMentions(tokens.get(i));
			assert mentions.size() == 0 || mentions.size() == 1;
			Mention mention = null;
			if (mentions.size() > 0)
				mention = mentions.get(0);
			if (mention != null && i == mention.getStart()) {
				if (mention.getType() == MentionType.getType("DISEASE"))
				{
					diseaseMentionOutputFile.print(sentence.getTag());
					diseaseMentionOutputFile.print("|");
					diseaseMentionOutputFile.print(charCount);
					diseaseMentionOutputFile.print(" ");
				}
				else
				{
					treatmentMentionOutputFile.print(sentence.getTag());
					treatmentMentionOutputFile.print("|");
					treatmentMentionOutputFile.print(charCount);
					treatmentMentionOutputFile.print(" ");
				}
			}
			charCount += tokens.get(i).length();
			if (mention != null && i == mention.getEnd() - 1) {
				if (mention.getType() == MentionType.getType("DISEASE"))
				{
					diseaseMentionOutputFile.print(charCount - 1);
					diseaseMentionOutputFile.print("|");
					diseaseMentionOutputFile.println(mention.getText());
				}
				else
				{
					treatmentMentionOutputFile.print(charCount - 1);
					treatmentMentionOutputFile.print("|");
					treatmentMentionOutputFile.println(mention.getText());
				}
			}
		}
	}

	/**
     * @param args
     */
	public static void main(String[] args) throws IOException {
		String sentenceFilename = args[0];
		String diseaseMentionFilename = args[1];
		String treatmentMentionFilename = args[2];
		String rawTextFilename = args[3];
		BufferedReader sentenceFile = new BufferedReader(new FileReader(
				sentenceFilename));
		PrintWriter diseaseMentionFile = new PrintWriter(new BufferedWriter(
				new FileWriter(diseaseMentionFilename)));
		PrintWriter treatmentMentionFile = new PrintWriter(new BufferedWriter(
				new FileWriter(treatmentMentionFilename)));
		PrintWriter rawTextFile = new PrintWriter(new BufferedWriter(
				new FileWriter(rawTextFilename)));
		ArrayList<Sentence> sentences = new ArrayList<Sentence>();
		String line = sentenceFile.readLine();
		int id = 1;
		while (line != null) {
			Sentence sentence = Sentence.loadFromXML(Integer.toString(id), line
					.trim());
			sentences.add(sentence);
			outputMentions(sentence, diseaseMentionFile, treatmentMentionFile);
			rawTextFile.println(id + " " + sentence.getText());
			line = sentenceFile.readLine();
			id++;
		}
		sentenceFile.close();
		diseaseMentionFile.close();
		treatmentMentionFile.close();
		rawTextFile.close();
	}

}