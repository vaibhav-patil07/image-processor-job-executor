from typing import Dict
import json

class ImageJob():
    data: Dict[str, str]
    def __init__(self, data: Dict[str, str]):
        self.data = data
        self.data['message'] = json.loads(data['message'])
    def getPattern(self) -> str:
        return self.data['pattern']
    def getMessage(self) -> str:
        return self.data['message']
    def getImageId(self) -> str:
        message = self.getMessage()
        imageId = message['image_id']
        return imageId
    def getImageName(self) -> str:
        message = self.getMessage()
        imageName = message['filename']
        return imageName
    def getUserId(self) -> str:
        message = self.getMessage()
        userId = message['user_id']
        return userId
    def getMessageId(self) -> str:
        message = self.getMessage()
        messageId = message['message_id']
        return messageId