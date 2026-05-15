from abc import ABC, abstractmethod
import logging

class Publisher(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def publish(self, content: str, image_path: str = None) -> str:
        """
        Publishes the content to the platform.
        Returns the URL of the published post, or a success message.
        """
        pass
