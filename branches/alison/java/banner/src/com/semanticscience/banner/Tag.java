/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.BreakIterator;

import com.semanticscience.banner.processing.PostProcessor;
import com.semanticscience.banner.tagging.CRFTagger;
import com.semanticscience.banner.tokenization.Tokenizer;

public class Tag
{

    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        String propertiesFilename = args[0]; // banner.properties
        String modelFilename = args[1]; // model.bin
        String inputFilename = args[2];
        String outputFilename = args[3];

        // Get the properties and create the tagger
        BannerProperties properties = BannerProperties.load(new File(propertiesFilename));
        Tokenizer tokenizer = properties.getTokenizer();
        CRFTagger tagger = CRFTagger.load(new File(modelFilename), properties.getLemmatiser(), properties.getPosTagger());
        PostProcessor postProcessor = properties.getPostProcessor();

        // Get the input text
        BufferedReader inputReader = new BufferedReader(new FileReader(inputFilename));
        String text = "";
        String line = inputReader.readLine();
        while (line != null)
        {
            text += line.trim() + " ";
            line = inputReader.readLine();
        }
        inputReader.close();

        // Break the input into sentences, tag and write to the output file
        PrintWriter outputWriter = new PrintWriter(new BufferedWriter(new FileWriter(outputFilename)));
        BreakIterator breaker = BreakIterator.getSentenceInstance();
        breaker.setText(text);
        int start = breaker.first();
        for (int end = breaker.next(); end != BreakIterator.DONE; start = end, end = breaker.next())
        {
            String sentenceText = text.substring(start, end).trim();
            if (sentenceText.length() > 0)
            {
                Sentence sentence = new Sentence(null, sentenceText);
                tokenizer.tokenize(sentence);
                tagger.tag(sentence);
                if (postProcessor != null)
                    postProcessor.postProcess(sentence);
                outputWriter.println(sentence.getSGML());
            }
        }
        outputWriter.close();
    }
}