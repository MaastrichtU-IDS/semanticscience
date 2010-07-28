/* 
 Copyright (c) 2007 Arizona State University, Dept. of Computer Science and Dept. of Biomedical Informatics.
 This file is part of the BANNER Named Entity Recognition System, http://banner.sourceforge.net
 This software is provided under the terms of the Common Public License, version 1.0, as published by http://www.opensource.org.  For further information, see the file 'LICENSE.txt' included with this distribution.
 */

package com.semanticscience.banner.util;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * A Trie (also known as a prefix tree) essentially maps from a list of objects (keys) to a value. The interface is very similar, therefore, to the
 * interface for {@link Map}, except that the key is a {@link List} of objects. This data structure allows searching in O(m) time, where m is the
 * depth of the tree.
 * 
 * @author Bob
 * @param <K>
 * @param <V>
 */
public class Trie<K, V>
{

    private V value;
    private Map<K, Trie<K, V>> children;


    public Trie()
    {
        this(null);
    }


    public Trie(V value)
    {
        this.value = value;
        children = new HashMap<K, Trie<K, V>>();
    }


    public V getValue()
    {
        return value;
    }


    public void setValue(V value)
    {
        this.value = value;
    }


    public V add(List<K> keys, V value)
    {
        Trie<K, V> current = this;
        Iterator<K> keyIterator = keys.iterator();
        while (current != null && keyIterator.hasNext())
        {
            K nextKey = keyIterator.next();
            Trie<K, V> next = current.children.get(nextKey);
            if (next == null)
            {
                next = new Trie<K, V>();
                current.children.put(nextKey, next);
            }
            current = next;
        }
        V old = current.value;
        current.value = value;
        return old;
    }


    public Trie<K, V> getChild(K key)
    {
        return children.get(key);
    }


    public V getValue(List<K> keys)
    {
        Trie<K, V> current = this;
        Iterator<K> keyIterator = keys.iterator();
        while (current != null && keyIterator.hasNext())
        {
            K nextKey = keyIterator.next();
            current = current.children.get(nextKey);
        }
        if (current == null)
            return null;
        return current.getValue();
    }


    /**
     * Returns the number of mappings in this {@link Trie}
     * 
     * @return The number of mappings in this {@link Trie}
     */
    public int size()
    {
        int size = 0;
        if (value != null)
            size++;
        for (Trie<K, V> child : children.values())
            size += child.size();
        return size;
    }

}