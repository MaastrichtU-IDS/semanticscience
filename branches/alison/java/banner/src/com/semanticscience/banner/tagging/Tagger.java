/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import com.semanticscience.banner.Sentence;

/**
 * {@link Tagger}s add {@link Mention}s to a {@link Sentence} which has been tokenized. The Sentence may or may not already have some Mentions
 * already identified.
 */
public interface Tagger
{

    /**
     * Add {@link Mention}s to the {@link Sentence}. The {@link Sentence} must have been tokenized previously.
     * 
     * @param sentence
     *        The sentence to which {@link Mention}s should be added
     */
    public void tag(Sentence sentence);

}