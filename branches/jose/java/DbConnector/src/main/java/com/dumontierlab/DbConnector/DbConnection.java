package com.dumontierlab.DbConnector;
//checkout http://www.vogella.de/articles/MySQLJava/article.html#jdbc
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Date;



public class DbConnection {
	private Connection connection = null;
	private Statement statement = null;
	private PreparedStatement preparedStatement = null;
	private ResultSet resultSet = null;
	private static final String DRIVER = "com.mysql.jdbc.Driver";
	private static final String DB_URL = "jdbc:mysql://localhost/";
	private static final String username = "";
	private static final String password = "";
	
	public DbConnection(){
		// This will load the MySQL driver, each DB has its own driver
		try {
			Class.forName(DRIVER);
			connection = DriverManager.getConnection(DB_URL, username, password);
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	public DbConnection(String dbURL, String user, String passwd){
		
		try {
			Class.forName(DRIVER);
			this.connection = DriverManager.getConnection(dbURL, user, passwd);
		} catch (SQLException e1) {
			e1.printStackTrace();
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		}
	}
	
/*	public void readDataBase() throws Exception {
		try {
			// This will load the MySQL driver, each DB has its own driver
			Class.forName(DRIVER);
			// Setup the connection with the DB
			connection = DriverManager
					.getConnection(DB_URL, "root", "Negro7h!");

			// Statements allow to issue SQL queries to the database
			statement = connection.createStatement();
			// Result set get the result of the SQL query
			resultSet = statement
					.executeQuery("select * from input_acc");
			
			ResultSetMetaData md = resultSet.getMetaData();
			int numOfCols = md.getColumnCount();
			while(resultSet.next()){
				for(int i=1;i<=numOfCols;i++){
					System.out.print(resultSet.getObject(i)+"\t");
				}System.exit(1);
			}
			//writeResultSet(resultSet);

			// PreparedStatements can use variables and are more efficient
			preparedStatement = connection
					.prepareStatement("insert into  FEEDBACK.COMMENTS values (default, ?, ?, ?, ? , ?, ?)");
			// "myuser, webpage, datum, summery, COMMENTS from FEEDBACK.COMMENTS");
			// Parameters start with 1
			preparedStatement.setString(1, "Test");
			preparedStatement.setString(2, "TestEmail");
			preparedStatement.setString(3, "TestWebpage");
		//	preparedStatement.setDate(4, new Date());
			preparedStatement.setString(5, "TestSummary");
			preparedStatement.setString(6, "TestComment");
			preparedStatement.executeUpdate();

			preparedStatement = connection
					.prepareStatement("SELECT myuser, webpage, datum, summery, COMMENTS from FEEDBACK.COMMENTS");
			resultSet = preparedStatement.executeQuery();
			writeResultSet(resultSet);

			// Remove again the insert comment
			preparedStatement = connection
			.prepareStatement("delete from FEEDBACK.COMMENTS where myuser= ? ; ");
			preparedStatement.setString(1, "Test");
			preparedStatement.executeUpdate();
			
			resultSet = statement
			.executeQuery("select * from FEEDBACK.COMMENTS");
			writeMetaData(resultSet);
			
		
			
		} catch (Exception e) {
			throw e;
		} finally {
			close();
		}

	}
*/
	public ResultSet executeQuery(String aQry) {
		ResultSet returnMe = null;
		Statement st = null;
		// Statements allow to issue SQL queries to the database
		try {
			st = this.getConnect().createStatement();
			// Result set get the result of the SQL query
			returnMe = st.executeQuery(aQry);
		} catch (SQLException e) {
			e.printStackTrace();
		}
		
		return returnMe;
	}
	
	/**
	 * This method returns the column names for a result set
	 * @param resultSet
	 * @return
	 * @throws SQLException
	 */
	public ArrayList<String> getColumnNames(ResultSet resultSet) {
		// 	Now get some metadata from the database
		// Result set get the result of the SQL query
		ArrayList<String> returnMe = new ArrayList<String>();
		
		try {
			for  (int i = 1; i<= resultSet.getMetaData().getColumnCount(); i++){
				returnMe.add(resultSet.getMetaData().getColumnClassName(i));
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return returnMe;
	}
	

	private void writeResultSet(ResultSet resultSet) throws SQLException {
		// ResultSet is initially before the first data set
		while (resultSet.next()) {
			// It is possible to get the columns via name
			// also possible to get the columns via the column number
			// which starts at 1
			// e.g. resultSet.getSTring(2);
			String user = resultSet.getString("myuser");
			String website = resultSet.getString("webpage");
			String summery = resultSet.getString("summery");
			Date date = resultSet.getDate("datum");
			String comment = resultSet.getString("comments");
			System.out.println("User: " + user);
			System.out.println("Website: " + website);
			System.out.println("Summery: " + summery);
			System.out.println("Date: " + date);
			System.out.println("Comment: " + comment);
		}
	}

	// You need to close the resultSet
	private void close() {
		try {
			if (resultSet != null) {
				resultSet.close();
			}

			if (statement != null) {
				statement.close();
			}

			if (connection != null) {
				connection.close();
			}
		} catch (Exception e) {

		}
	}
	/**
	 * @return the connection
	 */
	public Connection getConnect() {
		return connection;
	}
	/**
	 * @param connection the connection to set
	 */
	public void setConnect(Connection connect) {
		this.connection = connect;
	}
	/**
	 * @return the statement
	 */
	public Statement getStatement() {
		return statement;
	}
	/**
	 * @param statement the statement to set
	 */
	public void setStatement(Statement statement) {
		this.statement = statement;
	}
	/**
	 * @return the resultSet
	 */
	public ResultSet getResultSet() {
		return resultSet;
	}
	/**
	 * @param resultSet the resultSet to set
	 */
	public void setResultSet(ResultSet resultSet) {
		this.resultSet = resultSet;
	}
	
}
