import streamlit as st
import plotly.graph_objs as go
from influxdb_client import InfluxDBClient
import pandas as pd

# InfluxDB connection parameters
influxdb_url = "http://localhost:8086"
influxdb_token = "my-super-secret-auth-token"
influxdb_org = "myorg"
influxdb_bucket = "bicycle_counts"

# Set up InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org, debug=True)

def get_latest_count():
    query = f'''
    from(bucket:"{influxdb_bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "bicycle_count")
        |> last()
    '''
    try:
        result = client.query_api().query(query=query)
        if result and len(result) > 0 and len(result[0].records) > 0:
            return result[0].records[0].values["_value"]
    except Exception as e:
        st.error(f"Error querying InfluxDB: {str(e)}")
        st.error(f"InfluxDB URL: {influxdb_url}")
        st.error(f"InfluxDB Org: {influxdb_org}")
        st.error(f"InfluxDB Bucket: {influxdb_bucket}")
        # Don't display the token for security reasons
        st.error("Please check your InfluxDB token")
    return 0

def get_historical_data():
    query = f'''
    from(bucket:"{influxdb_bucket}")
        |> range(start: -5m)
        |> filter(fn: (r) => r._measurement == "bicycle_count")
    '''
    try:
        result = client.query_api().query_data_frame(query=query)
        if not result.empty:
            result['_time'] = pd.to_datetime(result['_time'])
            print(" Historical data: ", result[['_time', '_value' , 'publisher_id']])
            return result[['_time', '_value' , 'publisher_id']]
    except Exception as e:
        st.error(f"Error querying InfluxDB: {str(e)}")
    print(" Historical data: ", result[['_time', '_value' , 'publisher_id']])
    return pd.DataFrame(columns=['_time', '_value', 'publisher_id'])

st.title("Real-time Bicycle Count")

# Display the latest count
latest_count = get_latest_count()
st.metric("Current Bicycle Count", latest_count)

# Create and display the graph
historical_data = get_historical_data()

if not historical_data.empty:
    fig = go.Figure()

    # Display different publishers with different colors
    for publisher_id in historical_data['publisher_id'].unique():
        publisher_data = historical_data[historical_data['publisher_id'] == publisher_id]
        fig.add_trace(go.Scatter(
            x=publisher_data['_time'], 
            y=publisher_data['_value'], 
            mode='lines+markers', 
            name=f"Publisher: {publisher_id}"
        ))

    fig.update_layout(title="Bicycle Count Over Time", xaxis_title="Time", yaxis_title="Count")
    st.plotly_chart(fig)
else:
    st.warning("No historical data available")

# Display debug information
st.subheader("Debug Information")
st.write(f"InfluxDB URL: {influxdb_url}")
st.write(f"InfluxDB Org: {influxdb_org}")
st.write(f"InfluxDB Bucket: {influxdb_bucket}")
st.write("Please check your InfluxDB token")

# Auto-refresh the app every 5 seconds
st.empty()
st.experimental_rerun()