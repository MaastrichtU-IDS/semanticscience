/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.bc2;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Set;

public class CheckTagVariations extends Base
{
    /**
     * @param args
     */
    public static void main(String[] args) throws IOException
    {
        long start = System.currentTimeMillis();
        BufferedReader tagFile = new BufferedReader(new FileReader(args[0]));
        BufferedReader alternateFile = new BufferedReader(new FileReader(args[1]));

        HashMap<String, LinkedList<Tag>> tags = getTags(tagFile);
        tagFile.close();

        HashMap<String, LinkedList<Tag>> alternates = getTags(alternateFile);
        alternateFile.close();

        Set<Tag> overlaps = new HashSet<Tag>();

        for (String id : tags.keySet())
        {
            LinkedList<Tag> alternateTags = alternates.get(id);
            if (alternateTags != null)
            {
                for (Tag tag : tags.get(id))
                {
                    for (Tag alternate : alternateTags)
                    {
                        if (tag.overlaps(alternate))
                            overlaps.add(tag);
                    }
                }
            }
        }
        System.out.println("Overlaps: " + overlaps.size());
        System.out.println("Took " + (System.currentTimeMillis() - start) + " ms");
    }

}