import paho.mqtt.client as paho
import random
import threading
import queue


CLIENT_ID = f'kyh-mqtt-{random.randint(0, 1000)}'
USERNAME = 'Mohamad'
PASSWORD = ''
BROKER = 'broker.hivemq.com'
PORT = 1883

"""
TODO: Skapa en dictionary: namn på chat-rum som mappar till en topic
Ex: python -> kyhchat/group1/python
Skapa tre olika chat-rum
"""
CHAT_ROOMS = {
    "Room1": "chat/room1",
    "Room2": "chat/room2",
    "Room3": "chat/room3",


}


class Chat:
    def __init__(self, username, room):
        self.username = username
        self.room = room
        self.topic = CHAT_ROOMS[room]
        self.client = None
        self.connect_mqtt()
        self.input_queue = queue.Queue()
        # This variable is used to exit the thread when the
        # user exits the application
        self.running = True

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected to Chat Server. Type "quit" to quit.')
        else:
            print(f'Error connecting to Chat Server. Error code {rc}')

    def connect_mqtt(self):
        # Create a MQTT client object.
        # Every client has an id
        self.client = paho.Client(CLIENT_ID)
        # Set username and password to connect to broker
        self.client.username_pw_set(USERNAME, PASSWORD)

        # When connection response is received from broker
        # call the function on_connect
        self.client.on_connect = self.on_connect

        # Connect to broker
        self.client.connect(BROKER, PORT)

    def on_message(self, client, userdata, message):
        """
        TODO: Implementera: När vi tar emot ett meddelande.
        Avkoda meddelandet (message) och skriv ut det.
        Skriv bara ut meddelandet om det börjar med någon annans användarnamn
        (Dvs. Skriv inte ut meddelanden du själv skickat)
        """

        if self.username != "Mohamad":
            print(f"Topic: {message.topic}, Message: {message.payload.decode('utf-8')}")

    def init_client(self):
        # Subscribe to selected topic
        self.client.subscribe(self.topic)
        # Set the on_message callback function
        self.client.on_message = self.on_message

        def get_input():
            """
            Function used by the input thread
            :return: None
            """
            while self.running:
                # Get user input and place it in the input_queue
                self.input_queue.put(input())

        # Create input thread
        input_thread = threading.Thread(target=get_input)
        # and start it
        input_thread.start()

        # Start the paho client loop
        self.client.loop_start()

        """
        TODO: Implementera: Skicka ett meddelande till chat-rummet att användaren har anslutit!
        Ex: Andreas has joined the chat
        """
        self.client.publish(self.topic, f'<{self.username}> has joined the chatroom.')

    def run(self):
        self.init_client()

        while True:
            try:
                # Check if there is an input from the user
                # If not we will get a queue.Empty exception
                msg_to_send = self.input_queue.get_nowait()
                # If we reach this point we have a message

                # Check if the user wants to exit the application
                if msg_to_send.lower() == "quit":
                    self.client.publish(self.topic, f'<{self.username}> has left the chatroom.')
                    # Indicate to the input thread that it can exit
                    self.running = False
                    break

                self.client.publish(self.topic, f'<{self.username}> {msg_to_send}.')

            except queue.Empty:  # We will end up here if there was no user input
                pass  # No user input, do nothing

        # Stop the paho loop
        self.client.loop_stop()
        # The user needs to press ENTER to exit the while loop in the thread
        print("You have left the chat. Press [ENTER] to exit application.")


def main():
    # Init application. Ask for username and chat room
    username = input("Enter your username: ")

    print("Pick a room:")
    for room in CHAT_ROOMS:
        print(f"\t{room}")
    room = input("> ")

    chat = Chat(username, room)
    chat.run()


if __name__ == '__main__':
    main()
