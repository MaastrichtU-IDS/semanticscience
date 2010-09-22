package com.dumontierlab.rsync_parser;

import java.util.ArrayList;
import java.util.List;

import com.sun.syndication.feed.synd.SyndContent;
import com.sun.syndication.feed.synd.SyndContentImpl;
import com.sun.syndication.feed.synd.SyndEntry;
import com.sun.syndication.feed.synd.SyndEntryImpl;
import com.sun.syndication.feed.synd.SyndFeed;
import com.sun.syndication.feed.synd.SyndFeedImpl;

public class RSSTester {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		SyndFeed feed = new SyndFeedImpl();
		feed.setFeedType("feedType");
		feed.setTitle("aTitle");
		feed.setLink("http://google.ca");
		feed.setDescription("hello 123");
		
		 List entries = new ArrayList();
	     SyndEntry entry;
	     SyndContent description;

	     entry = new SyndEntryImpl();
	     entry.setTitle("ROME v1.0");
	     entry.setLink("http://wiki.java.net/bin/view/Javawsxml/Rome01");
	     description = new SyndContentImpl();
	     description.setType("text/plain");
	     description.setValue("Initial release of ROME");
	     entry.setDescription(description);
	     entries.add(entry);
	    
	     
	     entry = new SyndEntryImpl();
	     entry.setTitle("ROME v3.0");
	     entry.setLink("http://wiki.java.net/bin/view/Javawsxml/Rome03");
	     description = new SyndContentImpl();
	     description.setType("text/html");
	     description.setValue("<p>More Bug fixes, mor API changes, some new features and some Unit testing</p>"+
	                          "<p>For details check the <a href=\"http://wiki.java.net/bin/view/Javawsxml/RomeChangesLog#RomeV03\">Changes Log</a></p>");
	     entry.setDescription(description);
	     entries.add(entry);
	     
	     feed.setEntries(entries);
	     
	}

}
