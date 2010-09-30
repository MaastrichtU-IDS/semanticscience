package com.dumontierlab.mcannotator.bin;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;
/**
 * This class executes MC Annotate :)
 * @author Jose Cruz-Toledo
 *
 */

public class RunMCAnnotate {
	/**
     * The directory specified by the user where all PDB entries are located.
     */
    private File inputDirectory;
    /**
     * The directory specified by the user where all raw MC-Annotate data and RDF files will be located.
     */
    private File outputDirectory;
    /**
     * The directory where all raw MC-Annotate data will be located.
     */
    private File mcaRawOutputDirectory;
    /**
     * The directory where all RDF files will be written.
     */
    private File rdfMCAOutputDirectory;
        

	/**
     * Constructor used to create this object.  Input directory is specified by the user; output 
     * directory will automatically be assigned to the /tmp/ directory of the user.
     * @param inputDirectory The directory where all PDB entries are stored.
     * @see #runRunMCAnnotate(File, File)
     * @see #inputDirectory
     */
	public RunMCAnnotate(File inputDirectory){
		this(inputDirectory, new File("/tmp"));
	}
    /**
     * Constructor used to create this object.  No directories are specified by the user; output and input
     * directories will automatically be assigned to the /tmp/ directory of the user.
     * @see #runRunMCAnnotate(File, File)
     */
    public RunMCAnnotate(){
    	this(new File("/tmp"), new File("/tmp"));	
    }
	
	/**
	 * Execute MCAnnotate on a specified input directory and store results in output directory
	 * @param inputDir the input directory
	 * @param outputDir the output directory
	 */
	public RunMCAnnotate(File inputDir, File outputDir){
		if(inputDir == null){
			System.out.println("User did not provide input directory.");
			System.exit(-1);
		}
		
		if(outputDir == null){
			System.out.println("User did not provide output directory.");
			System.exit(-1);
		}
		
		try {
			//Check if MC-Annotate is in the PATH
			Process p = Runtime.getRuntime().exec("MC-Annotate");
			p.waitFor();
		} catch (IOException ioe) {
			ioe.printStackTrace();
			System.out.println("Error executing MC-Annotate!\nMake sure that MC-Annotate is in your path.");
			System.exit(-1);
		}catch(InterruptedException ie){
			System.out.println("MC-Annotate was interrupted.");
			System.exit(-1);
		}
		
		this.setInputDirectory(inputDir);
		this.setOutputDirectory(outputDir);
		
		
	}//RunMCAnnotate
	/**
     * Returns the input directory
     * @return <code>File</file> object of the input directory.
     * @see #inputDirectory
     */
	public File getInputDirectory() {	return inputDirectory;}
	/**
     * Returns the output directory
     * @return <code>File</file> object of the output directory.
     * @see #outputDirectory
     */
	public File getOutputDirectory() { return outputDirectory;}
	/**
     * Returns the RDF output directory
     * @return <code>File</file> object of the RDF output directory.
     * @see #rdfMCAOutputDirectory
     */
	public File getRdfMcaOutputDirectory() { return rdfMCAOutputDirectory; }
	
	/**
     * Returns a list of all the PDB files in the input directory
     * @return <code>File</file> object array of all the PDB files.
     * @see #inputDirectory
     */
	public File[] getInputPaths(){ return (this.inputDirectory).listFiles();}
	
	/**
	 * This method returns the String that is outputted by some Process aProc
	 * @param aProc
	 * @return
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
     * Counts the number of models that are present in a given PDB file. 
     * @param file The PDB file.
     * @return The number of models that were found in the PDB file. Returns 0 if no models
     * were found; -1 if the file does not have a pdb, gz or ent extension.
     */
	public int getNumberOfModels(File file) {
		String pattern = "^MODEL\\s+\\d+";
		Pattern myPattern = Pattern.compile(pattern);
		int modelCount = 0;
		int flag = 1;
		try {
			BufferedReader br = null;
			String extension = file.getName().substring(file.getName().lastIndexOf('.')+1);

			if (extension.equals("gz")) {
				br = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(file))));
			} else if (extension.equals("pdb") || extension.equals("ent")) {
				br = new BufferedReader(new FileReader(file));
			} else{	flag = -1;}

			if (flag == 1) {
				String aLine;
				modelCount = 0;
				while ((aLine = br.readLine()) != null) {
					Matcher m = myPattern.matcher(aLine);
					if (m.find()) {
						modelCount++;
					}
				}
			}
			
			br.close();
		} catch (FileNotFoundException e) {
			System.out.println("Could not find file " + file);

		} catch (IOException e) {
			System.out.println("Could not read file " + file);
		}
		return modelCount;
	}
	/**
     * Sets the input directory.
     * @param directory The directory where all PDB entries are stored.
     * @see #inputDirectory
     */
	public void setInputDirectory(File directory){ 
		try{
			inputDirectory = directory;
			if ((inputDirectory == null) || (!inputDirectory.exists())){
				System.out.println("Input directory does not exist.");
				System.exit(-1);
			}
			else{
				inputDirectory = directory;
			}
			
		}catch(NullPointerException ne){
			System.out.println("Directory was not specified.");
		}catch(SecurityException se){
			System.out.println("Directory "+directory.getPath()+" or its subdirectories could not be created.");
		}
	}
	/**
	 * Sets the output directory, MC-Annotate raw data output directory and the RDF output directory.
	 * @param directory The output directory
	 * @see #outputDirectory
	 * @see #mcaOutputDirectory
	 * @see #rdfMCAOutputDirectory
	 */
	public void setOutputDirectory(File directory){ 
		try{
			outputDirectory = directory;
			
			if ((outputDirectory != null) && (!outputDirectory.exists())){
				outputDirectory.mkdirs();
			}
			this.mcaRawOutputDirectory = new File(outputDirectory + "/mca_raw");
			this.mcaRawOutputDirectory.mkdir();
			rdfMCAOutputDirectory = new File(outputDirectory + "/rdf");
			rdfMCAOutputDirectory.mkdir();
		}catch(NullPointerException ne){
			System.out.println("Directory was not specified.");
		}catch(SecurityException se){
			System.out.println("Directory "+directory.getPath()+" or its subdirectories could not be created.");
		}

	}
	/**
	 * Deletes a file or if the <code>File</code> object is a directory, all files and directories 
	 * (including the directory itself) will be deleted.
	 * @param file The file to be deleted.
	 * @return <code>Boolean</code> to determine if the deletion was successful.
	 * @see #deleteDirectory(File)
	 */
	public boolean deleteFile(File file){
		
		if( !file.exists() ) {
			return false;
		}
		
		if (file.isDirectory()){
			return deleteDirectory(file);
		}
		else if (file.isFile()){
			return file.delete();
		}
		
		return false;
	}
	/**
	 * Deletes all files and directories (including the directory) in a directory. 
	 * @param directory The directory where all the files will be deleted.
	 * @return <code>Boolean</code> to determine if the deletion was successful.
	 */
	public boolean deleteDirectory(File directory) {
		
		if(directory.exists()) {
			File[] files = directory.listFiles();
			
			for(int i=0; i<files.length; i++) {
				if(files[i].isDirectory()) {
					deleteDirectory(files[i]);
				}
				else {
					files[i].delete();
				}
			}
		}
		return directory.delete() ;
	}
	
	/**
	 * This method runs MCAnnotate
	 * @return
	 * @throws IOException
	 */
	public LinkedList<File> run(){
		File[] files = null;
		if(this.getInputDirectory().isFile()){
			files = new File[1];
			files[0] = this.getInputDirectory().getAbsoluteFile();
		}else{		
			files = this.getInputPaths();
		}
		
		LinkedList<File> outputFiles = new LinkedList<File>();
		for(int i=0; i<files.length; i++){
			File file = files[i];
			int numOfModels = this.getNumberOfModels(file);
			String pdbId = this.getPDBFromFile(file);
			//X-Ray only has one model
			if(numOfModels==0){
				//file = this.copyGZipFile(file);
				try{
					System.out.println("Running MCArunnnotate on "+pdbId+"...");
					String[] cmdArr = {"MC-Annotate", file.getPath()};
					Process p = Runtime.getRuntime().exec(cmdArr);
					p.waitFor();
					String mcaOutput = RunMCAnnotate.writeProcessOutput(p);
					try{
						String outputPath = this.getOutputDirectory()+"/mca_raw/"+pdbId+"_M_1.out";
						FileWriter fs = new FileWriter(outputPath);
						BufferedWriter out = new BufferedWriter(fs);
						out.write(mcaOutput);
						out.close();
						File outputFile = new File(outputPath);
						if(outputFile.exists()){
							outputFiles.add(outputFile);
						}
					}catch(Exception e){
						System.err.println("Error: " + e.getMessage());
						System.exit(-1);
					}
				}catch(IOException e){
					System.out.println("Error executing MC-Annotate!\nMake sure that MC-Annotate is in your path.");
					System.exit(-1);
				}catch(InterruptedException ie){
					System.out.println("MC-Annotate was interrupted.");
				}
			}
			//NMR ensembles
			else{
				//file = this.copyGZipFile(file);
				int j=0;
				for(int l=0;l<this.getNumberOfModels(file);l++){
					try{
						System.out.println("Running MCAnnotate on"+pdbId+" model "+j+"...");
						String[] cmdArr = {"MC-Annotate", "-f", Integer.toString(j), file.getPath()};
						Process p = Runtime.getRuntime().exec(cmdArr);
						p.waitFor();
						String mcaOutput = RunMCAnnotate.writeProcessOutput(p);
						try{
							String outputPath = this.getOutputDirectory()+"/mca_raw/"+pdbId+"_M_"+j+".out";
							FileWriter fs = new FileWriter(outputPath);
							BufferedWriter out = new BufferedWriter(fs);
							out.write(mcaOutput);
							out.close();
							File outputFile = new File(outputPath);
							if(outputFile.exists()){
								outputFiles.add(outputFile);
							}
						}catch(Exception e){
							System.err.println("Error: " + e.getMessage());
							System.exit(-1);
						}						
					}catch(IOException e){
						System.out.println("Error executing MC-Annotate!\nMake sure that MC-Annotate is in your path.");
						System.exit(-1);
					}catch(InterruptedException ie){
						System.out.println("MC-Annotate was interrupted.");
					}
					j++;
					
				}//for
			}//else
		}//for
		System.out.println("Done running MC-Annotate");
		return outputFiles;
	}
	/**
     * Returns the PDB four-character alphanumeric identifier using the filename
     * @return PDB identifier
     */
    public String getPDBFromFile(File file) {
		String filename = file.getName();
		if(filename.toLowerCase().startsWith("pdb")){
			filename = filename.substring(3);
		}
		return filename.substring(0, 4).toUpperCase();
	}
    
    public File copyGZipFile(File file){
		String extension = file.getName().substring(file.getName().lastIndexOf('.')+1);

		if (!extension.equals("gz"))
			return null;
		
		try{
			GZIPInputStream gzipInputStream = new GZIPInputStream(new FileInputStream(file));
			File outFile = new File(this.getOutputDirectory()+"/"+file.getName().replace(".gz", ""));
			OutputStream outStream = new FileOutputStream(outFile);
					
	    	byte[] buf = new byte[1024];
	    	int len;
	    	while ((len = gzipInputStream.read(buf)) > 0){
	    		outStream.write(buf, 0, len);
	    	}
	 
	    	gzipInputStream.close();
	    	outStream.close();
	    	return outFile;
		}
	    catch (IOException e) {
			System.err.println(e.getMessage());
			System.exit(-1);
		}
    	return file;
	}
	
}// class
