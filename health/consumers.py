from channels.generic.websocket import WebsocketConsumer
import json

class LabAnalysisConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "lab_updates"

    def connect(self):
        print("Connection attempt")
        self.accept()
        print("Connection accepted")

    def disconnect(self, close_code):
        print(f"Disconnected: {close_code}")
        pass

    def receive(self, text_data):
        print(f"Received data: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            self.send(text_data=json.dumps({
                'type': 'lab_update',
                'data': text_data_json
            }))
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
