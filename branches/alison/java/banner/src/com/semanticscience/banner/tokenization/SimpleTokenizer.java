/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Tokens ouput by this tokenizer consist of a contiguous block of alphanumeric characters or a single punctuation mark. Note, therefore, that any
 * construction which contains a punctuation mark (such as a contraction or a real number) will necessarily span over at least three tokens.
 * 
 * @author Bob
 */
public class SimpleTokenizer implements Tokenizer
{

    private static boolean isPunctuation(char ch)
    {
        return ("`~!@#$%^&*()-=_+[]\\{}|;':\",./<>?".indexOf(ch) != -1);
    }


    public SimpleTokenizer()
    {
        // Empty
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
            else if (Character.isLetter(current) || Character.isDigit(current))
            {
                if (!Character.isLetter(next) && !Character.isDigit(next))
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