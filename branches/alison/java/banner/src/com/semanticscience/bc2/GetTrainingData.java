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
import com.semanticscience.banner.tokenization.Tokenizer;

/**
 * Converts from a raw input file in BioCreative II format into a file in the training format where every token is followed by a vertical pipe ("|")
 * and its type: I, O, or B.
 */
public class GetTrainingData extends Base
{
    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        long start = System.currentTimeMillis();
        BannerProperties properties = BannerProperties.load(new File(args[0]));
        BufferedReader inputFile = new BufferedReader(new FileReader(args[1]));
        BufferedReader tagFile = new BufferedReader(new FileReader(args[2]));
        PrintWriter outputFile = new PrintWriter(new BufferedWriter(new FileWriter(args[3])));

        HashMap<String, LinkedList<Base.Tag>> tags = getTags(tagFile);
        tagFile.close();

        Tokenizer tokenizer = properties.getTokenizer();

        String line = inputFile.readLine();
        while (line != null)
        {
            int space = line.indexOf(' ');
            String id = line.substring(0, space).trim();
            String sentence = line.substring(space).trim();
            outputFile.println(getSentence(id, sentence, tokenizer, tags).getTrainingText(properties.getTagFormat()));
            line = inputFile.readLine();
        }
        inputFile.close();
        outputFile.close();
        System.out.println("Took " + (System.currentTimeMillis() - start) + " ms");
    }
}