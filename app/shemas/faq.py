from pydantic import BaseModel, field_validator

class FaqCreate(BaseModel):

    question: str
    keywords: list[str]
    answer: str

    def to_list(self) -> list:
        return [self.question, self.keywords, self.answer]

    @field_validator("question")
    def question_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("question can't be empty")

        return v

    @field_validator("keywords")
    def keywords_not_empty(cls, v: str) -> str:

        if not v:
            raise ValueError("keywords can't be empty")

        return v

    @field_validator("answer")
    def answer_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("answer can't be empty")

        return v

class FaqList(BaseModel):
    item: list[FaqCreate]

    def __iter__(self):
        return iter(self.item)
