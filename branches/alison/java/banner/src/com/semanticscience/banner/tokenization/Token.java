/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Represents a single token of text. Note that the token does not know what Mention it is a part of, if any.
 * 
 * @author Bob
 */
public class Token
{

    private Sentence sentence;
    private int start;
    private int end;


    /**
     * The token is from character start to character end - 1
     * 
     * @param sentence
     * @param start
     * @param end
     */
    public Token(Sentence sentence, int start, int end)
    {
        if (sentence == null)
            throw new IllegalArgumentException();
        if (start < 0)
            throw new IllegalArgumentException("Start may not be less than 0: " + start);
        this.sentence = sentence;
        this.start = start;
        this.end = end;
        if (length() < 1)
            throw new IllegalArgumentException("End must be greater than start; start: " + start + " end: " + end);
    }


    /**
     * @return The {@link Sentence} for this {@link Token}
     */
    public Sentence getSentence()
    {
        return sentence;
    }


    /**
     * @return The text for this token
     */
    public String getText()
    {
        return sentence.getText(start, end);
    }


    /**
     * @return The start index for this token, inclusive
     */
    public int getStart()
    {
        return start;
    }


    /**
     * @return The end index for this token, exclusive
     */
    public int getEnd()
    {
        return end;
    }


    /**
     * @return The number of characters in this token
     */
    public int length()
    {
        return end - start;
    }


    // ----- Object overrides -----

    @Override
    public int hashCode()
    {
        final int PRIME = 31;
        int result = 1;
        result = PRIME * result + sentence.hashCode();
        result = PRIME * result + start;
        result = PRIME * result + end;
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
        final Token other = (Token)obj;
        if (!sentence.equals(other.sentence))
            return false;
        if (start != other.start)
            return false;
        if (end != other.end)
            return false;
        return true;
    }
}