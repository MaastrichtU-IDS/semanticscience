/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tokenization;

import com.semanticscience.banner.Sentence;

/**
 * Tokenizers take the text of a sentence and turn it into a Sentence object. They do not fill in the Mentions in the sentence, and the Tokens which
 * make up the sentence have no fields besides the text field filled in.
 */
public interface Tokenizer
{

    /**
     * Tokenizes the given {@link Sentence}
     * 
     * @param sentence
     *        The {@link Sentence} to tokenize
     */
    public void tokenize(Sentence sentence);
}