package com.dumontierlab.rsync_parser;

import java.io.File;
import java.io.IOException;

public class RunRsync {
	
	
	static String rsyncLocation = "/usr/bin/rsync";
	static String parameters = "-rtpl -v -z -n --delete --port=334444";
	static String sourceURI = "rsync.wwpdb.org::ftp_data/structures/divided/XML/";
	String destinationFolder;
	String filename;
	File logFile;
	
	public RunRsync() {
		this.destinationFolder = "/tmp/";
		this.filename = "pdbXML.log";
		this.logFile = new File(destinationFolder+filename);
	}
	
	public RunRsync(String destinationFolder, String filename){
		this.logFile = new File(destinationFolder+filename);
	}
	
	public RunRsync(File aLogFile){
		this.logFile = aLogFile;
		
		try {
			String[] cmdArr = {getRsyncLocation(), getParameters(),getSourceURI(),getDestinationFolder()};
			Process p = Runtime.getRuntime().exec(cmdArr);
			p.waitFor();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			System.out.println("ca222caca");
			e.printStackTrace();
			System.exit(-1);
		} catch(InterruptedException e){
			System.out.println("cacaca");
			System.exit(-1);
		}
	}



	/**
	 * @return the filename
	 */
	public String getFilename() {
		return filename;
	}



	/**
	 * @param filename the filename to set
	 */
	public void setFilename(String filename) {
		this.filename = filename;
	}



	/**
	 * @return the logFile
	 */
	public File getLogFile() {
		return logFile;
	}



	/**
	 * @param logFile the logFile to set
	 */
	public void setLogFile(File logFile) {
		this.logFile = logFile;
	}



	/**
	 * @return the destinationFolder
	 */
	public String getDestinationFolder() {
		return destinationFolder;
	}

	/**
	 * @param destinationFolder the destinationFolder to set
	 */
	public void setDestinationFolder(String destinationFolder) {
		this.destinationFolder = destinationFolder;
	}

	/**
	 * @return the rsyncLocation
	 */
	public static String getRsyncLocation() {
		return rsyncLocation;
	}

	/**
	 * @param rsyncLocation the rsyncLocation to set
	 */
	public static void setRsyncLocation(String rsyncLocation) {
		RunRsync.rsyncLocation = rsyncLocation;
	}

	/**
	 * @return the parameters
	 */
	public static String getParameters() {
		return parameters;
	}

	/**
	 * @param parameters the parameters to set
	 */
	public static void setParameters(String parameters) {
		RunRsync.parameters = parameters;
	}

	/**
	 * @return the sourceURI
	 */
	public static String getSourceURI() {
		return sourceURI;
	}

	/**
	 * @param sourceURI the sourceURI to set
	 */
	public static void setSourceURI(String sourceURI) {
		RunRsync.sourceURI = sourceURI;
	}
	
	
	
}
