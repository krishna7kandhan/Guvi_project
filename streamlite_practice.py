import psycopg2
import pandas as pd 
import streamlit as st 


#Postgresql Database connection 			
def db_connection():
	try:			
		db_conn_status = "postgresql://krishna:4YEGQ6WJavQHCDcyXmRH5ltplDbSZ3Bd@dpg-d1t45hmr433s73evet20-a.singapore-postgres.render.com/krishna_traffic"
		return db_conn_status
	except  Exception as db_conn_error:
		db_conn_status=st.error(f"DATABASE CONNECTION FAILURE: {db_conn_error}")
		return none
	
#Fecthing data from Connected Database
def db_fetch_info(DB_QUERY):
	db_conn_status = db_connection()
	if db_conn_status:
		try:
			cur = db_conn_status.cursor()
			cur.execute(query)
			query_result = cur.fetchall()
			result_df = pd.DataFrame(query_result)
			cur.close()
			return result_df 
		except Exception as db_error:
			     result_df=st.error(f"Database error: {db_error}") 
			     return result_df
	else:
		st.error("Database Connection error") 
		return pd.DataFrame()

#streamlite UI 
st.set_page_config(page_title="GUVI-Krishna Kumar Traffic police logs insights project1", layout = "wide")
st.title("GUVI PROJECT1 : TRAFFIC POLICE CHECKPOST STATISTICAL DATA")
st.header("Guvi project1 on Traffic police logs insights")
st.subheader("-developed by Krishna Kumar M")	

#Show full table 
st.header("TRAFFIC POLICE LOGS - OVERVIEW")
query = "select * from traffic_stops"
result_data = db_fetch_info(query)
#st.dataframe("Key Metrics")	
st.dataframe(result_data)	