package com.example.sadi;

import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.util.ResourceUtils;

public class EchoServiceServlet extends SimpleSynchronousServiceServlet
{	
	public void processInput(Resource input, Resource output)
	{
		output.getModel().add(ResourceUtils.reachableClosure(input));
	}
}
