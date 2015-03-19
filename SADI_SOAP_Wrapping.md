# Introduction #
Here we present a step by step guide for creating a Java SADI service that wraps an existing [ChEBI](http://www.ebi.ac.uk/chebi/) [SOAP service](http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl) for getting the charge of a molecule. This guide extends [Building a SADI service in Java](http://sadiframework.org/content/getting-involved/building-a-sadi-service-in-java/) and [this](http://code.google.com/p/semanticscience/wiki/SettingUpSADIServiceStepByStep) tutorial. Currently this service is available at [this](http://134.117.108.117:8080/sadi-soap-wrapper/) url.

# Create an OWL document describing your Input and Output #
The input and outputs of all SADI services must be described in a  dereferenceable OWL ontology document. For this example we will be using the following input and output classes:
Note that we are using Machester syntax and labels to render resources.

Input class description:
```
'ChEBI Entity' that 'has attribute' some 'ChEBI Identifier'
```
Where:
```
'ChEBI identifier' that  'has value' some Literal
```

**Note**: We use only valid ChEBI identifiers as the associated value of the 'ChEBI identifier' class, e.g.: "CHEBI:29977"

Output class description:
```
'ChEBI Entity' that 'has attribute' some Charge
```

Where:
```
Charge 'has value' some Literal
```

**Note**: The literal associated with the Charge attribute will have as value the value returned from the SOAP service call.

The resulting OWL document has been made available [here](http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl)

# Generate the SADI service code #
After creating a Maven project modify the pom.xml file and make sure that the following nodes are included
```
<packaging>war</packaging>
```

```
<build>
  <finalName>sadi-service-example</finalName>
  <plugins>
    <plugin>
       <groupId>org.apache.maven.plugins</groupId>
       <artifactId>maven-war-plugin</artifactId>
       <configuration>
         <webResources>
           <resource>
             <directory>${build.sourceDirectory}</directory>
             <targetPath>sources</targetPath>
           </resource>
         </webResources>
       </configuration>
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <configuration>
        <source>1.6</source>
        <target>1.6</target>
      </configuration>
    </plugin>
    <plugin>
      <groupId>org.mortbay.jetty</groupId>
      <artifactId>maven-jetty-plugin</artifactId>
      <version>6.1.24</version>
      <configuration>
        <contextPath>/sadi-services</contextPath>
      </configuration>
    </plugin>
    <plugin>
      <groupId>ca.wilkinsonlab.sadi</groupId>
      <artifactId>sadi-generator</artifactId>
      <version>0.1.0-SNAPSHOT</version>
    </plugin>
    <plugin>
      <groupId>ca.wilkinsonlab.sadi</groupId>
      <artifactId>sadi-tester</artifactId>
      <version>0.1.0-SNAPSHOT</version>
    </plugin>
  </plugins>
</build>
```


```
<pluginRepositories>
  <pluginRepository>
    <id>dev.biordf.net</id>
    <name>dev.biordf.net</name>
    <url>http://dev.biordf.net/maven</url>
  </pluginRepository>
</pluginRepositories>
<repositories>
  <repository>
    <id>dev.biordf.net</id>
    <name>dev.biordf.net</name>
    <url>http://dev.biordf.net/maven</url>
  </repository>
</repositories>
<dependencies>
  <dependency>
    <groupId>ca.wilkinsonlab.sadi</groupId>
    <artifactId>sadi-service</artifactId>
    <version>0.1.0-SNAPSHOT</version>
  </dependency>
</dependencies>
```

## Run the SADI service generator Maven plugin ##
**If you are using Eclipse** you can download the runtime maven configuration file from [here](http://sadi-data.semanticscience.org/setup/runconfigs.zip). Create a directory inside of your Maven project and extract to it the contents of the zip file. Now you can go to Run->Run configurations and from the left panel select "generate sadi service" under the Maven Build menu and change the serviceName, serviceClass, inputClass, outputClass and contact email.
We strongly recommend that you also add the serviceDescription parameter to your run configuration and provide a complete human readable description of what this service does. i.e.:


```
This SADI service wraps the SOAP service ChebiWebServiceService located  at
http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl. It calls the 
operation getChebiAsciiName. This service takes as an input an 
instance of the class 
http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030 
a ChEBI Entity that has attribute some ChEBI Identifier.
It returns as an output an instance of the class 
http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034, 
a ChEBI entity and has attribute some Charge. 
http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/input.rdf  
contains an example of an input and 
http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/output.rdf 
contains the corresponding output.
```

Once ready click on RUN.

**If you are not using Eclipse** you can go to the location of your project on your file system (where your pom.xml file is located) and run the following command
```
$ mvn ca.wilkinsonlab.sadi:sadi-generator:generate-service 
  -DserviceName=sadi-sercice-example 
  -DserviceClass=com.example.HelloWorldService 
  -DinputClass=http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030  -DoutputClass=http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034 
  -DcontactEmail=your-email-address
  -DserviceDescription=This service takes as an input a 
```

The service generator plugin should now have created a Java stub under src/main/java

## Add CXF as a dependency to your project ##
Add the following dependencies to your POM file:
```
<dependencies>
...
  <dependency>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-rt-frontend-jaxws</artifactId>
    <version>2.3.1</version>
  </dependency>
  <dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>1.6.1</version>
  </dependency>
  <dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-log4j12</artifactId>
    <version>1.6.1</version>
  </dependency>
  <dependency>
    <groupId>org.apache.cxf</groupId>
    <artifactId>cxf-rt-transports-http</artifactId>
    <version>2.3.1</version>
  </dependency>
...
</dependencies>

```

Recall that for this example we will be making use of http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl as the WSDL file that will be consumed by CXF.

Now add the following plugins to the build configuration in your POM file:

```
<build>
  <plugins>
   ...
    <plugin>
      <groupId>org.apache.cxf</groupId>
      <artifactId>cxf-codegen-plugin</artifactId>
      <version>2.3.1</version>
      <executions>
        <execution>
          <id>generate-sources</id>
          <phase>generate-sources</phase>
          <configuration>
            <sourceRoot>${basedir}/src/main/java</sourceRoot>
            <wsdlOptions>
              <wsdlOption>
                <wsdl>http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl</wsdl>
                <extraargs>
                  <extraarg>-client</extraarg>
                </extraargs>
                <bindingFiles>
                  <bindingFile>http://sadi-data.semanticscience.org/setup/bindings.xml</bindingFile>
                </bindingFiles>
              </wsdlOption>
            </wsdlOptions>
          </configuration>
          <goals>
            <goal>wsdl2java</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
    <!-- Add generated sources - avoids having to copy generated sources to build location -->
    <plugin>
      <groupId>org.codehaus.mojo</groupId>
      <artifactId>build-helper-maven-plugin</artifactId>
      <version>1.5</version>
      <executions>
        <execution>
          <id>add-source</id>
          <phase>generate-sources</phase>
          <goals>
            <goal>add-source</goal>
          </goals>
          <configuration>
            <sources>
              <source>${basedir}/target/generated/src/main/java</source>
            </sources>
          </configuration>
        </execution>
      </executions>
    </plugin>
    <plugin>
      <artifactId>maven-assembly-plugin</artifactId>
      <configuration>
        <descriptorRefs>
          <descriptorRef>jar-with-dependencies</descriptorRef>
        </descriptorRefs>
      </configuration>
    </plugin>
  ...
  </plugins>
</build>

```

The only items of interest in the POM are:
  * We depend on the CXF v2.3.1 client libraries
  * We invoke the cxf-codegen-plugin to run wsdl2java to generate our Java stub code into ${basedir}/target/generated/src/main/java
  * We use the build-helper-maven-plugin so that Maven can compile from two source directories. Thus allowing us to compile what is in ${basedir}/src/main and ${basedir}/target/generated/src/main/java
  * We use the maven-assembly-plugin to create a final JAR containing all necessary dependencies when we perform a mvn assembly:assembly
  * We use a binding file to avoid the usage of [JAXBElements](http://download.oracle.com/javase/6/docs/api/javax/xml/bind/JAXBElement.html) -> http://sadi-data.semanticscience.org/setup/bindings.xml


## Assemble the Java code ##
In order to execute the wsdl2java function from CXF you now need to run:
```
mvn assembly:assembly
```
from the command line in your project's directory. This will create the Java code from the WSDL file and thus let us communicate with the SOAP web service directly from java.


## Make the SOAP call within the SADI service ##

Open src /main/java/org/semanticscience/sadi/soapwrapper/chebisoap/GetCharge.java and you should have the following code
```
package org.semanticscience.sadi.soapwrapper.chebisoap;

import org.apache.log4j.Logger;

import ca.wilkinsonlab.sadi.service.annotations.Name; 
import ca.wilkinsonlab.sadi.service.annotations.Description; 
import ca.wilkinsonlab.sadi.service.annotations.ContactEmail; 
import ca.wilkinsonlab.sadi.service.annotations.InputClass; 
import ca.wilkinsonlab.sadi.service.annotations.OutputClass; 
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Model; 
import com.hp.hpl.jena.rdf.model.ModelFactory; 
import com.hp.hpl.jena.rdf.model.Property; 
import com.hp.hpl.jena.rdf.model.Resource; 

@Name("ChebiSoapGetCharge")
@Description("This SADI service wraps the SOAP service ChebiWebServiceService located  at http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl. 
It calls the operation getChebiAsciiName. This service takes as an input an instance of the class 
http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030 
a ChEBI Entity that has attribute some ChEBI Identifier. It returns as an output
 an instance of the class http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034, 
a ChEBI entity and has attribute some Charge. 
http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/input.rdf  contains an example of
 an input and http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/output.rdf contains 
the corresponding output.")
@ContactEmail("josemiguelcruztoledo@gmail.com")
@InputClass("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030")
@OutputClass("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034")
public class GetCharge extends SimpleSynchronousServiceServlet {
	private static final Logger log = Logger.getLogger(GetCharge.class);
	private static final long serialVersionUID = 1L;

	public void processInput(Resource input, Resource output) {
		/* your code goes here 
                 * (add properties to output node based on properties of input node…) 
                 */ 
	}

	@SuppressWarnings("unused")
	private static final class Vocab {
		private static Model m_model = ModelFactory.createDefaultModel();

		public static final Property chebi_soap_00052 = m_model
				.createProperty("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00052");
		public static final Property chebi_soap_00051 = m_model
				.createProperty("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00051");
		public static final Resource chebi_soap_00009 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00009");
		public static final Resource chebi_soap_00030 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030");
		public static final Resource chebi_soap_00034 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034");
		public static final Resource Literal = m_model
				.createResource("http://www.w3.org/2000/01/rdf-schema#Literal");
		public static final Resource chebi_soap_00013 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00013");
	}
}

```

At this stage you should also have the uk.ac.webservices.chebi package as a sibling of the package generated by the SADI service generator, which in this case is org.semanticscience.sadi.soapwrapper.chebisoap. Now we are ready to include add the code required to make the SOAP service call into the stub:


```
package org.semanticscience.sadi.soapwrapper.chebisoap;

import java.net.MalformedURLException;
import java.net.URL;

import org.apache.log4j.Logger;
import org.semanticscience.sadi.soapwrapper.chebisoap.helper.ChebiSoapHelper;

import uk.ac.ebi.webservices.chebi.ChebiWebServiceFault_Exception;
import uk.ac.ebi.webservices.chebi.ChebiWebServicePortType;
import uk.ac.ebi.webservices.chebi.ChebiWebServiceService;
import uk.ac.ebi.webservices.chebi.Entity;
import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.Description;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

/**
 * @author "Jose Cruz-Toledo"
 * ChebiSoapGetCharge
 */
@Name("ChebiSoapGetCharge")
@Description("This SADI service wraps the SOAP service ChebiWebServiceService located  at http://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl.
 It calls the operation getChebiAsciiName. This service takes as an input an instance of the class 
http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030 a ChEBI Entity that has
 attribute some ChEBI Identifier. It returns as an output an instance of the class 
http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034, a ChEBI entity and has attribute some Charge. 
http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/input.rdf  contains an example of an input and 
http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/output.rdf contains the corresponding output.")
@ContactEmail("josemiguelcruztoledo@gmail.com")
@InputClass("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030")
@OutputClass("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034")
public class GetCharge extends SimpleSynchronousServiceServlet {
	private static final Logger log = Logger.getLogger(GetCharge.class);
	private static final long serialVersionUID = 1L;

	public void processInput(Resource input, Resource output) {
		// get a model from the resource
		Model inputModel = input.getModel();
		Model outputModel = output.getModel();
		// get a chebi soap helper object
		ChebiSoapHelper csh = new ChebiSoapHelper();
		// Get the value of the CHEBI id that is coming in
		String chebiId = csh.getChebiId(input,
				Vocab.chebi_soap_00051.toString(),
				Vocab.chebi_soap_00052.toString());
		String charge = "";
		// Do SOAP
		// Check the ChebiId
		if (csh.checkChebiId(chebiId)) {
			// Find the class generated by CXF that extends Service
			ChebiWebServiceService service = new ChebiWebServiceService();
			// Find the get method that uses the Service classes' getPort method
			ChebiWebServicePortType port = service.getChebiWebServicePort();
			try {
				Entity en = port.getCompleteEntity(chebiId);
				charge = en.getCharge();
				// create attribute resource
				String base = csh.getBaseURL(new URL(input.getURI()));
				Resource attrInstance = outputModel.createResource(base
						+ csh.getPositiveRandomNumber());
				// type the attribute instance
				attrInstance.addProperty(ChebiSoapHelper.Vocabulary.rdftype,
						Vocab.chebi_soap_00013);
				// add the value to the attributed instance
				attrInstance.addProperty(Vocab.chebi_soap_00052, charge);
				// connect the output with the attributed instance
				output.addProperty(Vocab.chebi_soap_00051, attrInstance);
			} catch (ChebiWebServiceFault_Exception e) {
				e.printStackTrace();
			} catch (MalformedURLException e) {
				e.printStackTrace();
			}
		}
	}

	@SuppressWarnings("unused")
	private static final class Vocab {
		private static Model m_model = ModelFactory.createDefaultModel();

		public static final Property chebi_soap_00052 = m_model
				.createProperty("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00052");
		public static final Property chebi_soap_00051 = m_model
				.createProperty("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00051");
		public static final Resource chebi_soap_00009 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00009");
		public static final Resource chebi_soap_00030 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030");
		public static final Resource chebi_soap_00034 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00034");
		public static final Resource Literal = m_model
				.createResource("http://www.w3.org/2000/01/rdf-schema#Literal");
		public static final Resource chebi_soap_00013 = m_model
				.createResource("http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00013");
	}
}

```

Things to note about this wrapper code:
  * For simplicity of presentation I make use of a ChebiSoapHelper class that holds various helper methods to help with the generation of the SOAP call
  * For any SOAP service that you will wrap using CXF you will need to identify the following class and method generated by CXF's wsdl2java
    1. The class that extends the Service class:
```
ChebiWebServiceService service = new ChebiWebServiceService();
```
    1. The get method that uses the Service classes' getPort method:
```
ChebiWebServicePortType port = service.getChebiWebServicePort();
```

## Create the WAR file and deploy it ##
By now you should be ready to create a deployable servlet. To do so, from a command line simply:

```
mvn clean install
```

This command will generate in the target directory of your project amongst other things a WAR file. This file should be ready to deploy on any servlet container of your choice.

# Testing your deployed service #

An easy way of invoking your newly created SADI service is to use cURL. From a command line simply type:

```
curl --header "Content-type: text/rdf+xml" --data @input.rdf http://134.117.108.117:8080/sadi-soap-wrapper/ChebiGetCharge >output.rdf
```
**Note**:
  1. The input RDF that is being used is available at http://sadi-data.semanticscience.org/ChebiGetChargeSadiWrapper/input.rdf
```
<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:base="http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" >
<rdf:Description rdf:about="http://example.org/anInput">
	<rdf:type rdf:resource="http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00030"/>
	<base:chebi_soap_00051 rdf:resource="http://example.org/anInputAttribute"/>
</rdf:Description>
<rdf:Description rdf:about="http://example.org/anInputAttribute">
	<rdf:type rdf:resource="http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#chebi_soap_00009"/>
	<base:chebi_soap_00052 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">CHEBI:29977</base:chebi_soap_00052>
</rdf:Description>
</rdf:RDF>
```
  1. Your output document should look exactly like this:
```
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:j.0="http://sadi-ontology.semanticscience.org/chebi-sadi-soap.owl#">
  <j.0:chebi_soap_00034 rdf:about="http://example.org/anInput">
    <j.0:chebi_soap_00051>
      <j.0:chebi_soap_00013 rdf:about="http://example.org/141267108">
        <j.0:chebi_soap_00052>-1</j.0:chebi_soap_00052>
      </j.0:chebi_soap_00013>
    </j.0:chebi_soap_00051>
  </j.0:chebi_soap_00034>
</rdf:RDF>

```
# External Links #
  * [What is a SADI Service?](http://sadiframework.org/content/getting-involved/what-is-a-sadi-service/)
  * [Building a SADI service in Java](http://sadiframework.org/content/getting-involved/building-a-sadi-service-in-java/)
  * [The SADI service Registry](http://sadiframework.org/registry/services/)
  * [Register your SADI services](http://sadiframework.org/registry/register/)
  * [CXF SOAP client using Maven](http://nileshk.com/2009/05/20/cxf-soap-client-using-maven.html)