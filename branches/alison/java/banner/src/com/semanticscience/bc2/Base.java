/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tagging.MentionType;
import com.semanticscience.banner.tokenization.Token;
import com.semanticscience.banner.tokenization.Tokenizer;

public abstract class Base {

	protected static HashMap<String, LinkedList<Base.Tag>> getTags(BufferedReader tagFile) throws IOException
	{
	    HashMap<String, LinkedList<Base.Tag>> tags = new HashMap<String, LinkedList<Base.Tag>>();
	
	    String line = tagFile.readLine();
	    while (line != null)
	    {
	        String[] split = line.split(" |\\|");
	        LinkedList<Base.Tag> tagList = tags.get(split[0]);
	        if (tagList == null)
	            tagList = new LinkedList<Base.Tag>();
	        Base.Tag tag = new Base.Tag(Integer.parseInt(split[1]), Integer.parseInt(split[2]));
	        Iterator<Base.Tag> tagIterator = tagList.iterator();
	        boolean add = true;
	        while (tagIterator.hasNext() && add)
	        {
	            Base.Tag tag2 = tagIterator.next();
	            // FIXME Determine what to do for when A.contains(B) or
				// B.contains(A)
	            if (tag.contains(tag2))
	                tagIterator.remove();
	            // add = false;
	            else if (tag2.contains(tag))
	                add = false;
	            // tagIterator.remove();
	            else
            		assert !tag.overlaps(tag2);
	        }
	        if (add)
	        {
	            tagList.add(tag);
	            tags.put(split[0], tagList);
	        }
	        line = tagFile.readLine();
	    }
	    return tags;
	}
	
	protected static HashMap<String, LinkedList<Base.Tag>> getAlternateTags(BufferedReader tagFile) throws IOException
	{
	    HashMap<String, LinkedList<Base.Tag>> tags = new HashMap<String, LinkedList<Base.Tag>>();
	
	    String line = tagFile.readLine();
	    while (line != null)
	    {
	        String[] split = line.split(" |\\|");
	        LinkedList<Base.Tag> tagList = tags.get(split[0]);
	        if (tagList == null)
	            tagList = new LinkedList<Base.Tag>();
	        Base.Tag tag = new Base.Tag(Integer.parseInt(split[1]), Integer.parseInt(split[2]));
            tagList.add(tag);
            tags.put(split[0], tagList);
	        line = tagFile.readLine();
	    }
	    return tags;
	}
	
	protected static int convertNonWSIndex2FullIndex(String str, int index)
	{
		int nonWSIndex = -1;
		for (int i = 0; i < str.length(); i++)
		{
			if (!Character.isWhitespace(str.charAt(i)))
			{
				nonWSIndex++;
				if (nonWSIndex == index)
					return i;
			}
		}
		return -1;
	}

	protected static int convertFullIndex2NonWSIndex(String str, int index)
	{
		int nonWSIndex = -1;
		for (int i = 0; i < str.length(); i++)
		{
			if (!Character.isWhitespace(str.charAt(i)))
			{
				nonWSIndex++;
				if (i == index)
					return nonWSIndex;
			}
		}
		return -1;
	}

	private static int getTokenIndex(List<Token> tokens, int index)
	{
		int chars = 0;
		for (int i = 0; i < tokens.size(); i++)
		{
			int length = tokens.get(i).getText().length();
			if (index >= chars && index <= chars + length - 1)
				return i;
			chars += length;
		}
		return -1;
	}
	
	private static boolean checkTokenBoundary(List<Token> tokens, int index, boolean start)
	{
		int chars = 0;
		for (int i = 0; i < tokens.size(); i++)
		{
			int length = tokens.get(i).getText().length();
			if (start && index == chars)
				return true;
			if (!start && index == chars + length - 1)
				return true;
			chars += length;
		}
		return false;
	}
	
	protected static Sentence getSentence(String id, String sentenceText, Tokenizer tokenizer, HashMap<String, LinkedList<Base.Tag>> tags)
	{
	    Sentence sentence = new Sentence(id, sentenceText);
	    tokenizer.tokenize(sentence);
	    List<Token> tokens = sentence.getTokens();
	    LinkedList<Base.Tag> tagList = tags.get(id);
	    if (tagList != null)
			for (Base.Tag tag : tagList)
			{
	        	int start = getTokenIndex(tokens, tag.start);
	        	assert start >= 0;
				int end = getTokenIndex(tokens, tag.end);
	        	assert end >= start;
				sentence.addOrMergeMention(new Mention(sentence, MentionType.getType("GENE"), start, end + 1));
			}
	    return sentence;
	}

	protected static Set<Mention> getMentions(Sentence sentence, HashMap<String, LinkedList<Base.Tag>> tags)
	{
		Set<Mention> mentions = new HashSet<Mention>();
	    List<Token> tokens = sentence.getTokens();
	    LinkedList<Base.Tag> tagList = tags.get(sentence.getTag());
	    if (tagList != null)
			for (Base.Tag tag : tagList)
			{
	        	int start = getTokenIndex(tokens, tag.start);
	        	assert start >= 0;
				int end = getTokenIndex(tokens, tag.end);
	        	assert end >= start;
	        	mentions.add(new Mention(sentence, MentionType.getType("GENE"), start, end + 1));
			}
	    return mentions;
	}

	protected static int checkTokenBoundaries(Sentence sentence, Tokenizer tokenizer, HashMap<String, LinkedList<Base.Tag>> tags)
	{
	    List<Token> tokens = sentence.getTokens();
	    LinkedList<Base.Tag> tagList = tags.get(sentence.getTag());
	    int count = 0;
	    if (tagList != null)
			for (Base.Tag tag : tagList)
			{
				if (!checkTokenBoundary(tokens, tag.start, true) || !checkTokenBoundary(tokens, tag.end, false))
					count++;
			}
	    return count;
	}

	/**
     * @param id
     * @param sentence
     * @param tagger
     * @param mentionOutputFile
     */
	protected static void outputMentions(Sentence sentence,
			PrintWriter mentionOutputFile) {
		List<Token> tokens = sentence.getTokens();
		int charCount = 0;
		for (int i = 0; i < tokens.size(); i++) {
			List<Mention> mentions = sentence.getMentions(tokens.get(i));
			assert mentions.size() == 0 || mentions.size() == 1;
			Mention mention = null;
			if (mentions.size() > 0)
				mention = mentions.get(0);
			if (mention != null && i == mention.getStart()) {
				mentionOutputFile.print(sentence.getTag());
				mentionOutputFile.print("|");
				mentionOutputFile.print(charCount);
				mentionOutputFile.print(" ");
			}
			charCount += tokens.get(i).length();
			if (mention != null && i == mention.getEnd() - 1) {
				mentionOutputFile.print(charCount - 1);
				mentionOutputFile.print("|");
				mentionOutputFile.println(mention.getText());
			}
		}
	}

	public static class Tag
	{
	    int start;
	    int end;
	
	
	    /**
         * @param start
         * @param end
         */
	    public Tag(int start, int end)
	    {
	        this.start = start;
	        this.end = end;
	    }
	
	
	    public boolean overlaps(Tag tag)
	    {
	        return start <= tag.end && tag.start <= end;
	    }
	
	
	    public boolean contains(Tag tag)
	    {
	        return start <= tag.start && end >= tag.end;
	    }
	}

	protected static double[] getResults(Set<Mention> mentionsTest, Set<Mention> mentionsFound) {
		int tp = 0;
		for (Mention mention : mentionsTest) {
			if (mentionsFound.contains(mention))
				tp++;
		}
		double[] results = new double[3];
		results[1] = (double) tp / mentionsFound.size(); // precision
		results[2] = (double) tp / mentionsTest.size(); // recall
		results[0] = 2.0 * results[1] * results[2] / (results[1] + results[2]); // f-measure
		return results;
	}

	protected static double[] getResults(Set<Mention> mentionsRequired, Set<Mention> mentionsAllowed, Set<Mention> mentionsFound) {
		int tp = 0;
		for (Mention mention : mentionsFound) {
			if (mentionsRequired.contains(mention) || mentionsAllowed.contains(mention))
				tp++;
		}
		double[] results = new double[3];
		results[1] = (double) tp / mentionsFound.size(); // precision
		results[2] = (double) tp / mentionsRequired.size(); // recall
		results[0] = 2.0 * results[1] * results[2] / (results[1] + results[2]); // f-measure
		return results;
	}
}