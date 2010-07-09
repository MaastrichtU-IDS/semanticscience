package com.dumontierlab.mcannotator.bin;

import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.dumontierlab.mcannotator.rna.BasePair;
import com.dumontierlab.mcannotator.rna.Nucleotide;
import com.dumontierlab.mcannotator.rna.Stack;
import com.dumontierlab.mcannotator.vocabulary.McaOwlVocabulary;
import com.dumontierlab.mcannotator.vocabulary.Owl2Vocabulary;
import com.dumontierlab.mcannotator.vocabulary.PdbOwlVocabulary;
import com.dumontierlab.mcannotator.vocabulary.RnaoOwlVocabulary;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class RDFizeMCAnnotate {
	public String pdbId = "nil";
	public int modelNumber = 1;
	private Model rdfModel;
	private ParseMCAnnotate parsedMCA;
	private String rdfVersion;
	private LinkedList<BasePair> basePairs;
	private LinkedList<Nucleotide> nucleotides;
	private LinkedList<Stack> stacks;
	
	

	public RDFizeMCAnnotate(ParseMCAnnotate pM){
		this(pM, "", 0);
	}
	
	public RDFizeMCAnnotate(ParseMCAnnotate pM, String rdfVersion){
		this(pM, "", 0);
		this.setRdfVersion(rdfVersion);
		this.setRdfModel(ModelFactory.createDefaultModel()); 
		
		/*
		 * Here handle the RDFizer that is requested
		 */
		if(rdfVersion.equals("fr3d")){
			rdfizeForFR3D(pM);
		}else if(rdfVersion.equals("rnao")){
			//rdfizeForRnao(pM);
		}else if(rdfVersion.equals("rkb")){
			//rdfizeForRKB(pM);
		}
	}
		
	public RDFizeMCAnnotate(ParseMCAnnotate pM, String aPdbId, int aModelNum){
		this.setRdfModel(ModelFactory.createDefaultModel());
		
		if(aPdbId.equals("")){
			this.setPdbId(pM.getPdbId());
		}
		else{
			this.setPdbId(aPdbId);
		}
		
		if(aModelNum < 1){
			this.setModelNumber(pM.getModelNumber());
		}
		else{
			this.setModelNumber(aModelNum);
		}		
	}
	
	private void rdfizeForFR3D(ParseMCAnnotate pM) {
		basePairs = pM.getBasePairs();//subedges + anti| syn for each nucleotide
		nucleotides = pM.getNucleotides();
		
		//nucleotides first :)
		for (Nucleotide aNuc : nucleotides){
			addNucleotideResourceFr3d(aNuc);
		}
		//now the base pairs :-)
		for(BasePair aBp : basePairs){
			addBasePairResourceFr3d(aBp);
		}//for
		
	}//rdfizeForFr3d
	
	
	private void addBasePairResourceFr3d(BasePair aBp) {
		/*
		 * This mehtod will add to the RDFmodel the
		 * information about:
		 * 1) the base pairing relation
		 * 2) owl:axiom annotation of 1)
		 */
		Nucleotide nuc1 = aBp.getFirstNucleotide();
		Resource nuc1Res = this.getNucleotideResidueFr3d(nuc1);
		Nucleotide nuc2 = aBp.getSecondNucleotide();
		Resource nuc2Res = this.getNucleotideResidueFr3d(nuc2);
		String[] subEdgeArr = aBp.getSubEdgeArr();
		for(int i=0;i<subEdgeArr.length;i++){
			if(subEdgeArr.length == 1){
				//System.out.println(subEdgeArr[i]);
				//get pairsWithProperty and its Inverse
				Property pairsWith = getPairsWithPropertySimple(subEdgeArr[i], aBp.getStrandBPOrientation());
				Property pairsWithInv = RnaoOwlVocabulary.rnaoBasePairRelations.get(pairsWith);
				
				/* now make the following statements:
				 *  nuc1 pairsWith nuc2
				 *  nuc2 pairsWithInv nuc1
				 */
				getRdfModel().add(nuc1Res, pairsWith, nuc2Res);
				getRdfModel().add(nuc2Res, pairsWithInv, nuc1Res);
				
				this.annotatePredicate(pairsWith, nuc1Res, nuc2Res);
				this.annotatePredicate(pairsWithInv, nuc1Res, nuc2Res);
				
			}else if(subEdgeArr.length > 1){
				//do something painful
			}
		}
		//System.out.println(aBp.get);
		
	}

	private void annotatePredicate(Property pairsWith, Resource nuc1Res,
			Resource nuc2Res) {
		/*
		 * This method will create the owl axiom annotation for 
		 * the pairsWith relation
		 */
		String ns =  "http://bio2rdf.org/application:mcannotate";
		Resource program = this.getRdfModel().createResource(ns);
		Resource pdbModel = this.getRdfModel().createResource(
				PdbOwlVocabulary.PDB_NS+this.getPdbId()+"/model_"
				+this.getModelNumber());
		Resource axiom = this.getRdfModel().createResource();
		this.getRdfModel().add(axiom, 
				Owl2Vocabulary.ObjectProperty.annotatedProperty.property(), pairsWith);
		this.getRdfModel().add(axiom,
				Owl2Vocabulary.ObjectProperty.annotatedSource.property(), nuc1Res);
		this.getRdfModel().add(axiom,
				Owl2Vocabulary.ObjectProperty.annotatedTarget.property(), nuc2Res);
		this.getRdfModel().add(axiom, McaOwlVocabulary.ObjectProperty.generatedBy.property(), program);
		this.getRdfModel().add(axiom, McaOwlVocabulary.ObjectProperty.hasSource.property(), pdbModel);
		
	}

	private Property getPairsWithPropertySimple(String subEdge,
			String sBPO) {
		/*
		 * This method converts the subEdge-strandBPOrient
		 * into one of the corresponding pairsWith relations
		 * sBPO -> strand base pair orientation
		 */
		
		Pattern wwPattern = Pattern.compile("(W\\w/W\\w)");
		Pattern whPattern = Pattern.compile("(W\\w/H\\w)|(H\\w/W\\w)|()");
		Pattern wsPattern = Pattern.compile("(W\\w/S\\w)|(S\\w/W\\w)|(O2.*/)");
		Pattern hhPatern = Pattern.compile("(H\\w/H\\w)");
		Pattern hsPattern = Pattern.compile("(H\\w/S\\w)|(S\\w/H\\s)");
		Matcher wwM = wwPattern.matcher(subEdge.trim());
		Matcher whM = whPattern.matcher(subEdge.trim());
		Matcher wsM = wsPattern.matcher(subEdge.trim());
		Matcher hhM = hhPatern.matcher(subEdge.trim());
		Matcher hsM = hsPattern.matcher(subEdge.trim());
		
		
		if(wwM.matches()){
			//System.out.println(wwM.group(0)+" "+wwM.group(1));
		}
		//
		if(whM.matches()){
		//	System.out.println(whM.group(1)+" "+ whM.group(2));
		}
		if(wsM.matches()){
		//	System.out.println(wsM.group(1)+" "+wsM.group(2));
		}
		if(hhM.matches()){
			//System.out.println(hhM.group(1));
		}
		if(hsM.matches()){
			System.out.println(hsM.group(1)+" "+hsM.group(2));
		}
		
		//family 1
		if((subEdge.equals("Ww/Ww")
			|| subEdge.equals("Ww/Ws")
			|| subEdge.equals ("Ww/Wh")) && sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCWW.property();
		}
		else if((subEdge.equals("Ww/Ww")
				|| subEdge.equals("Ws/Ww")) && sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCWW.property();
		}
		
		//family 2
		else if(subEdge.equals("Ww/Ww") && sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTWW.property();
		}
		
		//family 3
		else if((subEdge.equals("Bh/Ww") 
				|| subEdge.equals("Hh/Ww"))
				&& sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCHW.property();
		}
		else if((subEdge.equals("Ww/Bh") 
				|| subEdge.equals("Ww/Hh"))
				&& sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCWH.property();
		}
		
		//family 4
		else if((subEdge.equals("Ww/Hh") 
				|| subEdge.equals("Ww/Bh"))
				&& sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTWH.property();
		}
		else if((subEdge.equals("Hh/Ww") 
				|| subEdge.equals("Bh/Ww"))
				&& sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTHW.property();
		}
		
		//family 5
		else if((subEdge.equals("Ss/Ww") 
				|| subEdge.equals("Bs/Ww"))
				&& sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCSW.property();
		}
		else if((subEdge.equals("Ww/Ss") 
				|| subEdge.equals("Ww/Bs"))
				&& sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCWS.property();
		}
		
		//family 6
		else if((subEdge.equals("Ss/Ww") 
				|| subEdge.equals("Bs/Ww")
				|| subEdge.equals("Ss/Ws"))
				&& sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTSW.property();
		}
		else if((subEdge.equals("Ww/Ss") 
				|| subEdge.equals("Ww/Bs")
				|| subEdge.equals("Ws/Ss"))
				&& sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTWS.property();
		}
		
		//family 7
		else if(subEdge.equals("Hh/Hh") && sBPO.equals("cis")){
			//highly unlikely edge interaction
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCHH.property();
		}
		
		//family 8
		else if(subEdge.equals("Hh/Hh") && sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTHH.property();
		}
	
		//family 9
		else if(subEdge.equals("Hh/Bs") && sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCHS.property();
		}
		else if(subEdge.equals("Bs/Hh") && sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCSH.property();
		}
		
		//family 10
		else if(subEdge.equals("Hh/Ss") && sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTHS.property();
		}
		else if(subEdge.equals("Ss/Hh") && sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTSH.property();
		}
		
		//family 11
		else if(subEdge.equals("Ss/Ss") && sBPO.equals("cis")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithCSS.property();
		}
		
		//family 12
		else if(subEdge.equals("Ss/Ss") && sBPO.equals("trans")){
			return RnaoOwlVocabulary.ObjectProperty.pairsWithTSS.property();
		}
		
		else{
			System.out.println("Could not find a pairs_with relation for:");
			System.out.println(subEdge+"  "+sBPO);
		}
		
		
		return null;
	}

	private void addNucleotideResourceFr3d(Nucleotide aNuc) {
		/*
		 * This method will add to the RDFmodel the information 
		 * about:
		 * 1) nucleotide conformation (anti|syn)
		 * 2) the nucleobase's rnao type
		 * 3) the part-hood relation to the pdb chemical component
		 */
		
		//First: we create the resource for the nucleotide conformation(nC)
		Resource nC = getNucleotideConformationFr3d(aNuc);
		//Second: we create the resource for the nucleotide residue(nR)
		Resource nR = getNucleotideResidueFr3d(aNuc);
		//Third: we establish the parthood relation with PDB (pdbCc) 
		Resource pdbCc = getPdbChemicalComponent(aNuc);
		
		/*
		 * now we connect assert the relation between 
		 * the nucleotide conformation and its
		 * corresponding residue		
		 */
		getRdfModel().add(nR, RnaoOwlVocabulary.ObjectProperty.hasQuality.property(),nC);
		/*
		 * Finally, we assert the parthood relation to 
		 * the pdb chemical component
		 */
		getRdfModel().add(nR, RnaoOwlVocabulary.ObjectProperty.partOf.property(), pdbCc);
		getRdfModel().add(pdbCc, RnaoOwlVocabulary.ObjectProperty.hasPart.property(), nR);
	}

	private Resource getPdbChemicalComponent(Nucleotide aNuc) {
		/*
		 * This method will return a resource for the corresponding
		 * chemical component in PDB for aNuc
		 */
		Resource chemicalComponent = getRdfModel().createResource(
					McaOwlVocabulary.PDB_NS+aNuc.getPdbId()
					+"/chemicalComponent_"+aNuc.getChainID()
					+aNuc.getResiduePosition());
		
		return chemicalComponent;
	}

	private Resource getNucleotideResidueFr3d(Nucleotide aNuc) {
		/*
		 * This method makes a resource for the nucleotide
		 * that describes the residue and has its
		 * corresponding label and adds it to the Model
		 */
		//label
		String residueLabel = "nucleotide residue "
			+ aNuc.getResidueLabel() +" chain-position"
			+ aNuc.getChainID()+"-"+aNuc.getResiduePosition()
			+" found in model: "+getModelNumber()+ " of PDB: "
			+getPdbId();
		//resource
		Resource residue = getRdfModel().createResource(McaOwlVocabulary.MCA_NS
				+getPdbId()+"_m"+getModelNumber()+"_c"+aNuc.getChainID()
				+"_r"+aNuc.getResiduePosition());
		//put the label for this resource
		getRdfModel().add(residue, RDFS.label, residueLabel);
		//type the resource
		getRdfModel().add(residue, RDF.type, lookupResidueResource(aNuc.getResidueLabel()));
		return residue;
	}

	private Resource getNucleotideConformationFr3d(Nucleotide aNuc) {
		/*
		 * This method makes a resource for the nucleotide
		 * that describes the residue conformation and has its
		 * corresponding label and adds it to the Model
		 */
		if(aNuc != null){
			//label
			String conformerLabel = "base conformation: "
				+ aNuc.getNucleotideConformation()+" on residue: "
				+ aNuc.getResidueLabel() +" from chain-position: "
				+ aNuc.getChainID()+"-"+aNuc.getResiduePosition()
				+ " from model:"+ this.getModelNumber() +" of PDB "+ this.getPdbId();
			//resource
			Resource nucleotideConformation = getRdfModel()
					.createResource(McaOwlVocabulary.MCA_NS + getPdbId()
							+"/"+ aNuc.getNucleotideConformation()+"_m"
							+ getModelNumber()+ "_c"+aNuc.getChainID()
							+ "_r"+aNuc.getResiduePosition());
			
			//put the label for this resource
			getRdfModel().add(nucleotideConformation, RDFS.label, conformerLabel);
			//type the resource
			getRdfModel().add(nucleotideConformation, RDF.type,
					this.lookupNucleotideConformationQuality(aNuc.getNucleotideConformation()));
			return nucleotideConformation;
		}
		return null;
	}

	private Resource lookupNucleotideConformationQuality(String aNucConfor){
		/*
		 * This method will return a resource to the corresponding 
		 * anti or syn quality according to RNAO
		 */
		if(aNucConfor != null){
			if(aNucConfor.equals("syn")){
				return RnaoOwlVocabulary.Class.SynNucleosideConformation.resource();
			}else if(aNucConfor.equals("anti")){
				return RnaoOwlVocabulary.Class.AntiNucleosideConformation.resource();
			}
		}
		return null;
	}
	public LinkedList<BasePair> getBasePairs() {
		return basePairs;
	}

	public void setBasePairs(LinkedList<BasePair> basePairs) {
		this.basePairs = basePairs;
	}

	public LinkedList<Nucleotide> getNucleotides() {
		return nucleotides;
	}

	public void setNucleotides(LinkedList<Nucleotide> nucleotides) {
		this.nucleotides = nucleotides;
	}

	public LinkedList<Stack> getStacks() {
		return stacks;
	}

	public void setStacks(LinkedList<Stack> stacks) {
		this.stacks = stacks;
	}
	
	public String getRdfVersion() {
		return rdfVersion;
	}

	public void setRdfVersion(String rdfVersion) {
		this.rdfVersion = rdfVersion;
	}
	
	public String getPdbId() {
		return pdbId;
	}

	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public int getModelNumber() {
		return modelNumber;
	}

	public void setModelNumber(int modelNumber) {
		this.modelNumber = modelNumber;
	}

	public Model getRdfModel() {
		return rdfModel;
	}

	public void setRdfModel(Model rdfModel) {
		this.rdfModel = rdfModel;
	}

	public ParseMCAnnotate getParsedMCA() {
		return parsedMCA;
	}

	public void setParsedMCA(ParseMCAnnotate parsedMCA) {
		this.parsedMCA = parsedMCA;
	}
	
	
	
	private Resource lookupResidueResource(String aRes) {
		String prefix = RnaoOwlVocabulary.RNAO_NS;
		if (aRes.equalsIgnoreCase("C")) {
			return this.getRdfModel().createResource(prefix + "0000025");
		} else if (aRes.equalsIgnoreCase("G")) {
			return this.getRdfModel().createResource(prefix + "0000028");
		} else if (aRes.equalsIgnoreCase("U")) {
			return this.getRdfModel().createResource(prefix + "0000026");
		} else if (aRes.equalsIgnoreCase("A")) {
			return this.getRdfModel().createResource(prefix + "0000027");
		}
		return null;
	}

}
