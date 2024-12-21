import base64
from cryptography.fernet import Fernet
import paho.mqtt.client as mqtt


class Chat:
    def __init__(self, passphrase: str, mqtt_broker: str, mqtt_port: int = 8883, topic: str = "chat"):
        self.key = base64.urlsafe_b64encode(bytes(passphrase.ljust(32)[:32], 'utf-8'))
        self.cipher = Fernet(self.key)

        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.topic = topic

        self.client = mqtt.Client()
        self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=120)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, return_code):
        print("Connected to MQTT-broker with code:", return_code)
        client.subscribe(self.topic)

    def on_message(self, msg):
        try:
            decrypted_message = self.cipher.decrypt(msg.payload).decode()
            print(f"Recieved: {decrypted_message}")
        except Exception as e:
            print("Error decrypting:", e)

    def send_message(self, message: str):
        try:
            encrypted_message = self.cipher.encrypt(message.encode())
            self.client.publish(self.topic, encrypted_message)
            print(f"Sent: {message}")
        except Exception as e:
            print("Error when encrypting:", e)

    def run(self):
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.client.loop_start()
        print("Chat client started.")

        try:
            while True:
                message = input("You: ")
                self.send_message(message)
        except KeyboardInterrupt:
            print("Ending...")
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    chat = Chat("password12345", "test.mosquitto.org")
    chat.run()
