import psycopg2
import pandas as pd 
import streamlit as st 
import plotly.express as px

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
			#result_df = pd.DataFrame(query_result)
			result_df=query_result
			#cur.close()
			return result_df 
		except Exception as db_error:
			st.error(f"Database error: {db_error}") 
			return None
		finally:
			cur.close()
	else:
		st.error("Database Connection error") 
		return None

#streamlite UI 
st.set_page_config(
    page_title="GUVI-Krishna Kumar Traffic Police Logs Insights Project1",
    layout="wide"
)
st.title(":red[GUVI PROJECT1 : TRAFFIC POLICE CHECKPOST STATISTICAL DATA]")
st.markdown("**Guvi Project1 on Traffic Police Logs Insights**")
st.markdown("***-developed by Krishna Kumar M***")


#Show full table 
st.markdown("**TRAFFIC POLICE LOGS - OVERVIEW**",width="stretch")
query = "select * from stop_details"
result_dis = db_fetch_info(query)
#result_data = result_data.reset_index(drop=True, inplace=False)
#result_data = result.data
columns = ['country_name', 'driver_gender','driver_age','driver_race','violation','search_conducted','search_type','stop_outcome','is_arrested','stop_duration','drugs_related_stop','vehicle_number','stop_datetime']
result_data = pd.DataFrame(result_dis, columns = columns)
st.write(result_data)
st.markdown("***Key Metrics***")	

col1, col2, col3, col4 = st.columns(4)

with col1:
	total_stops = result_data.shape[0]
	st.metric("Total Police Stops",total_stops)
	
with col2:
	arrests = result_data[result_data['stop_outcome'].str.contains("ARREST", case=False, na=False)].shape[0]
	st.metric("Total Arrests",arrests)
	
with col3:
	warnings = result_data[result_data['stop_outcome'].str.contains("WARNING",case=False, na=False)].shape[0]
	st.metric("Total Warnings",warnings)
	
with col4:
	drug_related = result_data[result_data['drugs_related_stop'] == 1].shape[0]
	st.metric("Total Drug related stops",drug_related)
	
#charts
st.title(":blue[Visual Insights]")
tab1, tab2 = st.tabs(["stops by violation","Driver Gender Distribution"])

with tab1:
	if not result_data.empty and 'violation' in result_data.columns:
		violation_data = result_data['violation'].value_counts().reset_index()
		violation_data.columns = ['violation','count']
		#fig = px.bar(violation_data, x='violation', y='count', title="Stops by Violation Types", color = 'violation')
		fig = px.pie(violation_data, names='violation', values='count',title= "Stops by Violation Types")
		st.plotly_chart(fig,use_container_width=True)
	else:
		st.warning("No data available for Violation chart.")
		
with tab2:
	if not result_data.empty and 'driver_gender' in result_data.columns:
		gender_data = result_data['driver_gender'].value_counts().reset_index()
		gender_data.columns = ['Gender','Count']
		#fig = px.pie(gender_data, names='Gender', values='Count',title= "Driver Gender Distribution")
		fig = px.bar(gender_data, x='Gender', y='Count', title="Driver Gender Distribution", color = 'Gender')
		st.plotly_chart(fig,use_container_width=True) 
	else:
		st.warning("No Data Available for Driver Gender Chart.")

#Advanced Queries
st.title(":red[Advanced Insights]")

selected_query = st.selectbox("select a query to run",[
"Total Number of Police Stops",
"Count of Stops by Violation Types",
"Number of Arrests Vs Warnings",
"Average age of Drivers stopped",
"Top 5 most frequent search types",
"Count of Stops by Gender",
"Most common Violation for Arrests"])

query_map = {
    "Total Number of Police Stops": "SELECT COUNT(*) AS total_stops FROM stop_details",
    "Count of Stops by Violation Types": "SELECT violation, COUNT(*) AS count FROM stop_details GROUP BY violation ORDER BY count DESC",
    "Number of Arrests Vs Warnings": "SELECT stop_outcome, COUNT(*) AS count FROM stop_details GROUP BY stop_outcome",
    "Average age of Drivers stopped": "SELECT AVG(driver_age) AS average_age FROM stop_details",
    "Top 5 most frequent search types": "SELECT search_type, COUNT(*) AS count FROM stop_details WHERE search_type != '' GROUP BY search_type ORDER BY count DESC LIMIT 5",
    "Count of Stops by Gender": "SELECT driver_gender, COUNT(*) AS count FROM stop_details GROUP BY driver_gender",
    "Most common Violation for Arrests": "SELECT violation, COUNT(*) AS count FROM stop_details WHERE stop_outcome LIKE '%ARREST%' GROUP BY violation ORDER BY count DESC LIMIT 1"
}

if st.button("Run Query"):
	query = query_map[selected_query]
	result = db_fetch_info(query)
	#columns = ['country_name', 'driver_gender','driver_age','driver_race','violation','search_conducted','search_type','stop_outcome','is_arrested','stop_duration','drugs_related_stop','vehicle_number','stop_datetime']
	result_out = pd.DataFrame(result)
	if not result_out.empty:
		st.write(result_out)
	else:
		st.warning("No Result Found for Selected Query")
		
st.markdown("*----------------------------------------------------------------------------*")
st.markdown("**Built for Law Enforcement by securecheck**")
st.markdown("***Custom Natural Language Filter***")
st.markdown("Fill in the details below to get the natural Language prediction of the stop outcome based on existing data.")
st.markdown("Add New Policies Log & Predict Outcome and violation")
#Input form for all fields (excluding output)
with st.form("new_log_form"):
    country_name = st.text_input("Country_Name")
    driver_gender = st.selectbox("Driver_Gender", ["Male", "Female"])
    driver_age = st.number_input("Driver_Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver_Race")
    search_conducted = st.selectbox("Search Conducted?", [1, 0])
    search_type = st.text_input("Search_Type")
    drugs_related_stop = st.selectbox("Drug Related?", [1, 0])
    stop_duration = st.selectbox("Stop_Duration", result_data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle_Number")
    stop_datetime = st.date_input("Stop_Datetime")
    timestamp = pd.Timestamp.now()

    submit_form = st.form_submit_button("Predict Stop Outcome & Violation")

if submit_form:
    filter_data = result_data[
        (result_data['driver_gender'] == driver_gender) &
        (result_data['driver_age'] == driver_age) &
        (result_data['search_conducted'] == 1) &
        (result_data['stop_duration'] == stop_duration) &
        (result_data['drugs_related_stop'] == 1)
    ]

    if not filter_data.empty:
        predicted_outcome = filter_data['stop_outcome'].mode()[0]
        predicted_violation = filter_data['violation'].mode()[0]
    else:
        predicted_outcome = "WARNING"
        predicted_violation = "SPEEDING"

		
    #Natural Language Summary
    search_text = "A search was conducted" if (search_conducted) else "No Search was Conducted" 
    drug_text = "Was Drug Related" if (drugs_related_stop) else "No Drug related stop" 
	
    st.markdown(f"""
            **prediction summary** 
            **Predicted Violation:** {predicted_violation}
            **Predicted Stop Outcome:** {predicted_outcome}

            A {driver_age} year old {driver_gender} driver from {country_name} was stopped at {stop_datetime.strftime('%I:%M:%p')}
            for {search_text} and the stop {drug_text}.
            stop Duration : **{stop_duration}**
            Vehicle Number: **{vehicle_number}**
            """)