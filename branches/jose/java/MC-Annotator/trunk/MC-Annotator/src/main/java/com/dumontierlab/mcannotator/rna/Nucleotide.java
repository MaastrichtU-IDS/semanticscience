package com.dumontierlab.mcannotator.rna;

import java.net.MalformedURLException;
import java.net.URL;

public class Nucleotide {
	// A11 : G C3p_endo syn
	private String nucleotideConformation;// syn || anti
	private String chainID;// A
	private String residueLabel;// G
	private String residuePosition;// 11
	private String puckerAtom;// C3p
	private String puckerQuality;// endo
	private String pdbId;
	private URL url;

	public Nucleotide(String aPdbId, String aPos, String aChain) {
		this.setPdbId(aPdbId);
		this.setResiduePosition(aPos);
		this.setChainID(aChain);
		this.setPdbId(aPdbId);
		this.setUrl(makeNucURL(aPdbId, aChain, aPos));
	}

	public Nucleotide(String aPdbId, String aPos, String aChain, String aRes) {
		this.setPdbId(aPdbId);
		this.setChainID(aChain);
		this.setResidueLabel(aRes);
		this.setResiduePosition(aPos);
		this.setUrl(makeNucURL(aPdbId, aChain, aPos));
	}

	public Nucleotide(String aPdbId, String aPos, String aRes, String aChain,
			String aConformation) {
		this.setPdbId(aPdbId);
		this.setNucleotideConformation(aConformation);
		this.setChainID(aChain);
		this.setResidueLabel(aRes);
		this.setResiduePosition(aPos);
		this.setUrl(makeNucURL(aPdbId, aChain, aPos));
	}

	public URL makeNucURL(String pdbId, String chainId, String position){
		try {
			return new URL("http://bio2rdf.org/pdb:"+pdbId+"/chain_"+chainId+"/position_"+position);
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
		return null;
	}
	
	/**
	 * @return the url
	 */
	public URL getUrl() {
		return url;
	}

	/**
	 * @param url the url to set
	 */
	public void setUrl(URL url) {
		this.url = url;
	}

	
	/**
	 * @return the pdbId
	 */
	public String getPdbId() {
		return pdbId;
	}

	/**
	 * @param pdbId the pdbId to set
	 */
	public void setPdbId(String pdbId) {
		this.pdbId = pdbId;
	}

	public String getPuckerAtom() {
		return puckerAtom;
	}

	public void setPuckerAtom(String puckerAtom) {
		this.puckerAtom = puckerAtom;
	}

	public String getPuckerQuality() {
		return puckerQuality;
	}

	public void setPuckerQuality(String puckerQuality) {
		this.puckerQuality = puckerQuality;
	}

	public String getNucleotideConformation() {
		return nucleotideConformation;
	}

	public String getChainID() {
		return chainID;
	}

	public String getResidueLabel() {
		return residueLabel;
	}

	public String getResiduePosition() {
		return residuePosition;
	}

	public void setNucleotideConformation(String nucleotideConformation) {
		this.nucleotideConformation = nucleotideConformation;
	}

	public void setChainID(String chainID) {
		this.chainID = chainID;
	}

	public void setResidueLabel(String aResLabel) {
		this.residueLabel = aResLabel;
	}

	public void setResiduePosition(String residuePosition) {
		this.residuePosition = residuePosition;
	}

	public String toString() {
		return "Nucleotide residue: " + this.getPdbId() + " chain:"
				+ this.getChainID() + " label:" + this.getResidueLabel()
				+ " residuePos:" + this.getResiduePosition() + " PA:"
				+ this.getPuckerAtom() + " PQ:" + this.getPuckerQuality()
				+ " RC:"+this.getNucleotideConformation();
	}
}
