package com.dumontierlab.mcannotator.rna;

import java.util.LinkedList;

public class Edge {
	/**
	 * The edge label
	 */
	private String edgeLabel;
	/**
	 * Linked List with all subEdges
	 */
	LinkedList<SubEdge> subEdges;
	/**
	 *  Residue Label
	 */
	private String residueLabel;
	
	/**
	 * Default constructor
	 */
	public Edge(){
		this.setEdgeLabel("-1");
		this.subEdges = new LinkedList<SubEdge>();
	}
	
	public Edge(String eLabel, String residueLabel){
		this.subEdges = new LinkedList<SubEdge>();
		this.setEdgeLabel(eLabel);
		this.setResidueLabel(residueLabel);
		this.setSubEdges(inferSubEdges(eLabel));
	}
	
	public Edge(String eLabel, String residueLabel, String[] subEdgeArr){
		this(eLabel, residueLabel);
		String edgeLabel = inferEdgeLabel(subEdgeArr);
		if(edgeLabel != eLabel){
			System.out.println("Edge inferencing error!");
			System.exit(1);
		}//if	
	}//Edge
	
	/**
	 * This method infers the Edge to which the SubEdges in subEdgeArr correspond to. (NAR 2002) 
	 * @param subEdgeArr
	 * @return A string of the infered Edge
	 */
	private String inferEdgeLabel(String[] subEdgeArr) {
		// First deal with the sub edge descriptions in NAR2002 figure 8 LW+
		for(int i=0;i<subEdgeArr.length;i++){
			String aSE = subEdgeArr[i];
			/*
			if(aSE.equals("G-C Ww/Ww trans") || aSE.equals("C-G Ww/Ww trans")){
				
			}else if(aSE.equals("A-U Ww/Ww trans") || aSE.equals("U-A Ww/Ww trans")){
				
			}else if(aSE.equals("G-U Ww/Ww trans") || aSE.equals("U-G Ww/Ww trans")){
				
			}else if(aSE.equals("A-C Hh/Ww trans") || aSE.equals("C-A Ww/Hh trans")){
				
			}else if(aSE.equals("A-U Hh/Ww trans") || aSE.equals("U-A Ww/Hh trans")){
				
			}else if(aSE.equals("G-C Hh/Hh trans") || aSE.equals("C-G Hh/Hh trans")){

			}else if(aSE.equals("A-U Ss/Ws trans") || aSE.equals("U-A Ws/Ss trans")){
				
			}else if(aSE.equals("G-U Ww/Bs trans") || aSE.equals("U-G Bs/Ww trans")){
				
			}else if(aSE.equals("A-U Ww/Ww trans") || aSE.equals("U-A Ww/Ww trans")){
				
			}
			*/
		}
		return null;
	}

	/**
	 * This method infers Sub Edge correspondence for each LW Edge
	 * @See http://semanticscience.org/projects/rkb/
	 * @param eLabel an LW edge label [W, H or S]
	 * @return A linked list containing the sub edges for this edge. Returns null if error occurs.
	 */
	private LinkedList<SubEdge> inferSubEdges(String eLabel) {
		if(eLabel.toUpperCase().trim().equals("W")){
			if(this.getResidueLabel().equals("A")){
				this.subEdges.add(new SubEdge("Wh"));
				this.subEdges.add(new SubEdge("Ww"));
			}
			else if(this.getResidueLabel().equals("G")){
				this.subEdges.add(new SubEdge("Wh"));
				this.subEdges.add(new SubEdge("Ww"));
				this.subEdges.add(new SubEdge("Ws"));
			}
			else if(this.getResidueLabel().equals("U")){
				this.subEdges.add(new SubEdge("Wh"));
				this.subEdges.add(new SubEdge("Ww"));
				this.subEdges.add(new SubEdge("Ws"));
			}
			else if(this.getResidueLabel().equals("C")){
				this.subEdges.add(new SubEdge("Wh"));
				this.subEdges.add(new SubEdge("Ww"));
				this.subEdges.add(new SubEdge("Ws"));
			}
		}//if Watson
		else if(eLabel.toUpperCase().trim().equals("H")){
			if(this.getResidueLabel().equals("A")){
				this.subEdges.add(new SubEdge("C8"));
				this.subEdges.add(new SubEdge("Hh"));
				this.subEdges.add(new SubEdge("Hw"));
				this.subEdges.add(new SubEdge("Bh"));
			}
			else if(this.getResidueLabel().equals("G")){
				this.subEdges.add(new SubEdge("C8"));
				this.subEdges.add(new SubEdge("Hh"));
				this.subEdges.add(new SubEdge("Hw"));
				this.subEdges.add(new SubEdge("Bh"));
			}
			else if(this.getResidueLabel().equals("U")){
				this.subEdges.add(new SubEdge("Hh"));
				this.subEdges.add(new SubEdge("Hw"));
				this.subEdges.add(new SubEdge("Bh"));
			}
			else if(this.getResidueLabel().equals("C")){
				this.subEdges.add(new SubEdge("Hh"));
				this.subEdges.add(new SubEdge("Hw"));
				this.subEdges.add(new SubEdge("Bh"));	
			}
		}//elseif Hoogsteen
		else if(eLabel.toUpperCase().trim().equals("S")){
			if(this.getResidueLabel().equals("A")){
				this.subEdges.add(new SubEdge("Bs"));
				this.subEdges.add(new SubEdge("Ss"));
				this.subEdges.add(new SubEdge("O2"));
			}
			else if(this.getResidueLabel().equals("G")){
				this.subEdges.add(new SubEdge("Bs"));
				this.subEdges.add(new SubEdge("Sw"));
				this.subEdges.add(new SubEdge("Ss"));
				this.subEdges.add(new SubEdge("O2"));
			}
			else if(this.getResidueLabel().equals("U")){
				this.subEdges.add(new SubEdge("Bs"));
				this.subEdges.add(new SubEdge("Sw"));
				this.subEdges.add(new SubEdge("O2"));
			}
			else if(this.getResidueLabel().equals("C")){
				this.subEdges.add(new SubEdge("Bs"));
				this.subEdges.add(new SubEdge("Sw"));
				this.subEdges.add(new SubEdge("O2"));
			}
		}//elseif Sugar
		return getSubEdges();
	}
	
	/* Getters and Setters*/
	public String getEdgeLabel() {
		return edgeLabel;
	}
	public void setEdgeLabel(String edgeLabel) {
		this.edgeLabel = edgeLabel;
	}
	public LinkedList<SubEdge> getSubEdges() {
		return subEdges;
	}
	public void setSubEdges(LinkedList<SubEdge> subEdges) {
		this.subEdges = subEdges;
	}

		
	public String getResidueLabel() {
		return residueLabel;
	}
	public void setResidueLabel(String residueLabel) {
		this.residueLabel = residueLabel;
	}

	
	
	
	
}
