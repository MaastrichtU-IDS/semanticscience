/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

public class AnalyzeMentionBoundaries extends Base {

	private static boolean isPunctuation(char ch) {
		return ("`~!@#$%^&*()-=_+[]\\{}|;':\",./<>?".indexOf(ch) != -1);
	}

	private static char getBoundaryType(char boundary) {
		if (Character.isWhitespace(boundary))
			return '_';
		if (Character.isDigit(boundary))
			return '0';
		if (isPunctuation(boundary))
			return boundary;
		if (Character.isLetter(boundary))
			return 'A';
		return '?';
	}

	private static String getBoundaryType(String boundary) {
		StringBuffer type = new StringBuffer();
		type.append(getBoundaryType(boundary.charAt(0)));
		type.append(getBoundaryType(boundary.charAt(1)));
		return type.toString();
	}

	private static void getAllBoundaries(String sentenceText,
			HashMap<String, Integer> all) {
		for (int i = 0; i < sentenceText.length() - 1; i++) {
			String boundary = sentenceText.substring(i, i + 2);
			boundary = getBoundaryType(boundary);
			Integer count = all.get(boundary);
			if (count == null)
				count = new Integer(0);
			all.put(boundary, new Integer(count.intValue() + 1));
		}
	}

	private static void getTokenBoundaries(String sentenceText,
			List<Base.Tag> tagList, HashMap<String, Integer> starts,
			HashMap<String, Integer> ends) {
		for (Base.Tag tag : tagList) {
			// System.out.println(sentenceText);

			int start = convertNonWSIndex2FullIndex(sentenceText, tag.start);
			assert start != -1;
			if (start > 0)
			{
				String startBoundary = sentenceText.substring(start - 1, start + 1);
				startBoundary = getBoundaryType(startBoundary);
				Integer startCount = starts.get(startBoundary);
				if (startCount == null)
					startCount = new Integer(0);
				starts.put(startBoundary, new Integer(startCount.intValue() + 1));
				// System.out.println(tag.start + ": |" + startBoundary + "|");
			}

			int end = convertNonWSIndex2FullIndex(sentenceText, tag.end);
			assert end != -1;
			if (end + 2 < sentenceText.length())
			{
				String endBoundary = sentenceText.substring(end, end + 2);
				endBoundary = getBoundaryType(endBoundary);
				Integer endCount = ends.get(endBoundary);
				if (endCount == null)
					endCount = new Integer(0);
				ends.put(endBoundary, new Integer(endCount.intValue() + 1));
				// System.out.println(tag.end + ": |" + endBoundary + "|");
			}

			// System.out.println();
		}
	}

	/**
     * @param args
     */
	public static void main(String[] args) throws IOException {
		BufferedReader inputFile = new BufferedReader(new FileReader(args[0]));

		BufferedReader tagFile = new BufferedReader(new FileReader(args[1]));
		HashMap<String, LinkedList<Base.Tag>> tags = getTags(tagFile);
		tagFile.close();

		HashMap<String, Integer> all = new HashMap<String, Integer>();
		HashMap<String, Integer> starts = new HashMap<String, Integer>();
		HashMap<String, Integer> ends = new HashMap<String, Integer>();

		String line = inputFile.readLine();
		while (line != null) {
			int space = line.indexOf(' ');
			String id = line.substring(0, space).trim();
			String sentence = line.substring(space).trim();
			getAllBoundaries(sentence, all);
			List<Tag> tagList = tags.get(id);
			if (tagList != null)
				getTokenBoundaries(sentence, tagList, starts, ends);
			line = inputFile.readLine();
		}
		inputFile.close();

		for (String boundary : all.keySet())
		{
			Integer allCount = all.get(boundary);
			Integer startCount = starts.get(boundary);
			Integer endCount = ends.get(boundary);
			System.out.print("'" + boundary);
			System.out.print("\t");
			System.out.print(allCount == null ? 0 : allCount.intValue());
			System.out.print("\t");
			System.out.print(startCount == null ? 0 : startCount.intValue());
			System.out.print("\t");
			System.out.print(endCount == null ? 0 : endCount.intValue());
			System.out.println();
		}
	}
}