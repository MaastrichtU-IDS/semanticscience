/**
 * 
 */
package com.semanticscience.banner;

import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;

import com.semanticscience.banner.processing.ParenthesisPostProcessor;
import com.semanticscience.banner.processing.PostProcessor;
import com.semanticscience.banner.tagging.TaggedToken.TagFormat;
import com.semanticscience.banner.tokenization.BaseTokenizer;
import com.semanticscience.banner.tokenization.NaiveTokenizer;
import com.semanticscience.banner.tokenization.SimpleTokenizer;
import com.semanticscience.banner.tokenization.Tokenizer;

import dragon.nlp.tool.HeppleTagger;
import dragon.nlp.tool.MedPostTagger;
import dragon.nlp.tool.Tagger;
import dragon.nlp.tool.lemmatiser.EngLemmatiser;

public class BannerProperties
{
	
	public enum TextDirection
	{
		Forward, Reverse, Union, Intersection;
		
		public boolean doForward()
		{
			return this != Reverse;
		}
		
		public boolean doReverse()
		{
			return this != Forward;
		}
	}
	
	private EngLemmatiser lemmatiser;
	private Tagger posTagger;
	private Tokenizer tokenizer;
	private TagFormat tagFormat;
	private PostProcessor postProcessor;
	private boolean useNumericNormalization;
	private int order;
	private boolean useFeatureInduction;
	private TextDirection textDirection;
	
	private BannerProperties()
	{
		// Empty
	}
	
    /**
     * Loads the properties file from the specified filename, and instantiates any objects to be used, such as the lemmatiser and part-of-speech (pos)
     * tagger
     * 
     * @param fileReader
     * @return An instance of {@link BannerProperties} which can be queried for configuration parameters
     */
	public static BannerProperties load(File file)
	{
		
		Properties properties = new Properties();
		BannerProperties bannerProperties = new BannerProperties();
		try {
			properties.load(new FileInputStream(file));
			String lemmatiserDataDirectory = properties.getProperty("lemmatiserDataDirectory");
			if (lemmatiserDataDirectory != null)
				bannerProperties.lemmatiser = new EngLemmatiser(lemmatiserDataDirectory, false, true);
			String posTaggerDataDirectory = properties.getProperty("posTaggerDataDirectory");
			if (posTaggerDataDirectory != null)
			{
				String posTagger = properties.getProperty("posTagger", HeppleTagger.class.getName());
				if (posTagger.equals(HeppleTagger.class.getName()))
					bannerProperties.posTagger = new HeppleTagger(posTaggerDataDirectory);
				else if (posTagger.equals(MedPostTagger.class.getName()))
					bannerProperties.posTagger = new MedPostTagger(posTaggerDataDirectory);
				else
					throw new IllegalArgumentException("Unknown POS tagger type: " + posTagger);
			}
			String tokenizer = properties.getProperty("tokenizer", SimpleTokenizer.class.getName());
			if (tokenizer.equals(NaiveTokenizer.class.getName()))
				bannerProperties.tokenizer = new NaiveTokenizer();
			else if (tokenizer.equals(SimpleTokenizer.class.getName()))
				bannerProperties.tokenizer = new SimpleTokenizer();
			else if (tokenizer.equals(BaseTokenizer.class.getName()))
				bannerProperties.tokenizer = new BaseTokenizer();
			else
				throw new IllegalArgumentException("Unknown tokenizer type: " + tokenizer);
			bannerProperties.tagFormat = TagFormat.valueOf(properties.getProperty("tagFormat", "IOB"));
			if (Boolean.parseBoolean(properties.getProperty("useParenthesisPostProcessing", "true")))
				bannerProperties.postProcessor = new ParenthesisPostProcessor();
			bannerProperties.useNumericNormalization = Boolean.parseBoolean(properties.getProperty("useNumericNormalization", "true"));
			bannerProperties.order = Integer.parseInt(properties.getProperty("order", "2"));
			bannerProperties.useFeatureInduction = Boolean.parseBoolean(properties.getProperty("useFeatureInduction", "false"));
			bannerProperties.textDirection = TextDirection.valueOf(properties.getProperty("textDirection", "Forward"));
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		return bannerProperties;
	}
	
    /**
     * @return The {@link TextDirection} to use for training and tagging, default is Forward (only)
     */
	public TextDirection getTextDirection() {
		return textDirection;
	}

    /**
     * @return The lemmatiser ({@link EngLemmatiser}) to use for training and tagging
     */
	public EngLemmatiser getLemmatiser() {
		return lemmatiser;
	}

    /**
     * @return The CRF order to use for training and tagging. Valid values are 1 or 2, default is 2
     */
	public int getOrder() {
		return order;
	}

    /**
     * @return The part-of-speech {@link Tagger} to use for training and tagging.
     */
	public Tagger getPosTagger() {
		return posTagger;
	}

    /**
     * @return The instance of {@link ParenthesisPostProcessor} to use for training and tagging, or <code>null</code> if it should not be used
     */
	public PostProcessor getPostProcessor() {
		return postProcessor;
	}

/**
 * @return The {@link TagFormat} (IO/IOB/IOBEW) which should be used for training and tagging. Default is IOB
 */
    public TagFormat getTagFormat() {
		return tagFormat;
	}

    /**
     * @return The tokenizer to use for training and tagging. Default is {@link SimpleTokenizer}
     */
	public Tokenizer getTokenizer() {
		return tokenizer;
	}

    /**
     * @return Whether or not to use feature induction
     */
	public boolean isUseFeatureInduction() {
		return useFeatureInduction;
	}

    /**
     * @return Whether or not to include numeric normalization features
     */
	public boolean isUseNumericNormalization() {
		return useNumericNormalization;
	}

    /**
     * Outputs the settings for this configuration to the console, very useful for ensuring the configuration is set as desired prior to a training
     * run
     */
	public void log()
	{
		System.out.println("Lemmatiser: " + (lemmatiser == null ? null : lemmatiser.getClass().getName()));
		System.out.println("POSTagger: " + (posTagger == null ? null : posTagger.getClass().getName()));
		System.out.println("Tokenizer: " + tokenizer.getClass().getName());
		System.out.println("Tag format: " + tagFormat.name());
		System.out.println("PostProcessor: " + (postProcessor == null ? null : postProcessor.getClass().getName()));
		System.out.println("Using numeric normalization: " + useNumericNormalization);
		System.out.println("CRF order is " + order);
		System.out.println("Using feature induction: " + useFeatureInduction);
		System.out.println("Text textDirection: " + textDirection);
	}
	
}