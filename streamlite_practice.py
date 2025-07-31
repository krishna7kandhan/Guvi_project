import psycopg2
import pandas as pd 
import streamlit as st 
import plotly.express as px
#import numpy as np
import matplotlib.pyplot as plt

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
# style
#th_props = [
# ('font-size', '14px'),
# ('text-align', 'center'),
#  ('font-weight', 'bold'),
# ('color', '#6d6d6d'),
#  ('background-color', '#f7ffff')
# ]
                               
#td_props = [
 # ('font-size', '12px')
# ]
                                 
#styles = [
#  dict(selector="th", props=th_props),
# dict(selector="td", props=td_props)
 #]

#result_info = result_info.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)
#result_data = st.table(result_info) 
result_data = st.data_editor(
    result_data,
    column_config={
        "driver_age": st.column_config.NumberColumn(
            "driver_age",
            help="Age of the driver stopped by police",
            min_value=16,
            max_value=100,
            step=1,
            format="%d",
        ),
		"country_name": st.column_config.SelectboxColumn(
            "country_name",
            help="The country where incident actually happened",
            width="small",
            options=["CANADA","INDIA","OTHER","USA"],
            required=True,
        ),
		"driver_race": st.column_config.SelectboxColumn(
            "driver_race",
            help="Race of the driver",
            width="small",
            options=["ASIAN","BLACK","HISPANIC","OTHER","WHITE"],
            required=True,
        ),
		"violation": st.column_config.SelectboxColumn(
            "violation",
            help="Violation type",
            width="small",
            options=["DUI","OTHER","SPEEDING","SIGNAL","SEATBELT"],
            required=True,
        ),
		"search_type": st.column_config.SelectboxColumn(
            "search_type",
            help="Type of search police conducted",
            width="small",
            options=["FRISK","VEHICLE SEARCH"],
            required=True,
        ),
		"stop_outcome": st.column_config.SelectboxColumn(
            "stop_outcome",
            help="Outcome of the stop",
            width="small",
            options=["ARREST","TICKET","WARNING"],
            required=True,
        ),
		"stop_datetime": st.column_config.DatetimeColumn(
            "stop_datetime",
            help="Stop date time",
            width="medium"
        ),
		"search_conducted": st.column_config.CheckboxColumn(
            "search_conducted",
            help="whether search was conducted or not.Checked box says search was conducted",
            default=False,
        ),
		"is_arrested": st.column_config.CheckboxColumn(
            "is_arrested",
            help="whether driver was arrested or not.Checked box says driver was arrested",
            default=False,
        ),
		"drugs_related_stop": st.column_config.CheckboxColumn(
            "drugs_related_stop",
            help="whether driver was drugged or not.Checked box says driver was drugged",
            default=False,
        ),
		"stop_duration": st.column_config.NumberColumn(
            "stop_duration",
            help="duration of the stop/search conducted by police",
            min_value=15,
            max_value=60,
            step=15,
            format="%d",
        )
    },
    hide_index=True,
)
#st.write(result_data)
st.markdown("***Key Metrics***")	

col1, col2, col3, col4 = st.columns(4)

with col1:
	total_stops = result_data.shape[0]
	st.metric("Total Police Stops",total_stops)
	#plt.figure(figsize=(5, 2))
	#plt.hist(total_stops, bins=500, color='blue', edgecolor='white')
	#plt.title('Total Stops')
	#plt.xlabel('Value')
	#plt.ylabel('stop count')
	#plt.legend()
	#plt.show()
	
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
with st.form("create_form"):
    country_name = st.selectbox("Country Name", result_data['country_name'].dropna().unique())
    driver_gender = st.selectbox("Driver Gender", ["Male", "Female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.selectbox("Driver Race", result_data['driver_race'].dropna().unique())
    search_conducted = st.selectbox("Search Conducted?", ["Yes", "No"])
    search_type = st.selectbox("Search Type", result_data['search_type'].dropna().unique())
    drugs_related_stop = st.selectbox("Drug Related?", ["Yes", "No"])
    stop_duration = st.selectbox("Stop Duration (in Min)", result_data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    stop_datetime = st.date_input("Stop Datetime")
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
    search_text = "A search was conducted" if search_conducted else "No Search was Conducted"
    drug_text = "Was Drug Related" if drugs_related_stop else "Was No Drug Related"

    st.markdown(":blue[TRAFFIC LOG PREDICTION SUMMARY]")
    st.markdown(f"&nbsp;&nbsp;:green[Predicted Violation:] :red[{predicted_violation}]")
    st.markdown(f"&nbsp;&nbsp;:green[Predicted Stop Outcome:] :red[{predicted_outcome}]")
    st.markdown("  \n  \n")

    st.markdown(f"&ensp;&ensp;:blue[A ]:orange[ {driver_age}]:blue[ year old ]:orange[ {driver_gender}]:blue[ driver from]:orange[ {country_name}]:blue[ was stopped at] :orange[ {stop_datetime.strftime('%I:%M:%p')}]")
    st.markdown(f"&ensp;&ensp;:orange[{search_text}]:blue[ and the stop]:orange[ {drug_text}.]")
    st.markdown("  \n  \n")

    st.markdown(f"&emsp;:blue[Stop Duration: ]:orange[ {stop_duration}]")
    st.markdown(f"&emsp;:blue[Vehicle Number: ]:orange[ {vehicle_number}]")

                     