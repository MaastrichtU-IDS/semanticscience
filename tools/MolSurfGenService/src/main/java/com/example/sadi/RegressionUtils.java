package com.example.sadi;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.commons.math.stat.regression.SimpleRegression;
import org.joda.time.DateTime;
import org.joda.time.Interval;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.ISODateTimeFormat;

import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.ResourceFactory;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.vocabulary.RDF;

public class RegressionUtils
{
	private static final Log log = LogFactory.getLog(RegressionUtils.class);


	public static final Resource PairedValue = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#PairedValue");
	public static final Resource DatedValue = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#DatedValue");
	public static final Property element = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#element");
	public static final Property x = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#x");
	public static final Property y = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#y");
	public static final Property date = ResourceFactory.createProperty("http://purl.org/dc/elements/1.1/date");
	public static final Property value = ResourceFactory.createProperty("http://www.w3.org/1999/02/22-rdf-syntax-ns#value");
	public static final Resource LinearRegressionModel = ResourceFactory.createResource("http://sadiframework.org/examples/regression.owl#LinearRegressionModel");
	public static final Property hasRegressionModel = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#hasRegressionModel");
	public static final Property slope = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#slope");
	public static final Property intercept = ResourceFactory.createProperty("http://sadiframework.org/examples/regression.owl#intercept");
	
	private static List<PairedValue> getNormalizedData(StmtIterator statements)
	{
		List<PairedValue> pairedValues = new ArrayList<PairedValue>();
		List<DatedValue> datedValues = new ArrayList<DatedValue>();
		while (statements.hasNext()) {
			Statement statement = statements.nextStatement();
			Resource pair = statement.getResource();
			log.trace(pair.listProperties().toList().toString());
			if (pair.hasProperty(RDF.type, PairedValue)) {
				pairedValues.add(new PairedValue(pair.getProperty(x).getDouble(), pair.getProperty(y).getDouble()));
			} else if (pair.hasProperty(RDF.type, DatedValue)) {
				datedValues.add(new DatedValue(pair.getProperty(date).getString(), pair.getProperty(value).getDouble()));
			}
		}
		
		DateTime minDate = null;
		for (DatedValue datedValue: datedValues) {
			if (minDate == null || datedValue.date.isBefore(minDate))
				minDate = datedValue.date;
		}
		for (DatedValue datedValue: datedValues) {
			Interval interval = new Interval(minDate, datedValue.date);
			int day = interval.toDuration().toStandardSeconds().toStandardDays().getDays();
			pairedValues.add(new PairedValue(day, datedValue.value));
		}
		return pairedValues;
	}
	
	public static void processInput(Resource input, Resource output)
	{
		log.debug("processing input " + input);
		SimpleRegression regressionModel = new SimpleRegression();
		for (PairedValue pairedValue: getNormalizedData(input.listProperties(element))) {
			regressionModel.addData(pairedValue.x, pairedValue.y);
		}
		
		double m = regressionModel.getSlope();
		double b = regressionModel.getIntercept();
		Resource linearRegressionModel = output.getModel().createResource(LinearRegressionModel);
		linearRegressionModel.addLiteral(slope, m);
		linearRegressionModel.addLiteral(intercept, b);
		output.addProperty(hasRegressionModel, linearRegressionModel);
	}
	
	private static class PairedValue
	{
		public double x;
		public double y;
		
		public PairedValue(double x, double y)
		{
			this.x = x;
			this.y = y; 
		}
	}
	
	private static class DatedValue
	{
		private static DateTimeFormatter fmt = ISODateTimeFormat.date();
		
		public DateTime date;
		public double value;
		
		public DatedValue(String date, double value)
		{
			this.date = fmt.parseDateTime(date);
			this.value = value;
		}
	}
}
