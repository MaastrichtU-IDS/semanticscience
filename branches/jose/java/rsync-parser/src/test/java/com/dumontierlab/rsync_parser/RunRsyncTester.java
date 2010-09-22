package com.dumontierlab.rsync_parser;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;

public class RunRsyncTester {

	/**
	 * @param args
	 * @throws IOException 
	 * @throws FileNotFoundException 
	 */
	public static void main(String[] args) throws FileNotFoundException, IOException {
		RunRsync r = new RunRsync(new File("/tmp/mylog.log"), new File("/opt/data/pdb/xml"));

	}
	
}
