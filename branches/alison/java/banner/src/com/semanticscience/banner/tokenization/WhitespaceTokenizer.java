/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Instances of this class tokenize {@link Sentence}s only at whitespace characters. All other boundaries (such as between alphabetic characters and
 * punctuation) are ignored.
 * 
 * @author Bob
 */
public class WhitespaceTokenizer implements Tokenizer
{
    public WhitespaceTokenizer()
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
            else if (Character.isSpaceChar(next))
            {
                sentence.addToken(new Token(sentence, start, i));
                start = i;
            }
        }
        if (start < text.length())
            sentence.addToken(new Token(sentence, start, text.length()));
    }

}