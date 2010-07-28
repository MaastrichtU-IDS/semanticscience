/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Tokens output by this tokenizer contain either a contiguous string of letters, a contiguous string of numbers or a single punctuation mark.
 */
public class NaiveTokenizer implements Tokenizer
{

    public NaiveTokenizer()
    {
        // Empty
    }


    private static boolean isPunctuation(char ch)
    {
        return ("`~!@#$%^&*()-=_+[]\\{}|;':\",./<>?".indexOf(ch) != -1);
    }


    public void tokenize(Sentence sentence)
    {
        String text = sentence.getText();
        int start = 0;
        for (int i = 1; i - 1 < text.length(); i++)
        {
            char current = text.charAt(i - 1);
            char next = 0;
            if (i < text.length())
                next = text.charAt(i);
            if (Character.isSpaceChar(current))
            {
                start = i;
            }
            else if (Character.isLetter(current))
            {
                if (!Character.isLetter(next))
                {
                    sentence.addToken(new Token(sentence, start, i));
                    start = i;
                }
            }
            else if (Character.isDigit(current))
            {
                if (!Character.isDigit(next))
                {
                    sentence.addToken(new Token(sentence, start, i));
                    start = i;
                }
            }
            else if (isPunctuation(current))
            {
                sentence.addToken(new Token(sentence, start, i));
                start = i;
            }
        }
        if (start < text.length())
            sentence.addToken(new Token(sentence, start, text.length()));
    }
}