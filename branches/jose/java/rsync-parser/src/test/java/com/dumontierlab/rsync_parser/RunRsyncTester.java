package com.dumontierlab.rsync_parser;

import java.io.File;

public class RunRsyncTester {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		RunRsync r = new RunRsync(new File("/tmp/mylog.log"));
		System.out.println("im done");
	}

}
