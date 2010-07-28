/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tagging.MentionType;
import com.semanticscience.banner.tagging.TaggedToken;
import com.semanticscience.banner.tagging.Tagger;
import com.semanticscience.banner.tagging.TaggedToken.TagFormat;
import com.semanticscience.banner.tagging.TaggedToken.TagPosition;
import com.semanticscience.banner.tokenization.Token;
import com.semanticscience.banner.tokenization.Tokenizer;
import com.semanticscience.banner.tokenization.WhitespaceTokenizer;

/**
 * This class represents a single sentence, and provides for the text to be tokenized and for mentions.
 * 
 * @author Bob
 */
public class Sentence
{

    private String tag;
    private String text;
    private List<Token> tokens;
    private List<Mention> mentions;


    private Sentence()
    {
        tokens = new ArrayList<Token>();
        mentions = new ArrayList<Mention>();
    }


    /**
     * Creates a new {@link Sentence} with the specified text and a <code>null</code> tag.
     * 
     * @param text
     *        The text of the sentence
     */
    public Sentence(String text)
    {
        this(null, text);
    }


    /**
     * Creates a new {@link Sentence} with the specified tag and text
     * 
     * @param tag
     *        The tag for the {@link Sentence}, which may be a unique identifier
     * @param text
     *        The text of the sentence
     */
    public Sentence(String tag, String text)
    {
        this.tag = tag;
        if (text == null)
            throw new IllegalArgumentException("Text cannot be null");
        text = text.trim();
        if (text.length() == 0)
            throw new IllegalArgumentException("Text must have length greater than 0");
        this.text = text;
        tokens = new ArrayList<Token>();
        mentions = new ArrayList<Mention>();
    }


    public static Sentence loadFromPiped(String tag, String pipedText)
    {
        Sentence sentence = new Sentence();
        sentence.tag = tag;
        String[] taggedTokens = pipedText.split("\\s+");
        StringBuffer sentenceText = new StringBuffer();
        TagPosition[] positions = new TagPosition[taggedTokens.length];
        MentionType[] types = new MentionType[taggedTokens.length];
        for (int i = 0; i < taggedTokens.length; i++)
        {
            String[] tokenSplit = taggedTokens[i].split("\\|");
            sentenceText.append(tokenSplit[0]);
            sentenceText.append(" ");
            // The tag string is e.g. "O" or "B-GENE"
            String[] tagSplit = tokenSplit[1].split("-");
            positions[i] = TagPosition.valueOf(tagSplit[0]);
            // TODO Verify that the type stays the same
            if (tagSplit.length == 2)
                types[i] = MentionType.getType(tagSplit[1]);
        }
        sentence.text = sentenceText.toString().trim();
        (new WhitespaceTokenizer()).tokenize(sentence);
        sentence.addMentions(positions, types);
        return sentence;
    }


    public static Sentence loadFromXML(String tag, String xmlText)
    {
        Sentence sentence = new Sentence();
        sentence.tag = tag;
        String[] pieces = xmlText.split("\\s+");
        StringBuffer sentenceText = new StringBuffer();
        for (int i = 0; i < pieces.length; i++)
        {
            if (!pieces[i].startsWith("<") || !pieces[i].endsWith(">"))
            {
                sentenceText.append(pieces[i]);
                sentenceText.append(" ");
            }
        }
        sentence.text = sentenceText.toString().trim();
        (new WhitespaceTokenizer()).tokenize(sentence);
        int index = 0;
        int mentionStart = -1;
        MentionType mentionType = null;
        for (int i = 0; i < pieces.length; i++)
        {
            if (pieces[i].startsWith("<") && pieces[i].endsWith(">"))
            {
                String typeStr = pieces[i];
                if (typeStr.startsWith("</"))
                {
                    if (mentionStart == -1 || mentionType == null)
                        throw new IllegalArgumentException("");
                    Mention mention = new Mention(sentence, mentionType, mentionStart, index);
                    sentence.mentions.add(mention);
                    mentionStart = -1;
                    mentionType = null;
                }
                else
                {
                    if (mentionStart != -1 || mentionType != null)
                        throw new IllegalArgumentException("");
                    mentionStart = index;
                    typeStr = typeStr.replace(">", "");
                    typeStr = typeStr.replace("<", "");
                    mentionType = MentionType.getType(typeStr);
                }
            }
            else
            {
                index++;
            }
        }
        return sentence;
    }


    public void inferTokenization(String tokenizedText)
    {
        if (tokens.size() != 0)
            throw new IllegalStateException();
        String[] split = tokenizedText.split("\\s+");
        int start = 0;
        for (int i = 0; i < split.length; i++)
        {
            while (Character.isWhitespace(text.charAt(start)))
                start++;
            if (!text.substring(start, start + split[i].length()).equals(split[i]))
                throw new IllegalArgumentException();
            tokens.add(new Token(this, start, start + split[i].length()));
            start += split[i].length();
        }
    }


    /**
     * Adds a {@link Token} to this {@link Sentence}. Normally called by instances of {@link Tokenizer}.
     * 
     * @param token
     */
    public void addToken(Token token)
    {
        // Add verification of no token overlap
        if (!token.getSentence().equals(this))
            throw new IllegalArgumentException();
        tokens.add(token);
    }


    /**
     * Adds a {@link Mention} to this Sentence, ignoring any potential overlap with existing {@link Mention}s. Normally called by instance of
     * {@link Tagger} or post-processors.
     * 
     * @param mention
     */
    public void addMention(Mention mention)
    {
        if (!mention.getSentence().equals(this))
            throw new IllegalArgumentException();
        mentions.add(mention);
    }


    /**
     * Adds a {@link Mention} to this Sentence or merges the {@link Mention} into an existing {@link Mention} which the new one would overlap.
     * Normally called by instance of {@link Tagger} or post-processors.
     * 
     * @param mention
     */
    public void addOrMergeMention(Mention mention)
    {
        if (!mention.getSentence().equals(this))
            throw new IllegalArgumentException();
        List<Mention> overlapping = new ArrayList<Mention>();
        for (Mention mention2 : mentions)
        {
            if (mention.overlaps(mention2) && mention.getType().equals(mention2.getType()))
                overlapping.add(mention2);
        }
        if (overlapping.size() == 0)
        {
            mentions.add(mention);
        }
        else
        {
            for (Mention mention2 : overlapping)
            {
                mentions.remove(mention2);
                mentions.add(new Mention(this, mention.getType(), Math.min(mention.getStart(), mention2.getStart()), Math.max(mention.getEnd(),
                                                                                                                              mention2.getEnd())));
            }
        }
    }


    public boolean removeMention(Mention mention)
    {
        return mentions.remove(mention);
    }


    public void addMentions(TagPosition[] positions, MentionType[] types)
    {
        // TODO Verify correct transitions & type continuity
        if (tokens.size() != positions.length)
            throw new IllegalArgumentException();
        if (tokens.size() != types.length)
            throw new IllegalArgumentException();
        int startIndex = -1;
        for (int i = 0; i < positions.length; i++)
        {
            if (positions[i] == TagPosition.O)
            {
                if (startIndex != -1)
                    addOrMergeMention(new Mention(this, types[i - 1], startIndex, i));
                startIndex = -1;
            }
            else if (positions[i] == TagPosition.B)
            {
                if (startIndex != -1)
                    addOrMergeMention(new Mention(this, types[i - 1], startIndex, i));
                startIndex = i;
            }
            else if (positions[i] == TagPosition.W)
            {
                if (startIndex != -1)
                    addOrMergeMention(new Mention(this, types[i - 1], startIndex, i));
                startIndex = i;
            }
            else
            {
                if (startIndex == -1)
                    startIndex = i;
            }
        }
    }


    /**
     * @return the tag for the {@link Sentence}
     */
    public String getTag()
    {
        return tag;
    }


    /**
     * @return The text of the {@link Sentence}
     */
    public String getText()
    {
        return text;
    }


    /**
     * @return The tokenized form of the text for this {@link Sentence}. Formed by placing a single space character between the text for each token
     *         in the {@link Sentence}.
     */
    public String getTokenizedText()
    {
        StringBuffer text2 = new StringBuffer();
        for (Token token : tokens)
        {
            text2.append(token.getText());
            text2.append(" ");
        }
        return text2.toString().trim();
    }


    public String getText(int start, int end)
    {
        return text.substring(start, end);
    }


    /**
     * @return The {@link List} of {@link Token}s for this {@link Sentence}
     */
    public List<Token> getTokens()
    {
        return Collections.unmodifiableList(tokens);
    }


    /**
     * @return The {@link List} of {@link Mention}s for this {@link Sentence}. This list may or may not contain overlaps
     */
    public List<Mention> getMentions()
    {
        return Collections.unmodifiableList(mentions);
    }


    /**
     * Assumes that each token is tagged either 0 or 1 times
     */
    private Mention getMention(int tokenIndex)
    {
        Mention mention = null;
        for (Mention mention2 : mentions)
        {
            if (mention2.contains(tokenIndex))
                if (mention == null)
                    mention = mention2;
                else
                    throw new IllegalArgumentException();
        }
        return mention;
    }


    public List<TaggedToken> getTaggedTokens()
    {
        List<TaggedToken> taggedTokens = new ArrayList<TaggedToken>();
        for (int i = 0; i < tokens.size(); i++)
        {
            taggedTokens.add(new TaggedToken(this, getMention(i), i));
        }
        return Collections.unmodifiableList(taggedTokens);
    }


    /**
     * Returns a text representation of the tagging for this {@link Sentence}, using the specified {@link TagFormat}. In other words, each token in
     * the sentence is given a tag indicating its position in a mention or that the token is not a mention.
     * 
     * @param format
     *        The {@link TagFormat} to use
     * @return A text representation of the tagging for this {@link Sentence}, using the specified {@link TagFormat}
     */
    public String getTrainingText(TagFormat format)
    {
        return getTrainingText(format, false);
    }


    /**
     * Returns a text representation of the tagging for this {@link Sentence}, using the specified {@link TagFormat}. In other words, each token in
     * the sentence is given a tag indicating its position in a mention or that the token is not a mention. Assumes that each token is tagged either 0
     * or 1 times.
     * 
     * @param format
     *        The {@link TagFormat} to use
     * @param reverse
     *        Whether to return the text in reverse order
     * @return A text representation of the tagging for this {@link Sentence}, using the specified {@link TagFormat}
     */
    public String getTrainingText(TagFormat format, boolean reverse)
    {
        List<TaggedToken> taggedTokens = new ArrayList<TaggedToken>(getTaggedTokens());
        if (reverse)
            Collections.reverse(taggedTokens);
        StringBuffer trainingText = new StringBuffer();
        for (TaggedToken token : taggedTokens)
        {
            trainingText.append(token.getText(format));
            trainingText.append(" ");
        }
        return trainingText.toString().trim();
    }


    public List<Mention> getMentions(Token token)
    {
        ArrayList<Mention> mentionsForToken = new ArrayList<Mention>();
        for (Mention mention : mentions)
            if (mention.getTokens().contains(token))
                mentionsForToken.add(mention);
        return Collections.unmodifiableList(mentionsForToken);
    }


    /**
     * Returns a SGML/XML representation of the tagged sentence. Mentions are surrounded by opening and closing tags containing the mention type.
     * Assumes that each token is tagged either 0 or 1 times.
     * 
     * @return A SGML/XML representation of the tagged sentence
     */
    public String getSGML()
    {
        List<TaggedToken> taggedTokens = getTaggedTokens();
        StringBuffer text2 = new StringBuffer();
        for (int i = 0; i < taggedTokens.size(); i++)
        {
            TaggedToken token = taggedTokens.get(i);
            TagPosition position = token.getPosition(TagFormat.IOBEW);
            if (position == TagPosition.B || position == TagPosition.W)
                text2.append("<" + token.getMention().getType().getText() + "> ");
            text2.append(token.getToken().getText() + " ");
            if (position == TagPosition.E || position == TagPosition.W)
                text2.append("</" + token.getMention().getType().getText() + "> ");
        }
        return text2.toString().trim();
    }


    // ----- Object overrides -----

    @Override
    public int hashCode()
    {
        return text.hashCode();
    }


    @Override
    public boolean equals(Object obj)
    {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        final Sentence other = (Sentence)obj;
        if (text == null)
        {
            if (other.text != null)
                return false;
        }
        else if (!text.equals(other.text))
            return false;
        return true;
    }
}
