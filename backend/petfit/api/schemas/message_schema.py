from pydantic import BaseModel


class MessageOutput(BaseModel):
    message: str