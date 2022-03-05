import streamlit as st
import time
import pandas as pd
def app():
    st.markdown("# API")
#    SQL_script = st.text_area(label='SQL Input', value='SELECT * FROM avlreports limit 1000;')
#
#    @st.cache(allow_output_mutation=True)
#    def get_connection():
#        return create_engine('postgresql://postgres:transitclock@goeuropa.tk:5432/MPK')
#
#    @st.cache
#    def load_data(SQL_script):
#        with st.spinner('Loading Data...'):
#            time.sleep(0.5)
#            df = pd.read_sql_query(SQL_script, get_connection())
#        return df
#
#    raw_data = load_data(SQL_script)
#    st.dataframe(raw_data)
