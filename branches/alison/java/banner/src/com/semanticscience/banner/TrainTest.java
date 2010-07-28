package com.semanticscience.banner;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

import com.semanticscience.banner.tagging.CRFTagger;
import com.semanticscience.banner.tagging.MentionType;
import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tokenization.Tokenizer;
import com.semanticscience.banner.Sentence;

//why is this here???
//import edu.umass.cs.mallet.projects.seg_plus_coref.anaphora.Mention;

public class TrainTest {

	/**
	 * @param args
	 * @throws FileNotFoundException 
	 */
	public static void main(String[] args) throws FileNotFoundException {

		// Get the properties information from file
		BannerProperties properties = BannerProperties.load(new File("/home/alison/Programs/BANNER/banner.properties"));
		Tokenizer tokenizer = properties.getTokenizer();
		
		// Load in the sentences
		Sentence s1 = new Sentence("Comparison with alkaline phosphatases and 5-nucleotidase");
		tokenizer.tokenize(s1);
		s1.addMention(new Mention(s1, MentionType.getType("geneProduct"), 2, 4));
		
		Sentence s2 = new Sentence("The//DT variable/JJ HMG/NN dosage/NN regimen/NN was/VBZ found/VBZ to/DT offer/VBZ no/DT advantages/NNS when compared with our standard daily dosage regimen.");
		tokenizer.tokenize(s2);
		s2.addMention(new Mention(s2, MentionType.getType("geneProduct"), 2, 3));
		
		Sentence s3 = new Sentence("Serum gamma glutamyltransferase in the diagnosis of liver disease in cattle.");
		tokenizer.tokenize(s3);
		s3.addMention(new Mention(s3, MentionType.getType("geneProduct"), 0, 2));
		
		Sentence s4 = new Sentence("The response of serum GH to arginine infusion was normal, while that to insulin-induced hypoglycemia was poor.");
		tokenizer.tokenize(s4);
		s4.addMention(new Mention(s4, MentionType.getType("geneProduct"), 14, 15));

		List<Sentence> sentences = new ArrayList<Sentence>();
		sentences.add(s1);
		sentences.add(s2);
		sentences.add(s3);
		sentences.add(s4);
		
		// Train the model
		CRFTagger tagger = CRFTagger.train(sentences, properties.getOrder(), properties.isUseFeatureInduction(), properties.getTagFormat(), properties.getTextDirection(), properties.getLemmatiser(), properties.getPosTagger(), properties.isUseNumericNormalization());
		// Output the model to file
		tagger.write(new File("/home/alison/testmodel"));
		System.out.println("Done writing model!!");
		
	}

}
