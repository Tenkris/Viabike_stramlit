# RabbitMQ Bicycle Counter with InfluxDB and Streamlit

This project implements a system that counts bicycles in images received from a RabbitMQ queue, stores the counts in InfluxDB, and displays real-time statistics using a Streamlit dashboard.

## Features

- Subscribes to a RabbitMQ queue for image data
- Uses YOLOv5 for bicycle detection in images
- Stores bicycle counts in InfluxDB time series database
- Displays real-time bicycle count statistics with Streamlit

## Prerequisites

- Docker and Docker Compose
- Python 3.7+
- CUDA-capable GPU (recommended for faster inference)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/rabbitmq-bicycle-counter.git
   cd rabbitmq-bicycle-counter
   ```

2. Set up a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Start the RabbitMQ and InfluxDB services using Docker Compose:

   ```
   docker-compose up -d
   ```

2. Open `bicycle_counter.py` and update the following variables if necessary:

   - `rabbitmq_host`
   - `influxdb_url`
   - `influxdb_token`
   - `influxdb_org`
   - `influxdb_bucket`

3. Open `streamlit_app.py` and update the InfluxDB connection parameters if necessary.

## Usage

1. Run the bicycle counter script:

   ```
   python rabbit_server.py
   ```

2. In a separate terminal, run the Streamlit app:

   ```
   streamlit run streamlit-main.py
   ```

3. Open a web browser and navigate to the URL provided by Streamlit (typically `http://localhost:8501`) to view the real-time dashboard.

## Project Structure

- `bicycle_counter.py`: Main script for consuming images from RabbitMQ, counting bicycles, and storing data in InfluxDB
- `streamlit_app.py`: Streamlit app for displaying real-time bicycle count statistics
- `docker-compose.yml`: Docker Compose file for setting up RabbitMQ and InfluxDB services
- `requirements.txt`: List of Python dependencies
- `README.md`: This file

## Troubleshooting

- Ensure that Docker and Docker Compose are installed and running correctly
- Check that RabbitMQ and InfluxDB services are up and accessible
- Verify that the RabbitMQ queue exists and is receiving image messages
- If you encounter any package-related issues, make sure you're running the scripts within the activated virtual environment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
