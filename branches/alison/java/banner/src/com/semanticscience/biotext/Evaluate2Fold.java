/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.biotext;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
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
import com.semanticscience.bc2.Base;

/**
 * Performs a 2-fold cross validation: partitions the data into two sets of roughly equal size, trains a model on each and then tests each model on
 * the unseen partition. To perform 5 x 2 cross validation, simply execute this 5 times.
 */
public class Evaluate2Fold extends Base
{

    public static PrintStream sysOut;

    static HashMap<String, Sentence> id2Sentence = new HashMap<String, Sentence>();

    private static BannerProperties properties;


    /**
     * @param args
     * @throws IOException
     */
    public static void main(String[] args) throws Exception
    {
        long start = System.currentTimeMillis();

        properties = BannerProperties.load(new File(args[0]));
        properties.log();
        BufferedReader sentenceFile = new BufferedReader(new FileReader(args[1]));
        BufferedReader diseaseMentionFile = new BufferedReader(new FileReader(args[2]));
        BufferedReader treatmentMentionFile = new BufferedReader(new FileReader(args[3]));
        String directory = args[4];
        String cross = args[5];
        Double percentage = null;
        if (args.length == 7)
            percentage = Double.valueOf(args[6]);

        Logger.getLogger(CRF.class.getName()).setLevel(Level.OFF);
        MalletLogger.getLogger(CRF.class.getName()).setLevel(Level.OFF);

        // Redirect the standard error stream
        sysOut = System.out;
        PrintStream fileOut = new PrintStream(new BufferedOutputStream(new FileOutputStream(directory + "/stdout" + cross + ".txt")));
        System.setOut(fileOut);
        PrintStream fileErr = new PrintStream(new BufferedOutputStream(new FileOutputStream(directory + "/stderr" + cross + ".txt")));
        System.setErr(fileErr);

        // try {

        // Get the mentions
        HashMap<String, LinkedList<Base.Tag>> tags = new HashMap<String, LinkedList<Base.Tag>>();
        tags.putAll(getTags(diseaseMentionFile));
        // tags.putAll(getTags(treatmentMentionFile));
        diseaseMentionFile.close();
        treatmentMentionFile.close();

        // Get the sentences
        String line = sentenceFile.readLine();
        while (line != null)
        {
            int space = line.indexOf(' ');
            String id = line.substring(0, space).trim();
            String sentence = line.substring(space).trim();
            if (percentage == null || Math.random() < percentage.doubleValue())
            {
                id2Sentence.put(id, getSentence(id, sentence, properties.getTokenizer(), tags));
            }
            line = sentenceFile.readLine();
        }
        sentenceFile.close();

        sysOut.println("Completed input: " + (System.currentTimeMillis() - start));

        start = System.currentTimeMillis();
        String trainingFilename_A = directory + "/training_A" + cross + ".txt";
        String trainingFilename_B = directory + "/training_B" + cross + ".txt";
        String modelFilename_A = directory + "/model_A" + cross + ".txt";
        String modelFilename_B = directory + "/model_B" + cross + ".txt";

        // Create folds & output to file
        PrintWriter rawFile_A = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/raw_A" + cross + ".txt")));
        PrintWriter rawFile_B = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/raw_B" + cross + ".txt")));
        PrintWriter trainingFile_A = new PrintWriter(new BufferedWriter(new FileWriter(trainingFilename_A)));
        PrintWriter trainingFile_B = new PrintWriter(new BufferedWriter(new FileWriter(trainingFilename_B)));
        ArrayList<Sentence> sentences_A = new ArrayList<Sentence>();
        ArrayList<Sentence> sentences_B = new ArrayList<Sentence>();
        Set<Mention> mentionsTest_A = new HashSet<Mention>();
        Set<Mention> mentionsTest_B = new HashSet<Mention>();
        for (String id : id2Sentence.keySet())
        {
            Sentence sentence = id2Sentence.get(id);
            if (Math.random() < 0.5)
            {
                sentences_A.add(sentence);
                mentionsTest_A.addAll(sentence.getMentions());
                rawFile_A.println(sentence.getText());
                trainingFile_A.println(sentence.getTrainingText(properties.getTagFormat()));
            }
            else
            {
                sentences_B.add(sentence);
                mentionsTest_B.addAll(sentence.getMentions());
                rawFile_B.println(sentence.getText());
                trainingFile_B.println(sentence.getTrainingText(properties.getTagFormat()));
            }
        }
        rawFile_A.close();
        rawFile_B.close();
        trainingFile_A.close();
        trainingFile_B.close();

        sysOut.println("Created folds for cross #" + cross + ": " + (System.currentTimeMillis() - start));

        String outputFilename_A = directory + "/output_A" + cross + ".txt";
        String outputFilename_B = directory + "/output_B" + cross + ".txt";
        String mentionFilename_A = directory + "/mention_A" + cross + ".txt";
        String mentionFilename_B = directory + "/mention_B" + cross + ".txt";

        // Train on fold A & output model
        CRFTagger tagger = train(sentences_A, modelFilename_A);
        sysOut.println("Completed training for fold A of cross #" + cross + ": " + (System.currentTimeMillis() - start));
        System.gc();

        // Test on fold B & output results
        Set<Mention> mentionsFound_B = test(sentences_B, tagger, outputFilename_B, mentionFilename_B);
        sysOut.println("Completed testing for fold A of cross #" + cross + ": " + (System.currentTimeMillis() - start));
        sysOut.println("cross #" + cross + ", B");
        double[] results;
        results = Base.getResults(mentionsTest_B, mentionsFound_B);
        Evaluate2Fold.sysOut.println("precision: " + results[1]);
        Evaluate2Fold.sysOut.println("   recall: " + results[2]);
        Evaluate2Fold.sysOut.println("f-measure: " + results[0]);
        tagger = null;
        System.gc();

        // Train on fold B & output model
        tagger = train(sentences_B, modelFilename_B);
        sysOut.println("Completed training for fold B of cross #" + cross + ": " + (System.currentTimeMillis() - start));
        System.gc();

        // Test on fold A & output results
        Set<Mention> mentionsFound_A = test(sentences_A, tagger, outputFilename_A, mentionFilename_A);
        sysOut.println("Completed testing for fold B of cross #" + cross + ": " + (System.currentTimeMillis() - start));
        sysOut.println("cross #" + cross + ", A");
        results = Base.getResults(mentionsTest_A, mentionsFound_A);
        Evaluate2Fold.sysOut.println("precision: " + results[1]);
        Evaluate2Fold.sysOut.println("   recall: " + results[2]);
        Evaluate2Fold.sysOut.println("f-measure: " + results[0]);
        System.gc();

        // } finally {
        // fileOut.close();
        // fileErr.close();
        // }
    }


    private static CRFTagger train(ArrayList<Sentence> sentences, String modelFile) throws IOException
    {
        sysOut.println("\tStarting training");
        CRFTagger tagger = CRFTagger.train(sentences, properties.getOrder(), properties.isUseFeatureInduction(), properties.getTagFormat(),
                                           properties.getTextDirection(), properties.getLemmatiser(), properties.getPosTagger(),
                                           properties.isUseNumericNormalization());
        sysOut.println("\tTraining complete, saving model");
        tagger.write(new File(modelFile));
        return tagger;
    }


    private static Set<Mention> test(ArrayList<Sentence> sentences, CRFTagger tagger, String outputFilename, String mentionFilename)
                                                                                                                                    throws IOException
    {
        PrintWriter outputFile = new PrintWriter(new BufferedWriter(new FileWriter(outputFilename)));
        Tokenizer tokenizer = properties.getTokenizer();
        PostProcessor postProcessor = properties.getPostProcessor();
        sysOut.println("\tTagging sentences");
        Set<Mention> mentions = new HashSet<Mention>();
        for (Sentence sentence : sentences)
        {
            String sentenceText = sentence.getText();
            Sentence sentence2 = new Sentence(sentenceText);
            tokenizer.tokenize(sentence2);
            tagger.tag(sentence2);
            if (postProcessor != null)
                postProcessor.postProcess(sentence2);
            outputFile.println(sentence2.getTrainingText(properties.getTagFormat()));
            mentions.addAll(sentence2.getMentions());
        }
        outputFile.close();
        return mentions;
    }
}