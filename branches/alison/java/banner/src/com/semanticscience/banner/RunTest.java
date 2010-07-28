package com.semanticscience.banner;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.semanticscience.banner.processing.ParenthesisPostProcessor;
import com.semanticscience.banner.tagging.CRFTagger;
import com.semanticscience.banner.tokenization.Tokenizer;

public class RunTest {

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub

		// Get the properties information from file
		BannerProperties properties = BannerProperties.load(new File("/home/alison/Programs/BANNER/banner.properties"));
		Tokenizer tokenizer = properties.getTokenizer();
		CRFTagger tagger = CRFTagger.load(new File("/home/alison/testmodel"), properties.getLemmatiser(), properties.getPosTagger());
		ParenthesisPostProcessor postProcessor = (ParenthesisPostProcessor) properties.getPostProcessor();
		
		
		
		List<String> sentenceTextList = new ArrayList<String>();
		sentenceTextList.add("Detection of anti-lymphocyte antibodies using the immunoperoxidase antiglobulin technic.");
		sentenceTextList.add("Basal FSH and LH levels were significantly lower in addicts; after GnRH stimulation the addicts' FSH and LH values increased but not significantly compared to controls.");
		sentenceTextList.add("In this article, the clinical actions of the principal dopamine receptor stimulating agents (apomorphine and its derivatives; piribedil, rye-ergot derivatives) are discussed on the basis of their biochemical and pharmacological properties.");
		
		for (String sentenceText : sentenceTextList)
		{
		    Sentence sentence = new Sentence(sentenceText);
		    tokenizer.tokenize(sentence);
		    tagger.tag(sentence);
		    System.out.println("Sentence: "+sentence.toString());
		    
		    if (postProcessor != null)
		        postProcessor.postProcess(sentence);
		    System.out.println(sentence.getTrainingText(properties.getTagFormat()));
		}

		
	}

}
