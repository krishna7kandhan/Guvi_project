import psycopg2
import pandas as pd 
import streamlit as st 
import plotly.express as px
#import numpy as np
import matplotlib.pyplot as plt


#Postgresql DB connection 
def db_connection():
	try:			
		db_conn_status = psycopg2.connect(database="krishna_traffic",
                        host="dpg-d1t45hmr433s73evet20-a.singapore-postgres.render.com",
                        user="krishna",
                        password="4YEGQ6WJavQHCDcyXmRH5ltplDbSZ3Bd",
                        port="5432")
		return db_conn_status
	except  Exception as db_conn_error:
		st.error(f"DATABASE CONNECTION FAILURE: {db_conn_error}")
		return None
	

#Function definition to run the SQL query passed
#Arguments : SQL query

def db_fetch_info(DB_QUERY):
    db_conn_status = db_connection()
    if db_conn_status:
        cursor = db_conn_status.cursor()
        try:
            cursor.execute(user_query)
            # Fetch results for SELECT queries
            if user_query.strip().lower().startswith("select"):
                query_result = cursor.fetchall()
                result_df = query_result
                return result_df
            else:
                db_conn_status.commit()
                st.success("Query executed successfully !")
                return None
        except Exception as db_error:
            st.error(f"Database error !!!: {db_error}")
            return None
        finally:
            cursor.close()
            db_conn_status.close()
    else:
        st.error(f"DATABASE CONNECTION ERROR !!!")
        return None
		
#streamlite Configurations
st.set_page_config(
    page_title="GUVI-Krishna Kumar Traffic Police Logs Insights Project1",
    layout="wide"
)
st.title(":red[GUVI PROJECT1 : TRAFFIC POLICE CHECKPOST STATISTICAL DATA]")
st.markdown(":green[Guvi Project1 on Traffic Police Logs Insights]")
st.markdown(":orange[-developed by Krishna Kumar M]")


#Show full table stop_details data
st.title(":red[TRAFFIC POLICE LOGS - OVERVIEW]",width="stretch")
user_query = "select * from stop_logs"
result_dis = db_fetch_info(user_query)
#defining the columns to show the data output
columns = ['country_name', 'driver_gender','driver_age','driver_race','violation','search_conducted','search_type','stop_outcome','is_arrested','stop_duration','drugs_related_stop','vehicle_number','stop_datetime']
result_data = pd.DataFrame(result_dis, columns = columns)

#Configuring the column data 
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

st.title(":red[Key Metrics from the Traffic log]",width="stretch")	
col1, col2, col3, col4 = st.columns(4)

with col1:
	total_stops = result_data.shape[0]
	st.metric(":green[Total Police Stops]",total_stops)
	#plt.figure(figsize=(5, 2))
	#plt.hist(total_stops, bins=500, color='blue', edgecolor='white')
	#plt.title('Total Stops')
	#plt.xlabel('Value')
	#plt.ylabel('stop count')
	#plt.legend()
	#plt.show()
	
with col2:
	arrests = result_data[result_data['stop_outcome'].str.contains("ARREST", case=False, na=False)].shape[0]
	st.metric(":green[Total Arrests]",arrests)
	
with col3:
	warnings = result_data[result_data['stop_outcome'].str.contains("WARNING",case=False, na=False)].shape[0]
	st.metric(":green[Total Warnings]",warnings)
	
with col4:
	drug_related = result_data[result_data['drugs_related_stop'] == 1].shape[0]
	st.metric(":green[Total Drug related stops]",drug_related)
	
#charts
st.title(":red[Visual Presentation]",width="stretch")
tab1, tab2 = st.tabs([":green[Stops by Violation]",":green[Distribution of Driver Gender]"])

with tab1:
	if not result_data.empty and 'violation' in result_data.columns:
		violation_data = result_data['violation'].value_counts().reset_index()
		violation_data.columns = ['violation','count']
		chart = px.pie(violation_data, names='violation', values='count',title= "Stops by Violation Types")
		st.plotly_chart(chart,use_container_width=True)
	else:
		st.warning(":red[No data available!!!]")
		
with tab2:
	if not result_data.empty and 'driver_gender' in result_data.columns:
		gender_data = result_data['driver_gender'].value_counts().reset_index()
		gender_data.columns = ['Gender','Count']
		chart = px.bar(gender_data, x='Gender', y='Count', title="Driver Gender Distribution", color = 'Gender')
		st.plotly_chart(chart,use_container_width=True) 
	else:
		st.warning(":red[No Data Available!!!]")

#Advanced Queries
st.title(":red[Advanced DATA Insights]",width="stretch")

selected_query = st.selectbox(":green[select a query to run]",[
"Total Number of Police Stops",
"Count of Stops by Violation Types",
"Number of Arrests Vs Warnings",
"Average age of Drivers stopped",
"Top 5 most frequent search types",
"Count of Stops by Gender",
"Most common Violation for Arrests"])

query_map = {
    "Total Number of Police Stops": "SELECT COUNT(*) AS STOP_COUNTS FROM stop_logs",
    "Count of Stops by Violation Types": "SELECT violation, COUNT(*) AS VIOLATION_COUNTS FROM stop_logs GROUP BY violation ORDER BY count DESC",
    "Number of Arrests Vs Warnings": "SELECT stop_outcome, COUNT(*) AS STOP_COUNTS FROM stop_logs GROUP BY stop_outcome",
    "Average age of Drivers stopped": "SELECT floor(AVG(driver_age)) AS AVERAGE_AGE FROM stop_logs",
    "Top 5 most frequent search types": "SELECT search_type, COUNT(*) AS SEARCH_COUNTS FROM stop_logs WHERE search_type != '' GROUP BY search_type ORDER BY count DESC LIMIT 5",
    "Count of Stops by Gender": "SELECT driver_gender, COUNT(*) AS GENDER_COUNTS FROM stop_logs GROUP BY driver_gender",
    "Most common Violation for Arrests": "SELECT violation, COUNT(*) AS VIOLATION_COUNTS FROM stop_logs WHERE stop_outcome LIKE '%ARREST%' GROUP BY violation ORDER BY count DESC LIMIT 1"
}

if st.button("Run Query"):
	user_query = query_map[selected_query]
	result = db_fetch_info(user_query)
	result_out = pd.DataFrame(result)
	if not result_out.empty:
		st.write(result_out)
	else:
		st.error(":red[No Result Found for Selected Query]")
		

#QUERY Categories and respective results:
query_options = {
    "Vehicle-Based Queries": [
        "What are the top 10 vehicle_Number involved in drug-related stops?",
        "Which top 10 vehicles were most recently searched?"
    ],
    "Demographic-Based Queries": [
        "Which driver age group had the highest arrest rate?",
        "What is the gender distribution of drivers stopped in each country?",
        "Which race and gender combination has the highest search rate?"
    ],
    "Time & Duration based Queries": [
        "What time of day sees the most traffic stops?",
        "What is the average stop duration for different violations?",
        "Are stops during the night more likely to lead to arrests?"
    ],
    "Violation Based Queries": [
        "Which violations are most associated with searches or arrests?",
        "Which violations are most common among younger drivers (<25)?",
        "Is there a violation that rarely results in search or arrest?"
    ],
    "Location Based Queries": [
        "Which countries report the highest rate of drug-related stops?",
        "What is the arrest rate by country and violation?",
        "Which country has the most stops with search conducted?"
    ],
    "Complex Queries & Statistics": [
        "Yearly Breakdown of Stops and Arrests by Country",
        "Driver Violation Trends Based on Age and Race",
        "Time Period Analysis of Stops-Number of Stops by Year,Month, Hour of the Day",
        "Violations with High Search and Arrest Rates",
        "Driver Demographics by Country",
        "Top 5 Violations with Highest Arrest Rates"
    ]
}

# SQL query map (as you defined)
query_map2 = {
"What are the top 10 vehicle_Number involved in drug-related stops?": "select distinct vehicle_number from stop_logs where drugs_related_stop = '1' LIMIT 10",
"Which top 10 vehicles were most recently searched?" : "select vehicle_number, stop_datetime,count(*) AS STOP_COUNTS from stop_logs where search_conducted = '1' and search_type = 'VEHICLE SEARCH' group by vehicle_number,stop_datetime order by stop_datetime desc LIMIT 10",
"Which driver age group had the highest arrest rate?" : "select stop_outcome,driver_age,count(*) AS ARREST_COUNT from stop_logs where stop_outcome = 'ARREST' group by stop_outcome,driver_age order by ARREST_COUNT desc limit '1'",
"What is the gender distribution of drivers stopped in each country?": "select country_name,driver_gender,count(*) AS GENDER_DISTRIBUTION  from stop_logs group by country_name,driver_gender order by country_name,driver_gender",
"Which race and gender combination has the highest search rate?" : "select driver_race,driver_gender,count(*) AS SEARCH_RATE from stop_logs group by driver_race,driver_gender order by SEARCH_RATE desc LIMIT 1",
"What time of day sees the most traffic stops?" : "SELECT date_part('hour', stop_datetime) AS HOUR ,count(*) AS STOP_COUNTS from stop_logs group by HOUR order by STOP_COUNTS desc",
"What is the average stop duration for different violations?" : "SELECT distinct violation, floor(avg(cast (stop_duration as INTEGER))) AS STOP_DURATION_AVERAGE from stop_logs group by violation order by STOP_DURATION_AVERAGE asc",
"Are stops during the night more likely to lead to arrests?" : "SELECT time_of_day,sum(stop_counts) AS TOTAL_STOP_COUNTS from (select date_part('hour', stop_datetime) AS HOUR, case when ((date_part('hour', stop_datetime)) < 19 and (date_part('hour', stop_datetime) > 7)) then 'DAY' else 'NIGHT' end as TIME_OF_DAY, count(*) AS STOP_COUNTS from stop_logs where stop_outcome = 'ARREST' group by HOUR,TIME_OF_DAY) group by TIME_OF_DAY order by TOTAL_STOP_COUNTS desc",
"Which violations are most associated with searches or arrests?" : "select violation ,count(*) AS VIOLATION_COUNTS from stop_logs where  (search_type = 'VEHICLE SEARCH' OR stop_outcome = 'ARREST') group by violation order by VIOLATION_COUNTS desc LIMIT 1",
"Which violations are most common among younger drivers (<25)?" : "SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE DRIVER_AGE < 25 GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS DESC LIMIT 1",
"Is there a violation that rarely results in search or arrest?" : "SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE (STOP_OUTCOME = 'ARREST' OR SEARCH_TYPE = 'VEHICLE SEARCH')GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS ASC LIMIT 1",
"Which countries report the highest rate of drug-related stops?" : "SELECT COUNTRY_NAME,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE DRUGS_RELATED_STOP = '1' GROUP BY COUNTRY_NAME ORDER BY VIOLATION_COUNTS DESC LIMIT 3",
"What is the arrest rate by country and violation?" : "SELECT COUNTRY_NAME, VIOLATION, FLOOR(AVG(STOP_COUNTS)) AS AVG_STOP_COUNT FROM (SELECT COUNTRY_NAME,VIOLATION,COUNT(*) AS STOP_COUNTS FROM STOP_LOGS WHERE STOP_OUTCOME = 'ARREST' GROUP BY COUNTRY_NAME, VIOLATION ) GROUP BY COUNTRY_NAME, VIOLATION ORDER BY COUNTRY_NAME, VIOLATION, AVG_STOP_COUNT",
"Which country has the most stops with search conducted?" : "SELECT COUNTRY_NAME,COUNT(*) AS STOP_COUNTS FROM STOP_LOGS WHERE SEARCH_CONDUCTED = '1' GROUP BY COUNTRY_NAME ORDER BY STOP_COUNTS DESC LIMIT 100",
"Yearly Breakdown of Stops and Arrests by Country" : "select date_part('year', stop_datetime) AS YEAR, country_name, search_type,stop_outcome,count(*) AS STOP_COUNTS from stop_logs where stop_outcome = 'ARREST' and search_type = 'VEHICLE SEARCH' group by YEAR,country_name, search_type,stop_outcome order by YEAR,country_name, search_type,stop_outcome",
"Driver Violation Trends Based on Age and Race" : "select YEAR,MONTH,DAY_DESC,driver_race,driver_gender,DRIVER_CATEGORY,count(stop_outcome) AS TOTAL_ARRESTS ,count(search_conducted) AS TOTAL_SEARCHES,count(drugs_related_stop) total_drug_cases from (select driver_race, driver_age,driver_gender,violation,date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,CASE when ((date_part('hour', stop_datetime)) > 6 and (date_part('hour', stop_datetime)) < 18) then 'DAY-HOURS' else 'NIGHT-HOURS' end AS DAY_DESC,search_type, stop_outcome,case 	when (( driver_age < 50) and (driver_age > 16)) then 'MIDDLE AGE' 	else 'ELDERS' end AS DRIVER_CATEGORY,search_conducted,drugs_related_stop from stop_logs ) stops_check where drugs_related_stop = '1' and search_conducted = '1' and stop_outcome = 'ARREST' group by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category order by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category,TOTAL_ARRESTS desc,TOTAL_SEARCHES desc,total_drug_cases desc",
"Time Period Analysis of Stops-Number of Stops by Year,Month, Hour of the Day" : "select date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,count(*) AS STOP_COUNTS from stop_logs group by YEAR,MONTH,HOUR order by YEAR,MONTH,HOUR",
"Violations with High Search and Arrest Rates" : "SELECT violation,MAX(STOP_COUNTS) OVER (PARTITION BY violation) AS MAX_STOP_COUNTS FROM (select violation,search_type,stop_outcome ,count(*) AS STOP_COUNTS from stop_logs group by violation ,search_type,stop_outcome) WHERE SEARCH_TYPE = 'VEHICLE SEARCH' AND STOP_OUTCOME = 'ARREST' order by MAX_STOP_COUNTS desc ",
"Driver Demographics by Country" : "select country_name, driver_race,driver_gender,driver_age,count(*) AS STOP_COUNTS from stop_logs group by country_name,driver_race, driver_gender,driver_age order by country_name, driver_race,driver_gender,driver_age",
"Top 5 Violations with Highest Arrest Rates" : "select violation,count(*) AS ARREST_RATES from stop_logs where stop_outcome = 'ARREST' group by violation order by ARREST_RATES desc limit 5"
}
	
query_map3 = {
"select distinct vehicle_number from stop_logs where drugs_related_stop = '1' LIMIT 10" : ['VEHICLE_NUMBER'],
"select vehicle_number, stop_datetime,count(*) AS STOP_COUNTS from stop_logs where search_conducted = '1' and search_type = 'VEHICLE SEARCH' group by vehicle_number,stop_datetime order by stop_datetime desc LIMIT 10" : ['VEHICLE_NUMBER','STOP_DATETIME','STOP_COUNTS'],
"select stop_outcome,driver_age,count(*) AS ARREST_COUNT from stop_logs where stop_outcome = 'ARREST' group by stop_outcome,driver_age order by ARREST_COUNT desc limit '1'" : ['STOP_OUTCOME','DRIVER_AGE','ARREST_COUNT'],
"select country_name,driver_gender,count(*) AS GENDER_DISTRIBUTION  from stop_logs group by country_name,driver_gender order by country_name,driver_gender" : ['COUNTRY_NAME','DRIVER_NAME','GENDER_DISTRIBUTION'],
"select driver_race,driver_gender,count(*) AS SEARCH_RATE from stop_logs group by driver_race,driver_gender order by SEARCH_RATE desc LIMIT 1" : ['DRIVER_RACE','DRIVER_GENDER','SEARCH_RATE'],
"SELECT date_part('hour', stop_datetime) AS HOUR ,count(*) AS STOP_COUNTS from stop_logs group by HOUR order by STOP_COUNTS desc" : ['HOUR','STOP_COUNTS'],
"SELECT distinct violation, floor(avg(cast (stop_duration as INTEGER))) AS STOP_DURATION_AVERAGE from stop_logs group by violation order by STOP_DURATION_AVERAGE asc" : ['VIOLATION','STOP_DURATION_AVERAGE (mins)'],
"SELECT time_of_day,sum(stop_counts) AS TOTAL_STOP_COUNTS from (select date_part('hour', stop_datetime) AS HOUR, case when ((date_part('hour', stop_datetime)) < 19 and (date_part('hour', stop_datetime) > 7)) then 'DAY' else 'NIGHT' end as TIME_OF_DAY, count(*) AS STOP_COUNTS from stop_logs where stop_outcome = 'ARREST' group by HOUR,TIME_OF_DAY) group by TIME_OF_DAY order by TOTAL_STOP_COUNTS desc" : ['TIME_OF_DAY','TOTAL_STOP_COUNTS'],
"select violation ,count(*) AS VIOLATION_COUNTS from stop_logs where  (search_type = 'VEHICLE SEARCH' OR stop_outcome = 'ARREST') group by violation order by VIOLATION_COUNTS desc LIMIT 1" : ['VIOLATION','VIOLATION_COUNTS'],
"SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE DRIVER_AGE < 25 GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS DESC LIMIT 1" : ['VIOLATION','STOP_COUNTS'],
"SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE (STOP_OUTCOME = 'ARREST' OR SEARCH_TYPE = 'VEHICLE SEARCH')GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS ASC LIMIT 1" : ['VIOLATION','VIOLATION_COUNTS'],
"SELECT COUNTRY_NAME,COUNT(*) AS VIOLATION_COUNTS FROM STOP_LOGS WHERE DRUGS_RELATED_STOP = '1' GROUP BY COUNTRY_NAME ORDER BY VIOLATION_COUNTS DESC LIMIT 3" : ['COUNTRY_NAME','VIOLATION_COUNTS'],
"SELECT COUNTRY_NAME, VIOLATION, FLOOR(AVG(STOP_COUNTS)) AS AVG_STOP_COUNT FROM (SELECT COUNTRY_NAME,VIOLATION,COUNT(*) AS STOP_COUNTS FROM STOP_LOGS WHERE STOP_OUTCOME = 'ARREST' GROUP BY COUNTRY_NAME, VIOLATION ) GROUP BY COUNTRY_NAME, VIOLATION ORDER BY COUNTRY_NAME, VIOLATION, AVG_STOP_COUNT" : ['COUNTRY_NAME','VIOLATION','AVG_STOP_COUNT'],
"SELECT COUNTRY_NAME,COUNT(*) AS STOP_COUNTS FROM STOP_LOGS WHERE SEARCH_CONDUCTED = '1' GROUP BY COUNTRY_NAME ORDER BY STOP_COUNTS DESC LIMIT 100" : ['COUNTRY_NAME','STOP_COUNTS'],
"select date_part('year', stop_datetime) AS YEAR, country_name, search_type,stop_outcome,count(*) AS STOP_COUNTS from stop_logs where stop_outcome = 'ARREST' and search_type = 'VEHICLE SEARCH' group by YEAR,country_name, search_type,stop_outcome order by YEAR,country_name, search_type,stop_outcome" : ['YEAR','COUNTRY_NAME','SEARCH_TYPE','SEARCH_OUTCOME','STOP_COUNTS'],
"select YEAR,MONTH,DAY_DESC,driver_race,driver_gender,DRIVER_CATEGORY,count(stop_outcome) AS TOTAL_ARRESTS ,count(search_conducted) AS TOTAL_SEARCHES,count(drugs_related_stop) total_drug_cases from (select driver_race, driver_age,driver_gender,violation,date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,CASE when ((date_part('hour', stop_datetime)) > 6 and (date_part('hour', stop_datetime)) < 18) then 'DAY-HOURS' else 'NIGHT-HOURS' end AS DAY_DESC,search_type, stop_outcome,case 	when (( driver_age < 50) and (driver_age > 16)) then 'MIDDLE AGE' 	else 'ELDERS' end AS DRIVER_CATEGORY,search_conducted,drugs_related_stop from stop_logs ) stops_check where drugs_related_stop = '1' and search_conducted = '1' and stop_outcome = 'ARREST' group by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category order by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category,TOTAL_ARRESTS desc,TOTAL_SEARCHES desc,total_drug_cases desc" : ['YEAR','MONTH','DAY_DESC','DRIVER_RACE','DRIVER_GENDER','DRIVER_CATEGOTY','TOTAL_ARRESTS','TOTAL_SEARCHES','TOTAL_DRUG_CASES'],
"select date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,count(*) AS STOP_COUNTS from stop_logs group by YEAR,MONTH,HOUR order by YEAR,MONTH,HOUR" : ['YEAR','MONTH','HOUR','STOP_COUNTS'],
"SELECT violation,MAX(STOP_COUNTS) OVER (PARTITION BY violation) AS MAX_STOP_COUNTS FROM (select violation,search_type,stop_outcome ,count(*) AS STOP_COUNTS from stop_logs group by violation ,search_type,stop_outcome) WHERE SEARCH_TYPE = 'VEHICLE SEARCH' AND STOP_OUTCOME = 'ARREST' order by MAX_STOP_COUNTS desc " : ['VIOLATION','MAX_STOP_COUNTS'],
"select country_name, driver_race,driver_gender,driver_age,count(*) AS STOP_COUNTS from stop_logs group by country_name,driver_race, driver_gender,driver_age order by country_name, driver_race,driver_gender,driver_age" : ['COUNTRY_NAME','DRIVER_RACE','DRIVER_GENDER','DRIVER_AGE','STOP_COUNTS'],
"select violation,count(*) AS ARREST_RATES from stop_logs where stop_outcome = 'ARREST' group by violation order by ARREST_RATES desc limit 5" : ['VIOLATION','ARREST_RATES']
}
#to reset the category select box 
def reset_category_type_value_selectbox():
    st.session_state.category_type_value = "No Categories selected"

if "category_type_value" not in st.session_state:
    st.session_state.category_type_value = "No Categories selected"

#Initializing the query list list
category_query_list=[]

st.title(":red[Traffic Violation Stops Categories and respective Query]",width="stretch")

if st.button("Reset"):
    reset_category_type_value_selectbox()

#Creating form with categories to select
with st.form("Create category"): 
    category_type = st.selectbox(":green[Select category to query]",[ 
                                "Vehicle-Based Queries", 
                                "Demographic-Based Queries", 
                                "Time & Duration based Queries", 
                                "Violation Based Queries", 
                                "Location Based Queries", 
                                "Complex Queries & Statistics"],key="category_type_value")
    timestamp = pd.Timestamp.now()
    submit_form = st.form_submit_button("Select Query")

for category in query_options.get(category_type,[]):
    category_query_list.append(category)
if category_query_list:
    with st.form("create Query"): 
        category_query = st.selectbox(":green[select a query to run:]",
                                           category_query_list,
                                           key="category_query_value")
        timestamp = pd.Timestamp.now()
        submit_form = st.form_submit_button("Run Query")
    user_query_res = query_map2.get(category_query,[])
    user_query = user_query_res
    result_info = db_fetch_info(user_query)
    columns=query_map3.get(user_query_res,[])
    result_output = pd.DataFrame(result_info, columns = columns)
    if not result_output.empty:
        result_output = st.write(result_output)
    else:
        st.markdown(":red[ERROR fetching result for the selected query]")

st.title(":red[Police Log Prediction and Results-User Data]",width="stretch")		
st.markdown("Fill in the details below to get the natural Language prediction of the stop outcome based on existing data.")
st.markdown(":green[Add New Police Log & Predict Outcome and violation]")

def reset_user_prediction_value_selectbox():
    st.session_state.country_name_value = "No Country Name selected"
    st.session_state.gender_value = "No Driver Gender selected"
    st.session_state.race_value = "No Driver Race selected"
    st.session_state.srch_con_value = "Yes/No"
    st.session_state.srch_type_value = "No Search Type selected"
    st.session_state.drug_rel_value = "Yes/No"
    st.session_state.stop_dur_value = "No Stop Duration selected"

    if "country_name_value" not in st.session_state:
        st.session_state.country_name_value = "No Country Name selected"
    if "gender_value" not in st.session_state:
        st.session_state.gender_value = "No Driver Gender selected"
    if "race_value" not in st.session_state:
        st.session_state.race_value = "No Driver Race selected"
    if "srch_con_value" not in st.session_state:
        st.session_state.srch_con_value = "Yes/No"
    if "srch_type_value" not in st.session_state:
        st.session_state.srch_type_value = "No Search Type selected"
    if "drug_rel_value" not in st.session_state:
        st.session_state.drug_rel_value = "Yes/No"
    if "stop_dur_value" not in st.session_state:
        st.session_state.stop_dur_value = "No Stop Duration selected"
        
    return None

if st.button("Reset_Value"):
    reset_user_prediction_value_selectbox()
#Create form page to get input data from user
with st.form("create_form"):
    country_name = st.selectbox("Country Name",
                                result_data['country_name'].dropna().unique(),
                                key="country_name_value")
    driver_gender = st.selectbox("Driver Gender",
                                ["Male", "Female"],
                                key="gender_value")
    driver_age = st.number_input("Driver Age",
                                min_value=16,
                                max_value=100,
                                value=27)
    driver_race = st.selectbox("Driver Race",
                                result_data['driver_race'].dropna().unique(),
                                key="race_value")
    search_conducted = st.selectbox("Search Conducted?",
                                ["Yes", "No"],
                                key="srch_con_value")
    search_type = st.selectbox("Search Type",
                                result_data['search_type'].dropna().unique(),
                                key="srch_type_value")
    drugs_related_stop = st.selectbox("Drug Related?",
                                ["Yes", "No"],
                                key="drug_rel_value")
    stop_duration = st.selectbox("Stop Duration (in Min)",
                                result_data['stop_duration'].dropna().unique(),
                                key="stop_dur_value")
    vehicle_number = st.text_input("Vehicle Number")
    stop_datetime = st.date_input("Stop Datetime")
    
    timestamp = pd.Timestamp.now()
    submit_form = st.form_submit_button("Predict the Stop Outcome & Violation")


if submit_form:
    user_input_data = result_data[
        (result_data['driver_gender'] == driver_gender) &
        (result_data['driver_age'] == driver_age) &
        (result_data['search_conducted'] == 1) &
        (result_data['stop_duration'] == stop_duration) &
        (result_data['drugs_related_stop'] == 1)
    ]

    if not user_input_data.empty:
        predicted_outcome = user_input_data['stop_outcome'].mode()[0]
        predicted_violation = user_input_data['violation'].mode()[0]
    else:
        predicted_outcome = "WARNING"
        predicted_violation = "SPEEDING"

		
    #Stop outcome summary
    search_text = "A search was conducted" if search_conducted else "No Search was Conducted"
    drug_text = "Was Drug Related" if drugs_related_stop else "Was No Drug Related"

    st.markdown(":red[TRAFFIC LOG PREDICTION SUMMARY:]")
    st.markdown(f"&nbsp;&nbsp;:green[Predicted Violation:] :red[{predicted_violation}]")
    st.markdown(f"&nbsp;&nbsp;:green[Predicted Stop Outcome:] :red[{predicted_outcome}]")
    st.markdown("  \n  \n")

    st.markdown(f"&ensp;&ensp;:blue[A ]:orange[ {driver_age}]:blue[ year old ]:orange[ {driver_gender}]:blue[ driver from]:orange[ {country_name}]:blue[ was stopped at] :orange[ {stop_datetime.strftime('%I:%M:%p')}.]")
    st.markdown(f"&ensp;&ensp;:orange[{search_text}]:blue[ and the stop outcome ]:orange[ {drug_text}.]")
    st.markdown("  \n  \n")

    st.markdown(f"&emsp;:blue[Stop Duration: ]:orange[ {stop_duration}mins]")
    st.markdown(f"&emsp;:blue[Vehicle Number: ]:orange[ {vehicle_number}]")

                     