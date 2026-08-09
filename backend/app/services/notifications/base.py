from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        raise NotImplementedError