/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.LinkedList;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tokenization.BaseTokenizer;
import com.semanticscience.banner.tokenization.Tokenizer;

public class CheckTokenization extends Base
{
    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        long start = System.currentTimeMillis();
        BufferedReader inputFile = new BufferedReader(new FileReader(args[0]));
        BufferedReader tagFile1 = new BufferedReader(new FileReader(args[1]));
        BufferedReader tagFile2 = new BufferedReader(new FileReader(args[2]));
        PrintWriter outputFile = new PrintWriter(new BufferedWriter(new FileWriter(args[3])));

        HashMap<String, LinkedList<Base.Tag>> tags = getTags(tagFile1);
        tagFile1.close();
        tags.putAll(getTags(tagFile2));
        tagFile2.close();

        // TODO Separate between errors in main file and errors in alternate file

        Tokenizer tokenizer = new BaseTokenizer();

        String line = inputFile.readLine();
        int count;
        int total = 0;
        while (line != null)
        {
            int space = line.indexOf(' ');
            String id = line.substring(0, space).trim();
            String sentenceText = line.substring(space).trim();
            Sentence sentence = new Sentence(id, sentenceText);
            tokenizer.tokenize(sentence);
            outputFile.println(sentence.getTokenizedText());
            count = checkTokenBoundaries(sentence, tokenizer, tags);
            if (count > 0)
                System.out.println(id);
            total += count;
            line = inputFile.readLine();
        }
        inputFile.close();
        outputFile.close();

        System.out.println("Had " + total + " tokenization errors");
        System.out.println("Took " + (System.currentTimeMillis() - start) + " ms");
    }
}