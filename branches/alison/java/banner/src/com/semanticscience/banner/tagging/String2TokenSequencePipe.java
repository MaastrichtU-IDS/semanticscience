/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import dragon.nlp.Sentence;
import dragon.nlp.Word;
import dragon.nlp.tool.Tagger;
import dragon.nlp.tool.Lemmatiser;

import edu.umass.cs.mallet.base.pipe.*;
import edu.umass.cs.mallet.base.types.*;

/**
 * This class is used by the CRFTagger as the base for the feature set. This class is a convenient place to implement adding new features to BANNER,
 * but should not otherwise require modification by the user.
 * 
 * @author Bob
 */
public class String2TokenSequencePipe extends Pipe
{
    private static final long serialVersionUID = 1L;

    private transient Lemmatiser lemmatiser = null;
    private transient Tagger posTagger = null;

    private boolean useNumericNormalization;


    public String2TokenSequencePipe(Lemmatiser lemmatiser, Tagger posTagger, boolean useNumericNormalization)
    {
    	  super(null, LabelAlphabet.class);
        this.lemmatiser = lemmatiser;
        this.posTagger = posTagger;
        this.useNumericNormalization = useNumericNormalization;
    }


    public void setLemmatiser(Lemmatiser lemmatiser)
    {
        this.lemmatiser = lemmatiser;
    }


    public void setPosTagger(Tagger posTagger)
    {
        this.posTagger = posTagger;
    }


    @Override
    public Instance pipe(Instance carrier)
    {
        String sentenceLines = (String)carrier.getData();
        String[] tokens = sentenceLines.trim().split("\\s+");

        TokenSequence data = new TokenSequence(tokens.length);
        
        LabelSequence target = new LabelSequence((LabelAlphabet)getTargetAlphabet(), tokens.length);
        StringBuffer source = new StringBuffer();

        for (int i = 0; i < tokens.length; i++)
        {
            String[] split = tokens[i].split("\\|");
            String text = split[0];
            String tag = split[1];
            Token token = new Token(text);

            // Add features to token
            token.setFeatureValue("W=" + text.toLowerCase(), 1);
            int[] pos = null;
            if (posTagger != null)
            {
                pos = getPOS(tokens);
                token.setFeatureValue("POS=" + pos[i], 1);
            }
            if (lemmatiser != null)
            {
                String lemma;
                if (pos == null)
                {
                    lemma = lemmatiser.lemmatize(text);
                }
                else
                    lemma = lemmatiser.lemmatize(text, pos[i]);
                token.setFeatureValue("LW=" + lemma, 1);
            }
            if (useNumericNormalization)
            {
                token.setFeatureValue("NC=" + getNumberClass(text), 1);
                token.setFeatureValue("BNC=" + getBriefNumberClass(text), 1);
            }
            token.setFeatureValue("WC=" + getWordClass(text), 1);
            token.setFeatureValue("BWC=" + getBriefWordClass(text), 1);

            // Add token to data
            data.add(token);
            target.add(tag);

            source.append(token.getText());
            source.append(" ");
        }

        carrier.setData(data);
        carrier.setTarget(target);
        carrier.setSource(source);
        return carrier;
    }


    private String getNumberClass(String text)
    {
        text = text.replaceAll("[0-9]", "0");
        return text;
    }


    private String getWordClass(String text)
    {
        text = text.replaceAll("[A-Z]", "A");
        text = text.replaceAll("[a-z]", "a");
        text = text.replaceAll("[0-9]", "0");
        text = text.replaceAll("[^A-Za-z0-9]", "x");
        return text;
    }


    private String getBriefNumberClass(String text)
    {
        text = text.replaceAll("[0-9]+", "0");
        return text;
    }


    private static String getBriefWordClass(String text)
    {
        text = text.replaceAll("[A-Z]+", "A");
        text = text.replaceAll("[a-z]+", "a");
        text = text.replaceAll("[0-9]+", "0");
        text = text.replaceAll("[^A-Za-z0-9]+", "x");
        return text;
    }


    private int[] getPOS(String[] tokens)
    {
        String[] rawTokens = new String[tokens.length];
        Word[] words = new Word[tokens.length];
        Sentence sentence = new Sentence();
        for (int i = 0; i < tokens.length; i++)
        {
        	rawTokens[i] = tokens[i].split("\\|")[0];
            words[i] = new Word(rawTokens[i]);
            sentence.addWord(words[i]);
        }
        posTagger.tag(sentence);
        int[] pos = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++)
        {
            pos[i] = words[i].getPOSIndex();
        }
        return pos;
    }
}