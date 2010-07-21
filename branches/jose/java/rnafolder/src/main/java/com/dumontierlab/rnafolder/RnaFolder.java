package com.dumontierlab.rnafolder;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * This class executes RNAfold :)
 * @author Jose Cruz-Toledo
 *
 */

public class RnaFolder {
	
	/**
	 * Default constructor
	 */
	public RnaFolder(){
		
	}
	
	/**
	 * This method creates a simple shell script that allows the execution of
	 * RNAfold 
	 * @param aScript String containing the script that is to be created
	 */
	public void createShellScript(String aScript){
		String scriptContents = aScript;
		try {
			FileWriter fw = new FileWriter("/tmp/rnafolder.sh");
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(scriptContents);
			bw.close();
		} catch (IOException e) {
			System.out.println("Could not write file!\nError 66-43");
			e.printStackTrace();
		}
	}
	
	/**
	 * This static method fetches the input stream from a process
	 * reads it into a string
	 * @param aProc
	 * @return the contents of the input stream of aProc
	 */
	public static String writeProcessOutput(Process aProc){
		InputStreamReader tmpReader = new  InputStreamReader(new BufferedInputStream(aProc.getInputStream()));
		BufferedReader reader = new BufferedReader(tmpReader);
		String returnMe ="";
		while(true){
			String line ="";
			try {
				line = reader.readLine();
			} catch (IOException e) {
				System.out.println("Could not read input file");
				e.printStackTrace();
				System.exit(-1);
			}
			if(line == null)
				break;
			returnMe += line+"\n";
		}//while
		return returnMe;
	}//writeProcessOutput
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

}
