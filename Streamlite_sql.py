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

# Example usage (you’d replace this with a Streamlit input)
with st.form("Type Query"):
       timestamp = pd.Timestamp.now()
       user_query = st.text_input("Enter your SQL query: ")
       submit_form = st.form_submit_button("Run Query")
       if submit_form:
               result = db_fetch_info(user_query)
               if result is not None:
                   result_data=st.dataframe(result)
               else:
                   st.markdown(":red[**ERROR**]")
           
