package com.dumontierlab.rnafolder;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;

/**
 * Hello world!
 *
 */
public class App {
	public App(){
		
	}
	
	public void run(){
		
	}
	
    public static void main( String[] args ) throws IOException, InterruptedException{
    	String [] cmdArr = {"sh","-c", "RNAfold"};
        ProcessBuilder pb = new ProcessBuilder(cmdArr);
    	pb.redirectErrorStream(true);
    	Process p = pb.start();
    	BufferedReader processOutput = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
    	//while((line ))
    	
    	/*Runtime runtime = Runtime.getRuntime();
    	String [] cmdArr = {"sh","-c", "RNAfold"};
        Process p = runtime.exec(cmdArr);
      
        BufferedReader processOutput = new BufferedReader(new InputStreamReader(p.getInputStream()));
        BufferedWriter processInput = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
        
        //String commandToSend = "RNAFold";
        String cc = "AAAAAAAAAAUUUUUUUUUUUGGGGGGGGGGGCCCCCCCCCCCCUUUUUU";
        //processInput.write(commandToSend);
        processInput.write(cc);
        processInput.flush();
        
        int lineCounter = 0;
        while(true){
        	System.out.println("pico");
        	String line = processOutput.readLine();
        	System.out.println("rico");
        	if(line == null)break;
        	System.out.println(++lineCounter + ": "+ line);
        }
        
        processInput.close();
        processOutput.close();
        p.waitFor();
        */
      
    }
}
