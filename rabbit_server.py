import pika

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'  # Or the IP of the RabbitMQ server
rabbitmq_queue = 'image_queue'

# Set up the connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=rabbitmq_queue)

last_file_number = 1

# Callback function to handle image data
def callback(ch, method, properties, body):
    global last_file_number

    with open(f"output/output_{last_file_number:03}.jpg", 'wb') as img_file:
        img_file.write(body)
    print(f"Image received and saved as 'output_{last_file_number:03}.jpg'")

    last_file_number += 1

# Start consuming the image data
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

print("Waiting for image...")
channel.start_consuming()
