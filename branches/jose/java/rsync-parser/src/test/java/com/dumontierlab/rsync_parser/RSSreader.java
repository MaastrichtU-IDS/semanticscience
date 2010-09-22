package com.dumontierlab.rsync_parser;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

import com.sun.syndication.feed.synd.SyndFeed;
import com.sun.syndication.io.FeedException;
import com.sun.syndication.io.SyndFeedInput;
import com.sun.syndication.io.XmlReader;

public class RSSreader {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		boolean ok = false;
		if(args.length == 1){
			try {
				URL feedUrl = new URL(args[0]);
				SyndFeedInput input = new SyndFeedInput();
				SyndFeed feed = input.build(new XmlReader(feedUrl));
				System.out.println(feed);
				ok = true;
				
			} catch (MalformedURLException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IllegalArgumentException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (FeedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
		}
		if(!ok){
			System.out.println();
            System.out.println("FeedReader reads and prints any RSS/Atom feed type.");
            System.out.println("The first parameter must be the URL of the feed to read.");
            System.out.println();
		}

	}

}
