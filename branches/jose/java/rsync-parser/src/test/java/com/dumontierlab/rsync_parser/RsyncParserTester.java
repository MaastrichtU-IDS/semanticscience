package com.dumontierlab.rsync_parser;

import java.io.File;
import java.util.Iterator;
import java.util.LinkedList;

public class RsyncParserTester {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		File aFile = new File("/home/jose/tmp/test.out");
		RsyncParser rp = new RsyncParser(aFile);
		
		LinkedList <String> ll = rp.getDeletedEntries();
		LinkedList <String> ll2 = rp.getModifiedEntries();
		
		Iterator <String> itr = ll.iterator();
		Iterator <String> itr2 = ll2.iterator();
		while(itr.hasNext()){
			System.out.println("Delete: " + itr.next());
		}
		while(itr2.hasNext()){
			System.out.println("Add or Modify: " + itr2.next());
		}
	}

}
