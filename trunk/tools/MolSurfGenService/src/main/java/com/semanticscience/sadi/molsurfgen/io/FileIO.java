package com.semanticscience.sadi.molsurfgen.io;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.ResourceFactory;
import com.semanticscience.sadi.molsurfgen.MolSurfGenService;

public class FileIO {
	
	private static final String BaseURL = "http://semanticscience.org/ontology/molecular_surface_generator.owl#";
	private static final String SioURL = "http://semanticscience.org/resource/";
	private static final String CHEBI_URL = "http://purl.obolibrary.org/obo/";
	private static final String GEO_URL = "http://semanticscience.org/ontology/";
	private static final String SO_URL = "http://purl.org/obo/owl/";
	
	private static final Log log = LogFactory.getLog(MolSurfGenService.class);
	public static final Resource chain = ResourceFactory.createResource(SioURL + "SIOBIO_000007");
	public static final Resource residue = ResourceFactory.createResource(CHEBI_URL + "CHEBI_33708");
	public static final Resource molecule = ResourceFactory.createResource(CHEBI_URL + "CHEBI_36357");
	public static final Resource pocket = ResourceFactory.createResource(SO_URL + "SO_0001105");
	public static final Resource identifier = ResourceFactory.createResource(SioURL + "SIO_000115");
	public static final Resource EP = ResourceFactory.createResource(BaseURL + "ElectrostaticPotential");
	//public static final Resource PocketDist = ResourceFactory.createResource(BaseURL + "LigandPocketDist");
	public static final Resource molStruct = ResourceFactory.createResource(BaseURL + "MolecularStructure");
	public static final Resource molStructWithModel = ResourceFactory.createResource(BaseURL + "MolecularStructureWithMSM");
	public static final Resource molecularSurfaceModel = ResourceFactory.createResource(BaseURL + "MolecularSurfaceModel");
	public static final Resource peptideLen = ResourceFactory.createResource(BaseURL + "PeptideMaxLength");
	public static final Resource SES = ResourceFactory.createResource(BaseURL + "SolventExcludedSurface");
	public static final Resource polyhedral = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000004");
	public static final Resource face = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000003");
	public static final Resource triangle = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000020");
	public static final Resource vertex = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000000");
	public static final Resource edge = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000001");
	public static final Resource normal = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000041");
	public static final Resource endPoint = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000008");
	public static final Resource startPoint = ResourceFactory.createResource(GEO_URL + "GEOMETRY_000009");
	public static final Resource xCoor = ResourceFactory.createResource(SioURL + "SIO_000400");
	public static final Resource yCoor = ResourceFactory.createResource(SioURL + "SIO_000401");
	public static final Resource zCoor = ResourceFactory.createResource(SioURL + "SIO_000402");
	
	private HashMap<String, Resource> resMap = new HashMap<String, Resource>();
	public static final Resource ala = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32441");
	public static final Resource arg = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32700");
	public static final Resource asn = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32664");
	public static final Resource asp = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32470");
	public static final Resource cys = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32460");
	public static final Resource glu = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32483");
	public static final Resource gln = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32677");
	public static final Resource gly = ResourceFactory.createResource(CHEBI_URL + "CHEBI_33708");
	public static final Resource his = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32535");
	public static final Resource ile = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32615");
	public static final Resource leu = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32630");
	public static final Resource lys = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32568");
	public static final Resource met = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32648");
	public static final Resource phe = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32503");
	public static final Resource pro = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32874");
	public static final Resource ser = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32848");
	public static final Resource thr = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32835");
	public static final Resource trp = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32732");
	public static final Resource tyr = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32789");
	public static final Resource val = ResourceFactory.createResource(CHEBI_URL + "CHEBI:32861");
	
	public static final Property hasPart = ResourceFactory.createProperty(SioURL + "SIO_000028");
	public static final Property hasProperPart = ResourceFactory.createProperty(SioURL + "SIO_000053");
	public static final Property hasUnit = ResourceFactory.createProperty(SioURL + "hasUnit");
	public static final Property isAbout = ResourceFactory.createProperty(SioURL + "SIO_000146");
	public static final Property isLocatedIn = ResourceFactory.createProperty(SioURL + "SIO_000061");
	public static final Property isLocationOf = ResourceFactory.createProperty(SioURL + "SIO_000145");
	public static final Property isPartOf = ResourceFactory.createProperty(SioURL + "SIO_000068");
	public static final Property isProperPartOf = ResourceFactory.createProperty(SioURL + "SIO_000093");
	public static final Property hasProperty = ResourceFactory.createProperty(SioURL + "SIO_000008");
	public static final Property representedBy = ResourceFactory.createProperty(SioURL + "SIO_000205");
	public static final Property hasValue = ResourceFactory.createProperty(SioURL + "SIO_000300");

	public FileIO(){
		resMap.put("ALA", ala);
		resMap.put("ARG", arg);
		resMap.put("ASN", asn);
		resMap.put("ASP", asp);
		resMap.put("CYS", cys);
		resMap.put("GLU", glu);
		resMap.put("GLN", gln);
		resMap.put("GLY", gly);
		resMap.put("HIS", his);
		resMap.put("ILE", ile);
		resMap.put("LEU", leu);
		resMap.put("LYS", lys);
		resMap.put("EMT", met);
		resMap.put("PHE", phe);
		resMap.put("PRO", pro);
		resMap.put("SER", ser);
		resMap.put("THR", thr);
		resMap.put("TRP", trp);
		resMap.put("TYR", tyr);
		resMap.put("VAL", val);
	}
	
	/**
	 * Parses the MSMG output file and adds the data to the output class.
	 * 
	 * @param fileName
	 * 		Name of the MSMG output file.
	 * @param output
	 * 		Output class to be annotated.
	 */
	public void parseAndAnnotate(String fileName, Resource output){
		
		HashMap<String, Resource> resPolyhedralMap = new HashMap<String, Resource>();
		HashMap<String, Resource> chains = new HashMap<String, Resource>();
		HashMap<String, Resource> residues = new HashMap<String, Resource>();
		HashMap<String, Resource> pockets = new HashMap<String, Resource>();
		HashMap<Integer, Resource> vertexPolyhedralMap = new HashMap<Integer, Resource>();
		HashMap<Integer, Resource> vertexMap = new HashMap<Integer, Resource>();
		BufferedReader in;
		int index = 0;
		
		try {
			in = new BufferedReader(new FileReader(fileName));
			
			Resource molSurfModel = output.getModel().createResource(molecularSurfaceModel);
			Resource polyhedralSurface = output.getModel().createResource(polyhedral);
			Resource polyatomicEntity = output.getModel().createResource(molecule);
			Resource ses = output.getModel().createResource(SES);
			
			String line = new String();
		    while ((line = in.readLine()) != null){
		    	String[] tokens = line.split("[\t]");
		    	
		    	if(tokens.length > 3){
		    		
		    		String chainID = tokens[0].trim();
		    		int id = Integer.parseInt(tokens[1].trim());
		    		String type = tokens[2].trim();
		    		float x = Float.parseFloat(tokens[3].trim());
		    		float y = Float.parseFloat(tokens[4].trim());
		    		float z = Float.parseFloat(tokens[5].trim());
		    		float nx = Float.parseFloat(tokens[6].trim());
		    		float ny = Float.parseFloat(tokens[7].trim());
		    		float nz = Float.parseFloat(tokens[8].trim());
		    		float ep = Float.parseFloat(tokens[9].trim());
		    		
		    		//Vertex vertex = new Vertex(index, new Point3d(x,y,z), new Point3d(nx,ny,nz), ep);
		    		Resource aVertex = output.getModel().createResource(vertex);
		    		Resource elecPot = output.getModel().createResource(EP);
		    		Resource aNormal = output.getModel().createResource(normal);
					Resource startpoint = output.getModel().createResource(startPoint);
					Resource endpoint = output.getModel().createResource(endPoint);
					Resource xcoor = output.getModel().createResource(xCoor);
					Resource ycoor = output.getModel().createResource(yCoor);
					Resource zcoor = output.getModel().createResource(zCoor);
					Resource xncoor = output.getModel().createResource(xCoor);
					Resource yncoor = output.getModel().createResource(yCoor);
					Resource zncoor = output.getModel().createResource(zCoor);
					
					xcoor.addLiteral(hasValue, x);
					ycoor.addLiteral(hasValue, y);
					zcoor.addLiteral(hasValue, z);
					
					xncoor.addLiteral(hasValue, x + nx);
					yncoor.addLiteral(hasValue, y + ny);
					zncoor.addLiteral(hasValue, z + nz);
					
					aVertex.addProperty(hasPart, xcoor);
					aVertex.addProperty(hasPart, ycoor);
					aVertex.addProperty(hasPart, zcoor);
		    		elecPot.addProperty(isLocatedIn, aVertex);
		    		elecPot.addLiteral(hasValue, ep);
					
					startpoint.addProperty(hasPart, xcoor);
					startpoint.addProperty(hasPart, ycoor);
					startpoint.addProperty(hasPart, zcoor);
					
					endpoint.addProperty(hasPart, xncoor);
					endpoint.addProperty(hasPart, yncoor);
					endpoint.addProperty(hasPart, zncoor);
					
					aNormal.addProperty(hasPart, startpoint);
					aNormal.addProperty(hasPart, endpoint);
					aVertex.addProperty(hasPart, aNormal);
					
					if(!chains.containsKey(chainID)){
						Resource aChain = output.getModel().createResource(chain);
						Resource aChainID = output.getModel().createResource(identifier);
						aChainID.addLiteral(hasValue, chainID);
						aChain.addProperty(hasPart, aChainID);
						
						chains.put(chainID, aChainID);
					}
		    		
		    		if(!residues.containsKey(chainID + "" + id)){
		    			
		    			Resource aResidue;
		    			
		    			if(resMap.containsKey(type)){
		    				aResidue = output.getModel().createResource(resMap.get(type));
		    			}
		    			else{
		    				aResidue = output.getModel().createResource(residue);
		    			}
		    			
		    			Resource aaSes = output.getModel().createResource(SES);
		    			Resource aaPolyhedralSurface = output.getModel().createResource(polyhedral);
		    			Resource aaResId = output.getModel().createResource(identifier);
		    			residues.put(chainID + "" + id, aResidue);
		    			
		    			aaResId.addLiteral(hasValue, id);
		    			aaSes.addProperty(representedBy, aaPolyhedralSurface);
		    			aResidue.addProperty(hasProperty, aaResId);
		    			aResidue.addProperty(hasProperPart, aaSes);
		    			chains.get(chainID).addProperty(hasProperPart, aResidue);
		    			resPolyhedralMap.put(chainID + ":" + id, aaPolyhedralSurface);
		    		}
		    		
		    		vertexPolyhedralMap.put(index, resPolyhedralMap.get(chainID + ":" + id));
		    		vertexMap.put(index, aVertex);
		    		
		    		if(!tokens[10].trim().equals("")){
		    			String ligands = tokens[10].trim();
		    			String[] ligandArray = ligands.split("[|]");
		    			
		    			for(String ligand : ligandArray){
			    			if(pockets.containsKey(ligand)){
			    				Resource pocketPolyhedralSurface = pockets.get(ligand);
			    				pocketPolyhedralSurface.addProperty(hasPart, resPolyhedralMap.get(chainID + ":" + id));
				    		}
				    		else{
				    			Resource ligandPocket = output.getModel().createResource(pocket);
				    			Resource pocketSES = output.getModel().createResource(SES);
				    			Resource pocketPolyhedralSurface = output.getModel().createResource(polyhedral);
				    			Resource ligandPocketID = output.getModel().createResource(identifier);
				    			pocketPolyhedralSurface.addProperty(hasPart, resPolyhedralMap.get(chainID + ":" + id));
				    			ligandPocketID.addLiteral(hasValue, ligand);
				    			pocketSES.addProperty(representedBy, pocketPolyhedralSurface);
				    			ligandPocket.addProperty(hasProperty, ligandPocketID);
				    			ligandPocket.addProperty(hasProperPart, pocketSES);
				    			pockets.put(ligand, pocketPolyhedralSurface);
				    		}
		    			}
		    		}
		    	}
		    	else{
		    		int id1 = Integer.parseInt(tokens[0].trim());
		    		int id2 = Integer.parseInt(tokens[1].trim());
		    		int id3 = Integer.parseInt(tokens[2].trim());
		    		
		    		Resource polygonFace = output.getModel().createResource(face);
					Resource aTriangle = output.getModel().createResource(triangle);
					Resource edge1 = output.getModel().createResource(edge);
					Resource edge2 = output.getModel().createResource(edge);
					Resource edge3 = output.getModel().createResource(edge);
					
					edge1.addProperty(isPartOf, aTriangle);
					edge1.addProperty(hasPart, vertexMap.get(id1));
					edge1.addProperty(hasPart, vertexMap.get(id2));
					edge2.addProperty(isPartOf, aTriangle);
					edge2.addProperty(hasPart, vertexMap.get(id2));
					edge2.addProperty(hasPart, vertexMap.get(id3));
					edge3.addProperty(isPartOf, aTriangle);
					edge3.addProperty(hasPart, vertexMap.get(id3));
					edge3.addProperty(hasPart, vertexMap.get(id1));
					
					polygonFace.addProperty(isPartOf, aTriangle);
					if(!vertexPolyhedralMap.get(id1).getModel().contains(polygonFace, hasPart)){
						vertexPolyhedralMap.get(id1).addProperty(hasPart, polygonFace);
					}
					if(!vertexPolyhedralMap.get(id1).getModel().contains(polygonFace, hasPart)){
						vertexPolyhedralMap.get(id2).addProperty(hasPart, polygonFace);
					}
					if(!vertexPolyhedralMap.get(id1).getModel().contains(polygonFace, hasPart)){
						vertexPolyhedralMap.get(id3).addProperty(hasPart, polygonFace);
					}
		    	}
		    	index++;
		    }
		    
		    ses.addProperty(representedBy, polyhedralSurface);
			polyatomicEntity.addProperty(hasProperPart, ses);
			molSurfModel.addProperty(hasPart, polyhedralSurface);
			molSurfModel.addProperty(isAbout, polyatomicEntity);
			output.addProperty(hasPart, molSurfModel);
			
			/*resPolyhedralMap = null;
			residues = null;
			pockets = null;
			vertexPolyhedralMap = null;
			vertexMap = null;*/
		    
		    in.close();
		    File file = new File(fileName);
		    file.delete();
		} catch (FileNotFoundException e) {
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	    
	}
}
