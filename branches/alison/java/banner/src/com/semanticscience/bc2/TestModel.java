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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

import edu.umass.cs.mallet.base.fst.CRF;
import edu.umass.cs.mallet.base.util.MalletLogger;

import com.semanticscience.banner.BannerProperties;
import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.processing.PostProcessor;
import com.semanticscience.banner.tagging.CRFTagger;
import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tokenization.Tokenizer;

public class TestModel extends Base
{

    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        long startTime = System.currentTimeMillis();
        BannerProperties properties = BannerProperties.load(new File(args[0]));
        BufferedReader sentenceFile = new BufferedReader(new FileReader(args[1]));
        BufferedReader mentionTestFile = new BufferedReader(new FileReader(args[2]));
        BufferedReader mentionAlternateFile = new BufferedReader(new FileReader(args[3]));
        File modelFile = new File(args[4]);
        String directory = args[5];

        properties.log();

        Logger.getLogger(CRF.class.getName()).setLevel(Level.OFF);
        MalletLogger.getLogger(CRF.class.getName()).setLevel(Level.OFF);

        HashMap<String, LinkedList<Base.Tag>> tags = new HashMap<String, LinkedList<Base.Tag>>(getTags(mentionTestFile));
        HashMap<String, LinkedList<Base.Tag>> alternateTags = new HashMap<String, LinkedList<Base.Tag>>(getAlternateTags(mentionAlternateFile));

        String line = sentenceFile.readLine();
        List<Sentence> sentences = new ArrayList<Sentence>();
        Set<Mention> mentionsTest = new HashSet<Mention>();
        Set<Mention> mentionsAlternate = new HashSet<Mention>();
        while (line != null)
        {
            int space = line.indexOf(' ');
            String id = line.substring(0, space).trim();
            String sentenceText = line.substring(space).trim();
            Sentence sentence = getSentence(id, sentenceText, properties.getTokenizer(), tags);
            mentionsTest.addAll(sentence.getMentions());
            mentionsAlternate.addAll(getMentions(sentence, alternateTags));
            sentences.add(sentence);
            line = sentenceFile.readLine();
        }
        sentenceFile.close();

        String outputFilename = directory + "/output.txt";
        String mentionFilename = directory + "/mention.txt";

        PrintWriter outputFile = new PrintWriter(new BufferedWriter(new FileWriter(outputFilename)));
        PrintWriter mentionFile = new PrintWriter(new BufferedWriter(new FileWriter(mentionFilename)));

        Tokenizer tokenizer = properties.getTokenizer();

        CRFTagger tagger = CRFTagger.load(modelFile, properties.getLemmatiser(), properties.getPosTagger());
        PostProcessor postProcessor = properties.getPostProcessor();

        System.out.println("Tagging sentences");
        int count = 0;
        Set<Mention> mentionsFound = new HashSet<Mention>();
        try
        {
            for (Sentence sentence : sentences)
            {
                if (count % 1000 == 0)
                    System.out.println(count);
                String sentenceText = sentence.getText();
                Sentence sentence2 = new Sentence(sentence.getTag(), sentenceText);
                tokenizer.tokenize(sentence2);
                tagger.tag(sentence2);
                if (postProcessor != null)
                    postProcessor.postProcess(sentence2);
                outputFile.println(sentence2.getTrainingText(properties.getTagFormat()));
                mentionsFound.addAll(sentence2.getMentions());
                outputMentions(sentence2, mentionFile);
                count++;
            }
        }
        catch (RuntimeException e)
        {
        }
        finally
        {
            outputFile.close();
            mentionFile.close();
        }

        System.out.println("Elapsed time: " + (System.currentTimeMillis() - startTime));

        // double[] results = Base.getResults(mentionsTest, mentionsAlternate,
        // mentionsFound);
        // System.out.println("precision: " + results[1]);
        // System.out.println(" recall: " + results[2]);
        // System.out.println("f-measure: " + results[0]);
    }

}