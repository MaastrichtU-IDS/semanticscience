package com.dumontierlab.mcannotator;

import java.io.File;
import java.io.IOException;

import com.dumontierlab.mcannotator.bin.RunMCAnnotate;

import junit.framework.TestCase;

public class RunMCAnnotateTest extends TestCase{
	public RunMCAnnotateTest(String testName){
		super(testName);
	}
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		//RunMCA by specifying only the input directory
		RunMCAnnotate r = new RunMCAnnotate(new File("/home/jose/tmp/input/1Y26.pdb"));
		r.run();
		//Run MCA on an input directory and an output directory
		RunMCAnnotate r2 = new RunMCAnnotate(new File("/home/jose/tmp/input"), new File("/home/jose/tmp/output"));
		r2.run();
		
	}

}
