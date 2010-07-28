/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.processing;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tagging.Mention;
import com.semanticscience.banner.tagging.TaggedToken;

/**
 * This class removes {@link Mention}s which contain a mismatched parenthesis ("(" or ")"), square bracket ("[" or "]") or curly bracket ("{" or
 * "}").
 * 
 * @author Bob
 */
public class ParenthesisPostProcessor implements PostProcessor
{

    /**
     * Creates a new instance of {@link ParenthesisPostProcessor}
     */
    public ParenthesisPostProcessor()
    {
        // Empty
    }


    public static boolean isStart(String text)
    {
        if (text.equals("("))
            return true;
        if (text.equals("["))
            return true;
        if (text.equals("{"))
            return true;
        return false;
    }


    public static boolean isEnd(String text)
    {
        if (text.equals(")"))
            return true;
        if (text.equals("]"))
            return true;
        if (text.equals("}"))
            return true;
        return false;
    }


    private static boolean isMismatched(Mention mention)
    {
        List<TaggedToken> tokens = mention.getTaggedTokens();
        boolean mismatched = false;
        LinkedList<Integer> startMatch = new LinkedList<Integer>();
        for (int i = 0; i < tokens.size(); i++)
        {
            TaggedToken token = tokens.get(i);
            if (ParenthesisPostProcessor.isStart(token.getToken().getText()))
            {
                startMatch.add(i);
            }
            else if (ParenthesisPostProcessor.isEnd(token.getToken().getText()))
            {
                if (startMatch.size() > 0)
                {
                    startMatch.removeLast();
                }
                else
                {
                    mismatched = true;
                }
            } // TODO Else handle quotes
        }
        return mismatched || startMatch.size() != 0;
    }


    /**
     * Removes {@link Mention}s which contain a mismatched parenthesis ("(" or ")"), square bracket ("[" or "]") or curly bracket ("{" or "}").
     */
    public void postProcess(Sentence sentence)
    {
        List<Mention> mentions = new ArrayList<Mention>(sentence.getMentions());
        for (Mention mention : mentions)
        {
            if (ParenthesisPostProcessor.isMismatched(mention))
                sentence.removeMention(mention);
        }
    }

}