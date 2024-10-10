import streamlit as st
import plotly.graph_objs as go
from influxdb_client import InfluxDBClient
import pandas as pd
import time 

# InfluxDB connection parameters
influxdb_url = "http://localhost:8086"
influxdb_token = "my-super-secret-auth-token"
influxdb_org = "myorg"
influxdb_bucket = "bicycle_counts"

# Set up InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org, debug=True)

def get_latest_count_by_publisher():
    query = f'''
    from(bucket:"{influxdb_bucket}")
        |> range(start: -5m)
        |> filter(fn: (r) => r._measurement == "bicycle_count")
        |> group(columns: ["publisher_id"])
        |> last()
    '''
    try:
        result = client.query_api().query(query=query)
        latest_counts = {}
        if result and len(result) > 0:
            for table in result:
                for record in table.records:
                    publisher_id = record.values['publisher_id']
                    latest_counts[publisher_id] = record.values["_value"]
        return latest_counts
    except Exception as e:
        st.error(f"Error querying InfluxDB: {str(e)}")
        return {}

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
            return result[['_time', '_value', 'publisher_id']]
    except Exception as e:
        st.error(f"Error querying InfluxDB: {str(e)}")
    return pd.DataFrame(columns=['_time', '_value', 'publisher_id'])

st.title("Real-time Bicycle Count by Publisher")

# Fetch the latest count by publisher_id
latest_counts = get_latest_count_by_publisher()

# Get historical data
historical_data = get_historical_data()

# Combine both current data and graphs
if latest_counts and not historical_data.empty:
    # Get unique publisher_ids from historical data
    publisher_ids = historical_data['publisher_id'].unique()

    # Display the current data and graph for each publisher_id
    for publisher_id in publisher_ids:
        # Filter historical data for the current publisher_id
        publisher_data = historical_data[historical_data['publisher_id'] == publisher_id]
        
        # Create a layout with two columns: one for current data and one for the graph
        col1, col2 = st.columns(2)

        # Display current count in the first column
        if publisher_id in latest_counts:
            col1.metric(f"Current Bicycle Count (Publisher ID: {publisher_id})", latest_counts[publisher_id])
        else:
            col1.warning(f"No current data available for Publisher ID {publisher_id}")

        # Create the graph for the current publisher in the second column
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=publisher_data['_time'], y=publisher_data['_value'], mode='lines+markers'))
        fig.update_layout(title=f"Bicycle Count Over Time (Publisher ID: {publisher_id})", 
                          xaxis_title="Time", yaxis_title="Count")
        col2.plotly_chart(fig)

else:
    st.warning("No data available for the publishers.")

# Display debug information
st.subheader("Debug Information")
st.write(f"InfluxDB URL: {influxdb_url}")
st.write(f"InfluxDB Org: {influxdb_org}")
st.write(f"InfluxDB Bucket: {influxdb_bucket}")
st.write("Please check your InfluxDB token")

# Auto-refresh the app every 5 seconds
# st.empty()
while True:
    time.sleep(1)
    st.experimental_rerun()
