/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Tokens returned by this class consist primarily of contiguous alphanumeric characters or single punctuation marks, however certain constructs such
 * as real numbers, percentages are recognized and returned as a single token.
 * 
 * @author Bob
 */
public class BaseTokenizer implements Tokenizer
{

    public BaseTokenizer()
    {
        // Empty
    }


    public void tokenize(Sentence sentence)
    {
        new InternalTokenizer(sentence);
    }

    private static class InternalTokenizer
    {
        Sentence sentence;

        String text;

        int current;


        public InternalTokenizer(Sentence sentence)
        {
            this.sentence = sentence;
            text = sentence.getText();
            current = 0;
            Token token = getToken();
            while (token != null)
            {
                sentence.addToken(token);
                token = getToken();
            }
        }


        // TODO Try fixing so possessives "'s" and "'" at end of an all-alpha token are included in the token

        public Token getToken()
        {
            getWhitespace();
            if (!hasChar(current))
                return null;
            Token token;
            token = getNumber();
            if (token != null)
                return token;
            token = getAlphaNumeric();
            if (token != null)
                return token;
            token = getPunctuation();
            if (token != null)
                return token;
            return null;
        }


        private Token getNumber()
        {
            // Verify previous character was acceptable
            if (current > 0 && Character.isLetter(text.charAt(current - 1)))
                return null;
            int end = current;
            // Get + or -
            if (hasChar(end) && (text.charAt(end) == '+' || text.charAt(end) == '-'))
            {
                end++;
            }
            // Get first set of digits
            boolean foundDigit = false;
            while (hasChar(end) && Character.isDigit(text.charAt(end)))
            {
                end++;
                foundDigit = true;
            }
            // Get "." and second set of digits
            if (hasChar(end) && text.charAt(end) == '.' && hasChar(end + 1) && Character.isDigit(text.charAt(end + 1)))
            {
                end++;
                while (hasChar(end) && Character.isDigit(text.charAt(end)))
                {
                    end++;
                    foundDigit = true;
                }
            }
            // Get percentage sign
            if (hasChar(end) && text.charAt(end) == '%')
            {
                end++;
            }
            Token token = null;
            if (foundDigit && (!hasChar(end) || !Character.isLetter(text.charAt(end))))
            {
                token = new Token(sentence, current, end);
                current = end;
            }
            return token;
        }


        private Token getAlphaNumeric()
        {
            int end = current;
            while (hasChar(end) && (Character.isLetter(text.charAt(end)) || Character.isDigit(text.charAt(end))))
                end++;
            Token token = null;
            if (end > current)
            {
                token = new Token(sentence, current, end);
                current = end;
            }
            return token;
        }


        private Token getPunctuation()
        {
            Token token = null;
            if (isPunctuation(text.charAt(current)))
            {
                token = new Token(sentence, current, current + 1);
                current++;
            }
            return token;
        }


        private static boolean isPunctuation(char ch)
        {
            return ("`~!@#$%^&*()-=_+[]\\{}|;':\",./<>?".indexOf(ch) != -1);
        }


        private boolean hasChar(int index)
        {
            return index < text.length();
        }


        private boolean getWhitespace()
        {
            boolean found = false;
            while (hasChar(current) && Character.isWhitespace(text.charAt(current)))
            {
                found = true;
                current++;
            }
            return found;
        }
    }
}