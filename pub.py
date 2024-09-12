# First, import the Paho MQTT package.
import paho.mqtt.client as mqtt
import time
# Also, import time for adding a timed delay.


if __name__ == "__main__":
    # Next, define an Id for the client to use.
    # And define the Ip address of the broker.
    Ip = "192.168.0.101"
    # Then, create a client.
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    # Connect to the broker.
    client.connect(Ip, 1883, 100)
    # Next, begin a loop that will countdown from 10.
    for i in range(10, 0, -1):
        # Before sending a message, format the message with the remaining time.
        message = F"conteo {i}"
        # Now, publish the message to the consumer's in topic.
        client.publish("datossenor/Humedad", i)
        # Then, sleep for one second to satisfy the countdown timer.
        time.sleep(1)
    
    # Finally, after counting down, send the quit signal to any listeners.
    client.publish("datossenor/temperatura", "quit")