# Load important libraries 
import streamlit as st 
import pandas as pd
import requests

headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'
}

params = (
    ('a', '1211'),
    ('r', '282'),
)

def refactor(tripsInput):
    trips = tripsInput["schedule"][0]["trip"]
    timeForStop = tripsInput["schedule"][0]["timesForStop"]

    for k in timeForStop:
        for i,j in enumerate(k["time"]):
            if j != {}:
                j["trip"] = trips[i]["tripId"]
                j["stopName"] = k["stopName"]

    emp = []
    for i in tripsInput["schedule"][0]["timesForStop"]:
        for j in i["time"]:
            emp.append(j)
    df = pd.DataFrame(emp)
    df = df.astype(str)
    df = df.dropna()
    return df[df["timeStr"] != "nan"]

def app():
    """This application is created to help the user change the metadata for the uploaded file. 
    They can perform merges. Change column names and so on.  
    """

    # Load the uploaded data 
    st.markdown("# Reports")
    response = requests.get('http://iplaner.pl:8093/api/v1/key/f78a2e9a/agency/1211/command/scheduleVertStops', headers=headers, params=params, verify=False)
    scheduled_stops = response.json()


    st.table(refactor(scheduled_stops))

    # Initialize connection.
    # Uses st.cache to only run once.
#    @st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
#    def init_connection():
#        return psycopg2.connect(**st.secrets["postgres"])
#
#    conn = init_connection()
#
#    # Perform query.
#    # Uses st.cache to only rerun when the query changes or after 10 min.
#    #@st.cache(ttl=600)
#    def run_query(query):
#        with conn.cursor() as cur:
#            cur.execute(query)
#            return cur.fetchall()
#
#    rows = conn.cursor().execute("SELECT * from avlreports limit 100000;")
#
#    # Print results.
#    for row in rows:
#        st.write(f"{row[0]} has a :{row[1]}:")
