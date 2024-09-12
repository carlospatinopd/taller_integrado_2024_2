import paho.mqtt.client as mqtt
import time
import random

if __name__ == "__main__":
    # Define the IP address of the broker
    Ip = "192.168.0.102"
    # Create a client
    client = mqtt.Client()
    # Connect to the broker
    client.connect(Ip, 1883, 100)

    try:
        while True:
            # Generate a random temperature between 20 and 30 degrees Celsius
            temperature = random.uniform(20.0, 30.0)
            presion=random.uniform(1.0,2.0)
            # Format the temperature to two decimal places
            message = f"{temperature:.2f}"
            message2= f"{presion:.2f}"
            # Publish the temperature data to the topic
            client.publish("datossenor/temperatura", message)
            time.sleep(0.5)
            client.publish("datossenor/humedad",presion)
            # Sleep for a second before sending the next temperature reading
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Gracefully exit on interrupt
        print("Stopping temperature data transmission.")
        client.publish("datossenor/temperatura", "quit")
        client.disconnect()
