package com.dumontierlab.DbConnector;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.util.ArrayList;
import java.util.Iterator;

public class DbConnectionTester {
	public static void main(String args[])throws Exception{
		
		DbConnection db = new DbConnection("jdbc:mysql://localhost/directed_studies","root", "Negro7h!");
		
		ResultSet rs = db.executeQuery("SELECT * FROM input_acc");

		int numOfCols = rs.getMetaData().getColumnCount();
		while(rs.next()){
			for(int i=1;i<=numOfCols;i++){
				System.out.print(rs.getObject(i)+"\t");
			}
			System.out.println();
		}
		//INSERT INTO test VALUE(?)
		PreparedStatement ps = db.getConnect().prepareStatement("UPDATE test SET a=? WHERE a=11");
		ps.setInt(1, 21);
		ps.executeUpdate();
	}
	
	
}
