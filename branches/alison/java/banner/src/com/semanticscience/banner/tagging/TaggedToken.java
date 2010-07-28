/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.tagging;

import com.semanticscience.banner.Sentence;
import com.semanticscience.banner.tokenization.Token;

/**
 * Represents a {@link Token} that has been identified by a {@link Tagger} as part of 1 or 0 {@link Mention}s. Note that this class does not extend
 * {@link Token}, nor is this class the primary internal representation for mentions. Rather, this is a convenience class whose instances are created
 * on demand
 * 
 * @author Bob
 */
public class TaggedToken {

	private Sentence sentence;
	private Mention mention;
	private int index; // Position in the sentence
	
    /**
     * Creates a new {@link TaggedToken}
     * 
     * @param sentence
     * @param mention
     * @param index
     */
	public TaggedToken(Sentence sentence, Mention mention, int index) {
		this.sentence = sentence;
		this.mention = mention;
		if (mention != null && !mention.getSentence().equals(sentence))
			throw new IllegalArgumentException();
		this.index = index;
		if (index < 0 || index >= sentence.getTokens().size())
			throw new IllegalArgumentException();
		if (mention != null && (index < mention.getStart() || index >= mention.getEnd()))
			throw new IllegalArgumentException();
	}

    /**
     * @return The {@link Token} to which this {@link TaggedToken} refers
     */
	public Token getToken() {
		return sentence.getTokens().get(index);
	}
	/**
     * @param format
     *        The {@link TagFormat} to use
     * @return The {@link TagPosition} representing the position of this token within the mention (i.e. I, O, B, E, or W)
     */
	public TagPosition getPosition(TagFormat format)
	{
		return TagPosition.getPostion(mention, index).convert(format);
	}

/**
 * @param format
 *        The {@link TagFormat} to use
 * @return A {@link String} consisting of the text of the token, a pipe ("|"), and the tag for this token, as returned by getTag(TagFormat)
 */
    public String getText(TagFormat format)
	{
		return getToken().getText() + "|" + getTag(format);
	}

    /**
     * @param format
     *        The {@link TagFormat} to use
     * @return A {@link String} consisting of the {@link TagPosition} for this token. If the token is part of a {@link Mention}, this is follwed by a
     *         dash ("-"), and the {@link MentionType} for the {@link Mention}
     */
	public String getTag(TagFormat format)
	{
		if (mention == null)
			return TagPosition.O.name();
		return getPosition(format).name() + "-" + mention.getType().getText();
	}

	public enum TagFormat
	{
		IO, IOB, IOBEW;
	}
	
	public enum TagPosition
	{
		I, O, B, E, W;
		
		public TagPosition convert(TagFormat format)
		{
			if (this == I || this == O)
				return this;
			if (format == TagFormat.IO)
				return I;
			if (format == TagFormat.IOB)
				if (this == E)
					return I;
				else
					return B;
			return this; 
		}

		public static TagPosition getPostion(Mention mention, int index)
		{
			if (mention == null)
				return O;
			if (index < mention.getStart() || index >= mention.getEnd())
				throw new IllegalArgumentException();
			if (mention.length() == 1)
				return W;
			if (index == mention.getStart())
				return B;
			if (index == mention.getEnd() - 1)
				return E;
			return I;
		}
	}

    /**
     * @return The {@link Mention} for this token, or <code>null</code> if this token is not part of a {@link Mention}
     */
	public Mention getMention() {
		return mention;
	}
}