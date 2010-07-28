/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

import dragon.nlp.tool.Lemmatiser;

import edu.umass.cs.mallet.base.fst.CRF4;
import edu.umass.cs.mallet.base.fst.MultiSegmentationEvaluator;
import edu.umass.cs.mallet.base.pipe.Pipe;
import edu.umass.cs.mallet.base.pipe.SerialPipes;
import edu.umass.cs.mallet.base.pipe.TokenSequence2FeatureVectorSequence;
import edu.umass.cs.mallet.base.pipe.tsf.OffsetConjunctions;
import edu.umass.cs.mallet.base.pipe.tsf.RegexMatches;
import edu.umass.cs.mallet.base.pipe.tsf.TokenTextCharNGrams;
import edu.umass.cs.mallet.base.pipe.tsf.TokenTextCharPrefix;
import edu.umass.cs.mallet.base.pipe.tsf.TokenTextCharSuffix;
import edu.umass.cs.mallet.base.types.Instance;
import edu.umass.cs.mallet.base.types.InstanceList;
import edu.umass.cs.mallet.base.types.Sequence;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.BannerProperties.TextDirection;
import com.semanticscience.banner.tagging.TaggedToken.TagFormat;
import com.semanticscience.banner.tagging.TaggedToken.TagPosition;

public class CRFTagger implements Tagger
{

    // TODO Add support for TextDirection.Union and TextDirection.Intersection

    private static String GREEK = "(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega)";
    private CRF4 forwardCRF;
    private CRF4 reverseCRF;
    private String2TokenSequencePipe basePipe;
    private int order;
    private boolean useFeatureInduction;
    private TagFormat format;
    private TextDirection textDirection;


    private CRFTagger(CRF4 forwardCRF, CRF4 reverseCRF, String2TokenSequencePipe basePipe, int order, boolean useFeatureInduction, TagFormat format,
            TextDirection textDirection)
    {
        // TODO Verify crf==null matches textDirection
    	this.forwardCRF = forwardCRF;    	
    	this.reverseCRF = reverseCRF;
        this.basePipe = basePipe;
        this.order = order;
        this.useFeatureInduction = useFeatureInduction;
        this.format = format;
        this.textDirection = textDirection;
    }


    /**
     * Loads a {@link CRFTagger} from the specified file. As the lemmatiser and part-of-speech tagger both require data, these cannot be written to
     * disk and must be passed in new.
     * 
     * @param f
     *        The file to load the CRFTagger from, as written by the {@link}write() method.
     * @param lemmatiser
     *        The {@link Lemmatiser} to use
     * @param posTagger
     *        The part-of-speech {@link dragon.nlp.tool.Tagger} to use
     * @throws IOException
     * @return A new instance of the CRFTagger contained in the specified file
     */
    public static CRFTagger load(File f, Lemmatiser lemmatiser, dragon.nlp.tool.Tagger posTagger) throws IOException
    {
        try
        {
            ObjectInputStream ois = new ObjectInputStream(new GZIPInputStream(new FileInputStream(f)));
            // ObjectInputStream ois = new ObjectInputStream((new FileInputStream(f)));
            TextDirection textDirection = (TextDirection)ois.readObject();
            CRF4 forwardCRF = null;
            if (textDirection.doForward())
                forwardCRF = (CRF4)ois.readObject();
            CRF4 reverseCRF = null;
            if (textDirection.doReverse())
                reverseCRF = (CRF4)ois.readObject();
            String2TokenSequencePipe basePipe = (String2TokenSequencePipe)ois.readObject();
            basePipe.setLemmatiser(lemmatiser);
            basePipe.setPosTagger(posTagger);
            int order = ois.readInt();
            boolean useFeatureInduction = ois.readBoolean();
            TagFormat format = (TagFormat)ois.readObject();
            ois.close();
            return new CRFTagger(forwardCRF, reverseCRF, basePipe, order, useFeatureInduction, format, textDirection);
        }
        catch (ClassNotFoundException e)
        {
            throw new RuntimeException(e);
        }
    }


    private static void setupPipes(ArrayList<Pipe> pipes)
    {
        pipes.add(new RegexMatches("ALPHA", Pattern.compile("[A-Za-z]+")));
        pipes.add(new RegexMatches("INITCAPS", Pattern.compile("[A-Z].*")));
        pipes.add(new RegexMatches("UPPER-LOWER", Pattern.compile("[A-Z][a-z].*")));
        pipes.add(new RegexMatches("LOWER-UPPER", Pattern.compile("[a-z]+[A-Z]+.*")));
        pipes.add(new RegexMatches("ALLCAPS", Pattern.compile("[A-Z]+")));
        pipes.add(new RegexMatches("MIXEDCAPS", Pattern.compile("[A-Z][a-z]+[A-Z][A-Za-z]*")));
        pipes.add(new RegexMatches("SINGLECHAR", Pattern.compile("[A-Za-z]")));
        pipes.add(new RegexMatches("SINGLEDIGIT", Pattern.compile("[0-9]")));
        pipes.add(new RegexMatches("DOUBLEDIGIT", Pattern.compile("[0-9][0-9]")));
        pipes.add(new RegexMatches("NUMBER", Pattern.compile("[0-9,]+")));
        pipes.add(new RegexMatches("HASDIGIT", Pattern.compile(".*[0-9].*")));
        pipes.add(new RegexMatches("ALPHANUMERIC", Pattern.compile(".*[0-9].*[A-Za-z].*")));
        pipes.add(new RegexMatches("ALPHANUMERIC", Pattern.compile(".*[A-Za-z].*[0-9].*")));
        pipes.add(new RegexMatches("LETTERS_NUMBERS", Pattern.compile("[0-9]+[A-Za-z]+")));
        pipes.add(new RegexMatches("NUMBERS_LETTERS", Pattern.compile("[A-Za-z]+[0-9]+")));

        pipes.add(new RegexMatches("HAS_DASH", Pattern.compile(".*-.*")));
        pipes.add(new RegexMatches("HAS_QUOTE", Pattern.compile(".*'.*")));
        pipes.add(new RegexMatches("HAS_SLASH", Pattern.compile(".*/.*")));

        // Start second set of new features (to handle improvements in
        // BaseTokenizer)
        pipes.add(new RegexMatches("REALNUMBER", Pattern.compile("(-|\\+)?[0-9,]+(\\.[0-9]*)?%?")));
        pipes.add(new RegexMatches("REALNUMBER", Pattern.compile("(-|\\+)?[0-9,]*(\\.[0-9]+)?%?")));
        pipes.add(new RegexMatches("START_MINUS", Pattern.compile("-.*")));
        pipes.add(new RegexMatches("START_PLUS", Pattern.compile("\\+.*")));
        pipes.add(new RegexMatches("END_PERCENT", Pattern.compile(".*%")));
        // End second set

        pipes.add(new TokenTextCharPrefix("2PREFIX=", 2));
        pipes.add(new TokenTextCharPrefix("3PREFIX=", 3));
        pipes.add(new TokenTextCharPrefix("4PREFIX=", 4));
        pipes.add(new TokenTextCharSuffix("2SUFFIX=", 2));
        pipes.add(new TokenTextCharSuffix("3SUFFIX=", 3));
        pipes.add(new TokenTextCharSuffix("4SUFFIX=", 4));
        pipes.add(new TokenTextCharNGrams("CHARNGRAM=", new int[] {2, 3}, true));
        // pipes.add(new LexiconMembership()); // Use this for determining
        // whether word in a lexicon
        pipes.add(new RegexMatches("ROMAN", Pattern.compile("[IVXDLCM]+", Pattern.CASE_INSENSITIVE)));
        pipes.add(new RegexMatches("GREEK", Pattern.compile(GREEK, Pattern.CASE_INSENSITIVE)));
        pipes.add(new RegexMatches("ISPUNCT", Pattern.compile("[`~!@#$%^&*()-=_+\\[\\]\\\\{}|;\':\\\",./<>?]+")));
        pipes.add(new OffsetConjunctions(new int[][] { {-2}, {2}}));
        pipes.add(new TokenSequence2FeatureVectorSequence(true, true));
    }


    /**
     * Trains and returns a {@link CRFTagger} on the specified {@link Sentence}s. This method may take hours or even days to complete. When training,
     * you will likely need to increase the amount of memory used by the Java virtual machine (try adding "-Xms1024m" to the command line).
     * 
     * @param sentences
     *        The {@link Sentence}s to train the tagger on
     * @param order
     *        The CRF order to use
     * @param useFeatureInduction
     *        Whether or not to use feature induction
     * @param format
     *        The {@link TagFormat} to use
     * @param textDirection
     *        The {@link TextDirection} to use
     * @param lemmatiser
     *        The {@link Lemmatiser} to use
     * @param posTagger
     *        The part-of-speech {@link dragon.nlp.tool.Tagger} to use
     * @param useNumericalNormalization
     *        Whether to use numeric normalization
     * @return A trained CRFTagger; ready to tag unseen sentences or be output to disk
     */
    public static CRFTagger train(List<Sentence> sentences, int order, boolean useFeatureInduction, TagFormat format, TextDirection textDirection,
                                  Lemmatiser lemmatiser, dragon.nlp.tool.Tagger posTagger, boolean useNumericalNormalization)
    {
    	if (sentences.size() == 0)
            throw new RuntimeException("Number of sentences must be greater than zero");
        String2TokenSequencePipe localBasePipe = new String2TokenSequencePipe(lemmatiser, posTagger, useNumericalNormalization);
        ArrayList<Pipe> pipes = new ArrayList<Pipe>();
        pipes.add(localBasePipe);
        setupPipes(pipes);
        Pipe pipe = new SerialPipes(pipes);
        CRF4 forwardCRF = null;
        if (textDirection == TextDirection.Intersection)
            throw new UnsupportedOperationException("TextDirection.Intersection not yet supported");
        if (textDirection.doForward())
            forwardCRF = train(sentences, order, useFeatureInduction, format, pipe, false);
        CRF4 reverseCRF = null;
        if (textDirection.doReverse())
            reverseCRF = train(sentences, order, useFeatureInduction, format, pipe, true);
        return new CRFTagger(forwardCRF, reverseCRF, localBasePipe, order, useFeatureInduction, format, textDirection);
    }


    private static CRF4 train(List<Sentence> sentences, int order, boolean useFeatureInduction, TagFormat format, Pipe pipe, boolean reverse)
    {
        InstanceList instances = new InstanceList(pipe);
        for (Sentence sentence : sentences)
        {
            String text = sentence.getTrainingText(format, reverse);
            instances.add(new Instance(text, null, sentence.getTag(), null, pipe));
        }
        CRF4 crf = new CRF4(pipe, null);
        if (order == 1)
            crf.addStatesForLabelsConnectedAsIn(instances);
        else if (order == 2)
            crf.addStatesForBiLabelsConnectedAsIn(instances);
        else
            throw new IllegalArgumentException("Order must be equal to 1 or 2");
        if (useFeatureInduction)
            crf.trainWithFeatureInduction(instances, null, null, null, 99999, 100, 10, 1000, 0.5, false, new double[] {.2, .5, .8});
        else
            crf.train(instances, null, null, (MultiSegmentationEvaluator)null, 99999, 10, new double[] {.2, .5, .8});
        return crf;
    }


    /**
     * Serializes and writes this CRFTagger to the specified file
     * 
     * @param f
     *        The file to write this CRFTagger to
     */
    public void write(File f)
    {
        try
        {
            ObjectOutputStream oos = new ObjectOutputStream(new GZIPOutputStream(new FileOutputStream(f)));
            oos.writeObject(textDirection);
            if (textDirection.doForward())
            	  oos.writeObject(forwardCRF);
            if (textDirection.doReverse())
                oos.writeObject(reverseCRF);
            oos.writeObject(basePipe);
            oos.writeInt(order);
            oos.writeBoolean(useFeatureInduction);
            oos.writeObject(format);
            oos.close();
        }
        catch (IOException e)
        {
            System.err.println("Exception writing file " + f + ": " + e);
        }
    }


    public void tag(Sentence sentence)
    {
        int size = sentence.getTokens().size();
        if (textDirection.doForward())
        {
            TagPosition[] positions = new TagPosition[size];
            MentionType[] types = new MentionType[size];
            getPositionsAndTypes(sentence, positions, types, false);
            sentence.addMentions(positions, types);
        }
        if (textDirection.doReverse())
        {
            TagPosition[] positions = new TagPosition[size];
            MentionType[] types = new MentionType[size];
            getPositionsAndTypes(sentence, positions, types, true);
            sentence.addMentions(positions, types);
        }
    }


    private static void reverse(Object[] array)
    {
        Object[] copy = new Object[array.length];
        System.arraycopy(array, 0, copy, 0, array.length);
        int offset = array.length - 1;
        for (int i = 0; i < array.length; i++)
            array[i] = copy[offset - i];
    }


    private void getPositionsAndTypes(Sentence sentence, TagPosition[] positions, MentionType[] types, boolean reverse)
    {
    	  Instance instance = new Instance(sentence.getTrainingText(format, reverse), null, sentence.getTag(), null, forwardCRF.getInputPipe());
          Sequence tags = forwardCRF.viterbiPath((Sequence)instance.getData()).output();
          if (positions.length != tags.size())
              throw new IllegalArgumentException();
          if (types.length != tags.size())
              throw new IllegalArgumentException();
          for (int i = 0; i < tags.size(); i++)
          {
            // The tag string is e.g. "O" or "B-GENE"
            String[] split = tags.get(i).toString().split("-");
            positions[i] = TagPosition.valueOf(split[0]);
            // TODO Verify that the type stays the same
            if (split.length == 2)
                types[i] = MentionType.getType(split[1]);
        }
        if (reverse)
        {
            reverse(positions);
            reverse(types);
        }
    }


    /**
     * @return The {@link TagFormat} used by this tagger
     */
    public TagFormat getFormat()
    {
        return format;
    }


    /**
     * @return The CRF order used by this tagger. Order 1 means that the last state is used and order 2 means that the last 2 states are used.
     */
    public int getOrder()
    {
        return order;
    }


    /**
     * @return Whether this {@link CRFTagger} was trained with feature induction
     */
    public boolean isUseFeatureInduction()
    {
        return useFeatureInduction;
    }


    /**
     * @return The {@link TextDirection} used by this {@link CRFTagger}
     */
    public TextDirection getTextDirection()
    {
        return textDirection;
    }

}