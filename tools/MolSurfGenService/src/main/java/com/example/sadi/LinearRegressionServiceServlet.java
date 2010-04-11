package com.example.sadi;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Resource;


public class LinearRegressionServiceServlet extends SimpleSynchronousServiceServlet
{

	private static final Log log = LogFactory.getLog(LinearRegressionServiceServlet.class);
	
	public LinearRegressionServiceServlet()
	{
		super();
	}
	
	public void processInput(Resource input, Resource output)
	{
		RegressionUtils.processInput(input, output);
	}
}
