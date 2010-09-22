package com.dumontierlab.rsync_parser;

import java.io.File;
import java.util.Iterator;
import java.util.LinkedList;

public class parserRunnerTest {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		File logFile = new File("/tmp/mylog.log");
		File mirrDir = new File("/opt/data/pdb/xml");
		RunRsync r = new RunRsync(logFile, mirrDir);
		RsyncParser rp = new RsyncParser(logFile);
		LinkedList<String> modded = rp.getModifiedEntries();
		Iterator <String> itr = modded.iterator();
		while(itr.hasNext()){
			System.out.println(itr.next());
		}
	}

}
