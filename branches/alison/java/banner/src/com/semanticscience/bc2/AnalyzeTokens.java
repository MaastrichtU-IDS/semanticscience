/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.LinkedList;

import com.semanticscience.banner.BannerProperties;
import com.semanticscience.banner.tokenization.SimpleTokenizer;

/**
 * Class will take a file in raw BioCreative II format, tokenize it, and output two CSV files showing the number of times each token is listed as B, I
 * or O in the data. This may assist the developer in visualizing which features will help discriminate between tokens indicative of NEs and ones that
 * are not.
 */
public class AnalyzeTokens extends Base
{

    private static class TagCounter
    {
        int bCount = 0;
        int iCount = 0;
        int oCount = 0;


        public TagCounter()
        {
            // Empty
        }


        public void add(String tag)
        {
            tag = tag.toUpperCase();
            if (tag.equals("B"))
                bCount++;
            else if (tag.equals("I"))
                iCount++;
            else
            {
                assert tag.equals("O");
                oCount++;
            }
        }


        @Override
        public String toString()
        {
            return bCount + "," + iCount + "," + oCount;
        }
    }


    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        // Get the args
    	BannerProperties properties = BannerProperties.load(new File(args[0]));
        BufferedReader rawTrainingFile = new BufferedReader(new FileReader(args[1]));
        String tagFilename = args[2];
        PrintWriter posOutputFile = new PrintWriter(new BufferedWriter(new FileWriter(args[3])));
        PrintWriter negOutputFile = new PrintWriter(new BufferedWriter(new FileWriter(args[4])));

        BufferedReader tagFile = new BufferedReader(new FileReader(tagFilename));
        HashMap<String, LinkedList<Base.Tag>> tags = getTags(tagFile);
        tagFile.close();

        HashMap<String, TagCounter> counts = new HashMap<String, TagCounter>();

        SimpleTokenizer tokenizer = new SimpleTokenizer();
        
        String line = rawTrainingFile.readLine();
        int count = 0;
        while (line != null)
        {
            int space = line.indexOf(' ');
            String id = line.substring(0, space).trim();
            String sentence = line.substring(space).trim();
            String trainingSentence = getSentence(id, sentence, tokenizer, tags).getTrainingText(properties.getTagFormat());
            String[] split = trainingSentence.split(" ");
            for (String taggedToken : split)
            {
                String[] parts = taggedToken.split("\\|");
                String token = parts[0];
                String tag = parts[1];
                TagCounter counter = counts.get(token);
                if (counter == null)
                {
                    counter = new TagCounter();
                    counter.add(tag);
                    counts.put(token, counter);
                }
                else
                {
                    counter.add(tag);
                }
            }
            line = rawTrainingFile.readLine();
            count++;
        }
        rawTrainingFile.close();

        for (String token : counts.keySet())
        {
            TagCounter tagCounter = counts.get(token);
            // CSV files require quotes around commas
            if (token.equals(","))
                token = "\",\"";
            if (tagCounter.bCount == 0 && tagCounter.iCount == 0)
                negOutputFile.println(token + "," + tagCounter.toString());
            else
                posOutputFile.println(token + "," + tagCounter.toString());
        }
        posOutputFile.close();
        negOutputFile.close();
    }

}