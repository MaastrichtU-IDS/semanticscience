/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tokenization.Token;
import com.semanticscience.banner.tokenization.Tokenizer;
import com.semanticscience.banner.util.Trie;

/**
 * This class represents a very simple dictionary-based tagger. All text subsequences which match an entry will be tagged, without regard to the
 * context. No facilities for text processing (such as case-folding) are provided.
 * 
 * @author Bob
 */
public class DictionaryTagger implements Tagger
{

    public static final String delimiter = "-->";

    private Tokenizer tokenizer;
    private boolean filterContainedMentions;
    private Trie<String, MentionType> entities;


    /**
     * Creates a new {@link DictionaryTagger}
     * 
     * @param tokenizer
     *        The {@link Tokenizer} to use for breaking new entries into tokens
     * @param filterContainedMentions
     *        Whether mentions which are contained in another mention should be added
     */
    public DictionaryTagger(Tokenizer tokenizer, boolean filterContainedMentions)
    {
        this.tokenizer = tokenizer;
        this.filterContainedMentions = filterContainedMentions;
        entities = new Trie<String, MentionType>();
    }


    private List<String> process(String input)
    {
        Sentence inputSentence = new Sentence(input);
        tokenizer.tokenize(inputSentence);
        List<Token> tokens = inputSentence.getTokens();
        List<String> output = new ArrayList<String>(tokens.size());
        for (int i = 0; i < tokens.size(); i++)
        {
            output.add(tokens.get(i).getText());
        }
        return output;
    }


    /**
     * Adds a single entry to the dictionary. The text is processed by the tokenizer and the resulting tokens are stored.
     * 
     * @param text
     *        The text to find
     * @param type
     *        The {@link MentionType} to tag the text with
     */
    public void add(String text, MentionType type)
    {
        MentionType previousType = entities.add(process(text), type);
        if (previousType != null && !previousType.equals(type))
            throw new IllegalArgumentException("Text is already associated with a different tag: " + text);
    }


    /**
     * Loads multiple entries of a single type to the dictionary by reading them from the specified {@link Reader}.
     * 
     * @param reader
     *        The {@link Reader} containing the entries to be added, one entry per line
     * @param type
     *        The {@link MentionType} for all entries to the dictionary
     * @throws IOException
     */
    public void add(Reader reader, MentionType type) throws IOException
    {
        BufferedReader buffered = new BufferedReader(reader);
        String line = buffered.readLine();
        while (line != null)
        {
            add(line.trim(), type);
            line = buffered.readLine();
        }
    }


    /**
     * Loads multiple entries to the dictionary by reading them from the specified {@link Reader}.
     * 
     * @param reader
     *        The {@link Reader} containing the entries to be added, one entry per line, in the format <entry>--><type>
     * @throws IOException
     */
    public void add(Reader reader) throws IOException
    {
        BufferedReader buffered = new BufferedReader(reader);
        String line = buffered.readLine();
        while (line != null)
        {
            String[] split = line.split(delimiter);
            if (split.length != 2)
                throw new IllegalArgumentException();
            add(split[0].trim(), MentionType.getType(split[1].trim()));
            line = buffered.readLine();
        }
        // System.out.println("Size is now " + entities.size());
    }


    public void tag(Sentence sentence)
    {
        List<Token> tokens = sentence.getTokens();
        // Lookup mentions
        ArrayList<Mention> mentions = new ArrayList<Mention>();
        for (int startIndex = 0; startIndex < tokens.size(); startIndex++)
        {
            Trie<String, MentionType> t = entities;
            for (int currentIndex = startIndex; currentIndex < tokens.size() && t != null; currentIndex++)
            {
                MentionType type = t.getValue();
                if (type != null)
                    mentions.add(new Mention(sentence, type, startIndex, currentIndex));
                Token currentToken = tokens.get(currentIndex);
                t = t.getChild(currentToken.getText());
            }
        }
        // Add mentions found
        Iterator<Mention> mentionIterator = mentions.iterator();
        while (mentionIterator.hasNext())
        {
            Mention mention = mentionIterator.next();
            boolean contained = false;
            for (Mention mention2 : mentions)
                contained |= !mention2.equals(mention) && mention2.contains(mention);
            if (!filterContainedMentions || !contained)
                sentence.addMention(mention);
        }
    }


    /**
     * @return The number of entries in this dictionary
     */
    public int size()
    {
        return entities.size();
    }
}