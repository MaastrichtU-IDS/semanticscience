/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import java.util.List;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tokenization.Token;

/**
 * Instances of this class represent the mention of an entity within a {@link Sentence}. Mentions are defined in terms of full tokens, and therefore
 * finding mentions (the job of a {@link Tagger}) requires tokenization first.
 * 
 * @author Bob
 */
public class Mention
{

    private Sentence sentence;
    private MentionType type;
    private int start;
    private int end;


    public Mention(Sentence sentence, MentionType type, int start, int end)
    {
        if (sentence == null)
            throw new IllegalArgumentException();
        this.sentence = sentence;
        if (type == null)
            throw new IllegalArgumentException();
        this.type = type;
        if (start < 0)
            throw new IllegalArgumentException();
        this.start = start;
        if (end > sentence.getTokens().size())
            throw new IllegalArgumentException();
        this.end = end;
        if (length() <= 0)
            throw new IllegalArgumentException("Illegal length - start: " + start + " end: " + end);
    }


    /**
     * @return A {@link MentionType} indicating the type of entity being mentioned
     */
    public MentionType getType()
    {
        return type;
    }


    /**
     * @return The {@link Sentence} containing this {@link Mention}
     */
    public Sentence getSentence()
    {
        return sentence;
    }


    /**
     * @return The {@link Token}s which comprise this {@link Mention}
     */
    public List<Token> getTokens()
    {
        return sentence.getTokens().subList(start, end);
    }


    /**
     * @return A representation of this {@link Mention}, as a list of {@link TaggedToken}s
     */
    public List<TaggedToken> getTaggedTokens()
    {
        return sentence.getTaggedTokens().subList(start, end);
    }


    /**
     * @return The number of tokens this {@link Mention} contains
     */
    public int length()
    {
        return end - start;
    }


    /**
     * @return The original text of this {@link Mention}
     */
    public String getText()
    {
        return sentence.getText().substring(getStartChar(), getEndChar());
    }


    /**
     * Determines whether this {@link Mention} contains the specified {@link Mention}
     * 
     * @param mention
     * @return <code>true</code> if this {@link Mention} contains the specified {@link Mention}, <code>false</code> otherwise
     */
    public boolean contains(Mention mention)
    {
        return sentence.equals(mention.sentence) && start <= mention.start && end >= mention.end;
    }


    public boolean contains(int tokenIndex)
    {
        return tokenIndex >= start && tokenIndex < end;
    }


    /**
     * @return The index of the last token in this {@link Mention}
     */
    public int getEnd()
    {
        return end;
    }


    /**
     * @return The index of the first token in this {@link Mention}
     */
    public int getStart()
    {
        return start;
    }


    public int getEndChar()
    {
        return sentence.getTokens().get(end - 1).getEnd();
    }


    public int getStartChar()
    {
        return sentence.getTokens().get(start).getStart();
    }


    /**
     * Determines whether this {@link Mention} overlaps the specified {@link Mention}
     * 
     * @param mention2
     * @return <code>true</code> if this Mention overlaps with the specified {@link Mention}, <code>false</code> otherwise
     */
    public boolean overlaps(Mention mention2)
    {
        return end > mention2.start && start < mention2.end;
    }


    // ----- Object overrides -----

    @Override
    public String toString()
    {
        return (type == null ? "null" : type.getText()) + ": " + getText();
    }


    @Override
    public int hashCode()
    {
        final int PRIME = 31;
        int result = 1;
        result = PRIME * result + end;
        result = PRIME * result + sentence.hashCode();
        result = PRIME * result + start;
        result = PRIME * result + type.hashCode();
        return result;
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
        final Mention other = (Mention)obj;
        if (!sentence.equals(other.sentence))
            return false;
        if (!type.equals(other.type))
            return false;
        if (start != other.start)
            return false;
        if (end != other.end)
            return false;
        return true;
    }

}