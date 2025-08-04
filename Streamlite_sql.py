import psycopg2
import pandas as pd
import streamlit as st

def db_connection():
    try:
        db_conn_status = psycopg2.connect(
            database="krishna_traffic",
                        host="dpg-d1t45hmr433s73evet20-a.singapore-postgres.render.com",
                        user="krishna",
                        password="4YEGQ6WJavQHCDcyXmRH5ltplDbSZ3Bd",
                        port="5432")
        return db_conn_status
    except Exception as conn_error:
        st.error(f"Connection failed: {conn_error}")
        return None

def db_fetch_info(user_query):
    db_conn_status = db_connection()
    if db_conn_status:
        cursor = db_conn_status.cursor()
        try:
            cursor.execute(user_query)

            # Fetch results for SELECT queries
            if user_query.strip().lower().startswith("select"):
                query_result = cursor.fetchall()
                #columns = [desc[0] for desc in cursor.description]  # get column names
                #columns = ['country_name', 'driver_gender','driver_age','driver_race','violation','search_conducted','search_type','stop_outcome','is_arrested','stop_duration','drugs_related_stop','vehicle_number','stop_datetime']
                #result_df = pd.DataFrame(query_result, columns=columns)
                result_df = pd.DataFrame(query_result)
                return result_df
            else:
                db_conn_status.commit()
                st.success("Query executed successfully.")
                return None
        except Exception as db_error:
            st.error(f"Database error: {db_error}")
            return None
        finally:
            cursor.close()
            db_conn_status.close()
    else:
        st.error("Database Connection error")
        return None

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
query_map = {
"What are the top 10 vehicle_Number involved in drug-related stops?": "select distinct vehicle_number from stop_details where drugs_related_stop = '1' LIMIT 10",
"Which top 10 vehicles were most recently searched?" : "select vehicle_number, stop_datetime,count(*) from stop_details where search_conducted = '1' and search_type = 'VEHICLE SEARCH' group by vehicle_number,stop_datetime order by stop_datetime desc LIMIT 10",
"Which driver age group had the highest arrest rate?" : "select stop_outcome,driver_age,count(*) AS ARREST_COUNT from stop_details where stop_outcome = 'ARREST' group by stop_outcome,driver_age order by ARREST_COUNT desc limit '1'",
"What is the gender distribution of drivers stopped in each country?": "select country_name,driver_gender,count(*) AS GENDER_DISTRIBUTION  from stop_details group by country_name,driver_gender order by country_name,driver_gender",
"Which race and gender combination has the highest search rate?" : "select driver_race,driver_gender,count(*) AS SEARCH_RATE from stop_details group by driver_race,driver_gender order by SEARCH_RATE desc LIMIT 1",
"What time of day sees the most traffic stops?" : "SELECT date_part('hour', stop_datetime) AS HOUR ,count(*) AS STOP_COUNTS from stop_details group by HOUR order by STOP_COUNTS desc",
"What is the average stop duration for different violations?" : "SELECT distinct violation, floor(avg(cast (stop_duration as INTEGER))) AS STOP_DURATION_AVERAGE from stop_details group by violation order by STOP_DURATION_AVERAGE asc",
"Are stops during the night more likely to lead to arrests?" : "SELECT time_of_day,sum(stop_counts) AS TOTAL_STOP_COUNTS from (select date_part('hour', stop_datetime) AS HOUR, case when ((date_part('hour', stop_datetime)) < 19 and (date_part('hour', stop_datetime) > 7)) then 'DAY' else 'NIGHT' end as TIME_OF_DAY, count(*) AS STOP_COUNTS from stop_details where stop_outcome = 'ARREST' group by HOUR,TIME_OF_DAY) group by TIME_OF_DAY order by TOTAL_STOP_COUNTS desc",
"Which violations are most associated with searches or arrests?" : "select violation ,count(*) AS VIOLATION_COUNTS from stop_details where  (search_type = 'VEHICLE SEARCH' OR stop_outcome = 'ARREST') group by violation order by VIOLATION_COUNTS desc LIMIT 1",
"Which violations are most common among younger drivers (<25)?" : "SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_DETAILS WHERE DRIVER_AGE < 25 GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS DESC LIMIT 1",
"Is there a violation that rarely results in search or arrest?" : "SELECT VIOLATION,COUNT(*) AS VIOLATION_COUNTS FROM STOP_DETAILS WHERE (STOP_OUTCOME = 'ARREST' OR SEARCH_TYPE = 'VEHICLE SEARCH')GROUP BY VIOLATION ORDER BY VIOLATION_COUNTS ASC LIMIT 1",
"Which countries report the highest rate of drug-related stops?" : "SELECT COUNTRY_NAME,COUNT(*) AS VIOLATION_COUNTS FROM STOP_DETAILS WHERE DRUGS_RELATED_STOP = '1' GROUP BY COUNTRY_NAME ORDER BY VIOLATION_COUNTS DESC LIMIT 3",
"What is the arrest rate by country and violation?" : "SELECT COUNTRY_NAME, VIOLATION, FLOOR(AVG(STOP_COUNTS)) AS AVG_STOP_COUNT FROM (SELECT COUNTRY_NAME,VIOLATION,COUNT(*) AS STOP_COUNTS FROM STOP_DETAILS WHERE STOP_OUTCOME = 'ARREST' GROUP BY COUNTRY_NAME, VIOLATION ) GROUP BY COUNTRY_NAME, VIOLATION ORDER BY COUNTRY_NAME, VIOLATION, AVG_STOP_COUNT",
"Which country has the most stops with search conducted?" : "SELECT COUNTRY_NAME,COUNT(*) AS STOP_COUNTS FROM STOP_DETAILS WHERE SEARCH_CONDUCTED = '1' GROUP BY COUNTRY_NAME ORDER BY STOP_COUNTS DESC LIMIT 100",
"Yearly Breakdown of Stops and Arrests by Country" : " select date_part('year', stop_datetime) AS YEAR, country_name, search_type,stop_outcome,count(*) AS STOP_COUNTS from stop_details where stop_outcome = 'ARREST' and search_type = 'VEHICLE SEARCH' group by YEAR,country_name, search_type,stop_outcome order by YEAR,country_name, search_type,stop_outcome",
"Driver Violation Trends Based on Age and Race" : "select YEAR,MONTH,DAY_DESC,driver_race,driver_gender,DRIVER_CATEGORY,count(stop_outcome) AS TOTAL_ARRESTS ,count(search_conducted) AS TOTAL_SEARCHES,count(drugs_related_stop) total_drug_cases from (select driver_race, driver_age,driver_gender,violation,date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,CASE when ((date_part('hour', stop_datetime)) > 6 and (date_part('hour', stop_datetime)) < 18) then 'DAY-HOURS' else 'NIGHT-HOURS' end AS DAY_DESC,search_type, stop_outcome,case 	when (( driver_age < 50) and (driver_age > 16)) then 'MIDDLE AGE' 	else 'ELDERS' end AS DRIVER_CATEGORY,search_conducted,drugs_related_stop from stop_details ) stops_check where drugs_related_stop = '1' and search_conducted = '1' and stop_outcome = 'ARREST' group by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category order by YEAR,MONTH,DAY_DESC,driver_race,driver_gender,driver_category,TOTAL_ARRESTS desc,TOTAL_SEARCHES desc,total_drug_cases desc",
"Time Period Analysis of Stops-Number of Stops by Year,Month, Hour of the Day" : "select date_part('year', stop_datetime) AS YEAR,date_part('month', stop_datetime) AS MONTH,date_part('hour', stop_datetime) AS HOUR,count(*) AS STOP_COUNTS from stop_details group by YEAR,MONTH,HOUR order by YEAR,MONTH,HOUR",
"Violations with High Search and Arrest Rates" : "SELECT violation,MAX(STOP_COUNTS) OVER (PARTITION BY violation) AS MAX_STOP_COUNTS FROM (select violation,search_type,stop_outcome ,count(*) AS STOP_COUNTS from stop_Details group by violation ,search_type,stop_outcome) WHERE SEARCH_TYPE = 'VEHICLE SEARCH' AND STOP_OUTCOME = 'ARREST' order by MAX_STOP_COUNTS desc ",
"Driver Demographics by Country" : "select country_name, driver_race,driver_gender,driver_age,count(*) AS STOP_COUNTS from stop_Details group by country_name,driver_race, driver_gender,driver_age order by country_name, driver_race,driver_gender,driver_age",
"Top 5 Violations with Highest Arrest Rates" : "select violation,count(*) AS ARREST_RATES from stop_details where stop_outcome = 'ARREST' group by violation order by ARREST_RATES desc limit 5"
}


def reset_category_type_value_selectbox():
    st.session_state.category_type_value = "No Categories selected"

#def reset_category_query_value_selectbox():
    #st.session_state.category_query_value = "No Queries from the above Category selected"

if "category_type_value" not in st.session_state:
    st.session_state.category_type_value = "No Categories selected"

#if "category_query_value" not in st.session_state:
    #st.session_state.category_query_value = "No Queries from the above Category selected"

if st.button("Reset"):
    reset_category_type_value_selectbox()
    #reset_category_query_value_selectbox()

category_query_list=[]

with st.form("Create category"): 
    category_type = st.selectbox("Select category to query",[ 
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
        category_query = st.selectbox("select the query to run:",
                                           category_query_list,
                                           key="category_query_value")
        timestamp = pd.Timestamp.now()
        submit_form = st.form_submit_button("Run Query")
    user_query_res = query_map.get(category_query,[])
    user_query = user_query_res
    result = db_fetch_info(user_query)
    if result is not None:
        result_data=st.dataframe(result)
    else:
        st.markdown(":red[**ERROR**]")




           
