import psycopg2
import pandas as pd 
import streamlit as st 


#Postgresql Database connection 			
def db_connection():
	try:			
		#db_conn_status = "psycopg2://krishna:4YEGQ6WJavQHCDcyXmRH5ltplDbSZ3Bd@dpg-d1t45hmr433s73evet20-a.singapore-postgres.render.com/krishna_traffic"
		db_conn_status = psycopg2.connect(database="krishna_traffic",
                        host="dpg-d1t45hmr433s73evet20-a.singapore-postgres.render.com",
                        user="krishna",
                        password="4YEGQ6WJavQHCDcyXmRH5ltplDbSZ3Bd",
                        port="5432")
		return db_conn_status
	except  Exception as db_conn_error:
		st.error(f"DATABASE CONNECTION FAILURE: {db_conn_error}")
		return None
	
#Fecthing data from Connected Database
def db_fetch_info(DB_QUERY):
	db_conn_status = db_connection()
	if db_conn_status:
		try:
			cur = db_conn_status.cursor()
			cur.execute(query)
			query_result = cur.fetchall()
			result_df = pd.DataFrame(query_result)
			#cur.close()
			return result_df 
		except Exception as db_error:
			st.error(f"Database error: {db_error}") 
			return None
	else:
		st.error("Database Connection error") 
		return None

#streamlite UI 
st.set_page_config(page_title="GUVI-Krishna Kumar Traffic police logs insights project1", layout = "wide")
st.title("GUVI PROJECT1 : TRAFFIC POLICE CHECKPOST STATISTICAL DATA")
st.header("Guvi project1 on Traffic police logs insights")
st.subheader("-developed by Krishna Kumar M")	

#Show full table 
st.header("TRAFFIC POLICE LOGS - OVERVIEW")
query = "select * from stop_details where country_name = 'INDIA'"
result_data = db_fetch_info(query)

st.dataframe(result_data)	
st.subheader("Key Metrics")	

col1, col2, col3, col4 = st.columns(4)

with col1:
	total_stops = result_data.shape[0]
	st.metric("Total Police Stops",total_stops)
	
with col2:
	arrests = result_data[result_data[6].str.contains("ARREST", case=False, na=False)].shape[0]
	st.metric("Total Arrests",arrests)
	
with col3:
	warnings = result_data[result_data[6].str.contains("WARNING",case=False, na=False)].shape[0]
	st.metric("Total Warnings",warnings)
	
with col4:
	drug_related = result_data[result_data[7] == 1].shape[0]
	st.metric("Total Drug related stops",drug_related)
	