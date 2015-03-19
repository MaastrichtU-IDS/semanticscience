# Requirements #

You will need the following components.
1. Eclipse IDE for Java developers
2. Java JDK
3. Sadi service skeleton
4. Curl (not necessary, but useful for quick testing with Jetty)

# Setting Up the Environment #

Install the Java JDK and extract the Eclipse IDE.
Within the Eclipse configurations file, eclipse.ini, you will need to add the path to the JDK, so you will need to add the following.
```
-vm
-path/to/the/jdk/jdkexecutable.exe
```

For windows, the jdkexecutable.exe will be javaw.exe within the bin folder of the JDK installation.

Further, you will need the Maven plugin installed for Eclipse. Within Eclipse, go to Help>Install New Software...  Within the dialogue that appears, you will need to specify the repository with which to work. As of June 2010, the repository has been at http://m2eclipse.sonatype.org/sites/m2e . Follow the wizard and complete the installation; it might take a few minutes.

Now, you will need to add the configuration file for Maven. If you are working in Windows, the configuration file is placed into the C:\Users\Username\.m2 folder, and is called settings.xml. The following contents should work.

```
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                      http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <localRepository/>
  <interactiveMode/>
  <usePluginRegistry/>
  <offline/>
  <pluginGroups>
    <pluginGroup>org.mortbay.jetty</pluginGroup>
  </pluginGroups>
  <servers/>
  <mirrors/>
  <proxies/>
  <profiles/>
  <activeProfiles/>
</settings>
```

Now, you should be ready to actually start with the creation of the SADI service from the skeleton.

# Creating a Sample Service #

In order to create the service, you will first need to download and extract the sadi-service-skeleton file provided on the SADI framework website. Next, within the Eclipse IDE, you will need to File>Import... the project and follow the dialogue to General>Import Existing Project from the root directory of the SADI service skeleton you have just extracted. If you are in the correct directory, the project should appear in the list.

Next, we would need to generate the SADI service code. To do this, you need to go to Run>Run Configurations... and select "generate sadi service" from the Maven build menu. The fields should be now filled out with the necessary information. You will need to indicate the Service Name, Service Class, Input and Output Classes. These should be ideally taken from an ontology somewhere.

# Class Creation Considerations #

The Input and Output classes defined such that they necessarily have to have the properties that you wish to operate upon. The service class should also be coming from an ontology such that reasoning over it would be enabled.

# Sample Code #

The following code will annotate a chemical entity that has a particular SMILES string with the string "Always Seven" as its hBondDonorCount property.

```

    String namespaceuri = "http://semanticscience.org/projects/sces/stuff#";
    String hasSMILES = "hasSMILES";
    String hbondcount = "hBondDonorCount";
    Property smilesproperty = ResourceFactory.createProperty(namespaceuri, hasSMILES);
    String smilesstring = input.getProperty(smilesproperty).getString();
    Property hbondcountproperty = ResourceFactory.createProperty(namespaceuri, hbondcount);
    output.getModel().add(ResourceUtils.reachableClosure(input));
    String thevalueofthis = "Always Seven";
    output.addProperty(hbondcountproperty, thevalueofthis);

```

Try to add this code and go to Run>Run Configurations... and select "run sadi services in jetty". This will, ideally, create and locally host the service as a Jetty service on your local machine, most likely at localhost:8080 . The service should be accessible at localhost:8080/servicename , unless you specified it otherwise.

# Submitting Input #

Here is some sample input to try submitting, a resource maka that has a SMILES string attached to it.

```
<rdf:RDF xmlns="http://semanticscience.org/projects/sces/stuff#"
    xmlns:log="http://www.w3.org/2000/10/swap/log#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:ss="http://semanticscience.org/projects/sces/stuff#">

    <owl:Thing rdf:about="http://semanticscience.org/projects/sces/stuff#maka">
        <hasSMILES>CCCCO</hasSMILES>
    </owl:Thing>
</rdf:RDF>
```

You will need to download and extract curl. For Windows, try searching for curl-7.20.0-ssl-sspi-zlib-static-bin-w32 . Without further setup, place the input.rdf file as indicated above, into the folder where curl.exe is located. You can now post the input.rdf to the service running in Jetty now wit the following command.

```
curl -d @input.rdf localhost:8080/yoursevicename
```

The actual service that actually computes the number of hydrogen bond donors for a molecule that has a SMILES string provided, can be reached with the input provided above using the following command.

```
curl -d @input.rdf http://cbrass.biordf.net/hbonddonorcount/hbondcounter
```

# Congratulations #

Congratulations, you service is now complete.

# P.S. Distributing Service as War #

In order to distribute the service as a WAR from within the Eclipse IDE, you can right-click on the pom.xml file in the workspace panel, and Run As...>Maven Package . This will create the WAR in the target directory of your project. You can then use this WAR to distribute the service with Tomcat.

# P.P.S. Issues With Maven #

Sometimes, certain packages may not be available, sometimes due to repository maintenance/downtime, so re-trying at a later time may solve build errors due to missing packages. If the problem persists, you will need to follow the instructions provided in the integrated console within the IDE. Ultimately, you may try to edit the pom.xml file appropriately to address this problem. If you cannot resolve the issue, it is recommended that you contact the SADI framework team.