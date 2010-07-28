/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import java.util.HashMap;
import java.util.Map;

/**
 * Instances of this class represent the type of a {@link Mention}. Instances of this class are kept in a static cache to ensure only one instance of
 * any type being in use. No processing is done on the text, however, so "Gene" is a different type than "GENE"
 * 
 * @author Bob
 */
public class MentionType
{

    private static final Map<String, MentionType> types = new HashMap<String, MentionType>();

    private String text;


    private MentionType()
    {
        // Not used
    }


    private MentionType(String text)
    {
        this.text = text;
    }


    public static MentionType getType(String text)
    {
        if (text == null)
            throw new IllegalArgumentException();
        MentionType type = types.get(text);
        if (type == null)
        {
            type = new MentionType(text);
            types.put(text, type);
        }
        return type;
    }


    public String getText()
    {
        return text;
    }


    @Override
    public String toString()
    {
        return text;
    }


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
        final MentionType other = (MentionType)obj;
        if (!text.equals(other.text))
            return false;
        return true;
    }

}