/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

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
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import edu.umass.cs.mallet.base.fst.CRF;
import edu.umass.cs.mallet.base.util.MalletLogger;

import com.semanticscience.banner.BannerProperties;
import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.processing.PostProcessor;
import com.semanticscience.banner.tagging.CRFTagger;
import com.semanticscience.banner.tokenization.Tokenizer;

/**
 * Performs a 2-fold cross validation: partitions the data into two sets of roughly equal size, trains a model on each and then tests each model on
 * the unseen partition. To perform 5 x 2 cross validation, simply execute this 5 times.
 */
public class Evaluate2Fold extends Base
{

    static PrintStream sysOut;

    static ArrayList<String> ids = new ArrayList<String>();

    static HashMap<String, Sentence> id2Sentence = new HashMap<String, Sentence>();

    private static BannerProperties properties;


    /**
     * @param args
     * @throws IOException
     */
    public static void main(String[] args) throws IOException
    {
        long start = System.currentTimeMillis();

        properties = BannerProperties.load(new File(args[0]));
        properties.log();
        BufferedReader sentenceFile = new BufferedReader(new FileReader(args[1]));
        String tagFilename = args[2];
        String directory = args[3];
        String cross = args[4];
        Double percentage = null;
        if (args.length == 6)
            percentage = Double.valueOf(args[5]);

        Logger.getLogger(CRF.class.getName()).setLevel(Level.OFF);
        MalletLogger.getLogger(CRF.class.getName()).setLevel(Level.OFF);

        // Redirect the standard error stream
        sysOut = System.out;
        PrintStream fileOut = new PrintStream(new BufferedOutputStream(new FileOutputStream(directory + "/stdout" + cross + ".txt")));
        System.setOut(fileOut);
        PrintStream fileErr = new PrintStream(new BufferedOutputStream(new FileOutputStream(directory + "/stderr" + cross + ".txt")));
        System.setErr(fileErr);

        try
        {
            BufferedReader tagFile = new BufferedReader(new FileReader(tagFilename));
            HashMap<String, LinkedList<Base.Tag>> tags = getTags(tagFile);
            tagFile.close();

            String line = sentenceFile.readLine();
            while (line != null)
            {
                int space = line.indexOf(' ');
                String id = line.substring(0, space).trim();
                String sentence = line.substring(space).trim();
                if (percentage == null || Math.random() < percentage.doubleValue())
                {
                    ids.add(id);
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
            PrintWriter idFile_A = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/ids_A" + cross + ".txt")));
            PrintWriter idFile_B = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/ids_B" + cross + ".txt")));
            PrintWriter rawFile_A = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/raw_A" + cross + ".txt")));
            PrintWriter rawFile_B = new PrintWriter(new BufferedWriter(new FileWriter(directory + "/raw_B" + cross + ".txt")));
            PrintWriter trainingFile_A = new PrintWriter(new BufferedWriter(new FileWriter(trainingFilename_A)));
            PrintWriter trainingFile_B = new PrintWriter(new BufferedWriter(new FileWriter(trainingFilename_B)));
            ArrayList<String> ids_A = new ArrayList<String>();
            ArrayList<String> ids_B = new ArrayList<String>();
            for (int index = 0; index < ids.size(); index++)
            {
                String id = ids.get(index);
                Sentence sentence = id2Sentence.get(id);
                if (Math.random() < 0.5)
                {
                    ids_A.add(id);
                    idFile_A.println(id);
                    rawFile_A.println(sentence.getText());
                    trainingFile_A.println(sentence.getTrainingText(properties.getTagFormat()));
                }
                else
                {
                    ids_B.add(id);
                    idFile_B.println(id);
                    rawFile_B.println(sentence.getText());
                    trainingFile_B.println(sentence.getTrainingText(properties.getTagFormat()));
                }
            }
            idFile_A.close();
            idFile_B.close();
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
            CRFTagger tagger = train(ids_A, modelFilename_A);
            sysOut.println("Completed training for fold A of cross #" + cross + ": " + (System.currentTimeMillis() - start));
            System.gc();

            // Test on fold B & output results
            test(ids_B, tagger, outputFilename_B, mentionFilename_B);
            sysOut.println("Completed testing for fold A of cross #" + cross + ": " + (System.currentTimeMillis() - start));
            tagger = null;
            System.gc();

            // Train on fold B & output model
            tagger = train(ids_B, modelFilename_B);
            sysOut.println("Completed training for fold B of cross #" + cross + ": " + (System.currentTimeMillis() - start));
            System.gc();

            // Test on fold A & output results
            test(ids_A, tagger, outputFilename_A, mentionFilename_A);
            sysOut.println("Completed testing for fold B of cross #" + cross + ": " + (System.currentTimeMillis() - start));
            System.gc();
        }
        finally
        {
            fileOut.close();
            fileErr.close();
        }
    }


    private static CRFTagger train(ArrayList<String> ids, String modelFile) throws IOException
    {
        sysOut.println("\tGetting sentence list");
        List<Sentence> sentences = new ArrayList<Sentence>(ids.size());
        for (String id : ids)
            sentences.add(id2Sentence.get(id));
        sysOut.println("\tTraining data loaded, starting training");
        CRFTagger tagger = CRFTagger.train(sentences, properties.getOrder(), properties.isUseFeatureInduction(), properties.getTagFormat(),
                                           properties.getTextDirection(), properties.getLemmatiser(), properties.getPosTagger(),
                                           properties.isUseNumericNormalization());
        sysOut.println("\tTraining complete, saving model");
        tagger.write(new File(modelFile));
        return tagger;
    }


    private static void test(ArrayList<String> ids, CRFTagger tagger, String outputFilename, String mentionFilename) throws IOException
    {
        PrintWriter outputFile = new PrintWriter(new BufferedWriter(new FileWriter(outputFilename)));
        PrintWriter mentionFile = new PrintWriter(new BufferedWriter(new FileWriter(mentionFilename)));

        Tokenizer tokenizer = properties.getTokenizer();
        PostProcessor postProcessor = properties.getPostProcessor();
        sysOut.println("\tTagging sentences");
        for (String id : ids)
        {
            String sentenceText = id2Sentence.get(id).getText();
            Sentence sentence = new Sentence(id, sentenceText);
            tokenizer.tokenize(sentence);
            tagger.tag(sentence);
            if (postProcessor != null)
                postProcessor.postProcess(sentence);
            outputFile.println(sentence.getTrainingText(properties.getTagFormat()));
            Base.outputMentions(sentence, mentionFile);
        }

        outputFile.close();
        mentionFile.close();
    }
}