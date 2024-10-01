import pika
import cv2
import numpy as np
import torch
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'  # Or the IP of the RabbitMQ server
rabbitmq_queue = 'image_queue'

# InfluxDB connection parameters
influxdb_url = "http://localhost:8086"
influxdb_token = "my-super-secret-auth-token"
influxdb_org = "myorg"
influxdb_bucket = "bicycle_counts"

# Set up the connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
channel = connection.channel()

output_dir = './output'
os.makedirs(output_dir, exist_ok=True)

# Declare the queue
channel.queue_declare(queue=rabbitmq_queue)

# Set up InfluxDB client
influx_client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def count_bicycles(image):
    results = model(image)
    bicycle_results = results.pandas().xyxy[0][results.pandas().xyxy[0]['class'] == 1]
    return len(bicycle_results)

def save_to_influxdb(count , publisher_id):
    point = Point("bicycle_count").field("count", count).tag("publisher_id", publisher_id )
    write_api.write(bucket=influxdb_bucket, record=point)

def log_image(image, count):
    timestamp = int(time.time())
    filename = f"{output_dir}/image_{timestamp}_{count}_bicycles.jpg"
    cv2.imwrite(filename, image)
    print(f"Image saved: {filename}")

# Callback function to handle image data
def callback(ch, method, properties, body):
    # Convert bytes to numpy array
    nparr = np.frombuffer(body, np.uint8)
    
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Count bicycles
    bicycle_count = count_bicycles(image)
    publisher_id = properties.headers.get('publisher_id', 'Unknown')
    print(f"Publisher ID: {publisher_id}")
    
    print(f"Number of bicycles detected: {bicycle_count}")
    
    # Save count to InfluxDB
    save_to_influxdb(bicycle_count , publisher_id)
    
    log_image(image, bicycle_count)

# Start consuming the image data
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

print("Waiting for images. To exit press CTRL+C")
channel.start_consuming()