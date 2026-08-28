from pydantic import BaseModel, field_validator

class FaqCreate(BaseModel):

    question: str
    keywords: list[str]
    answer: str

    def to_list(self) -> list:
        return [self.question, self.keywords, self.answer]

    @field_validator("question")
    def question_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("question can't be empty")

        return v

    @field_validator("answer")
    def answer_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("answer can't be empty")

        return v

class FaqList(BaseModel):
    item: list[FaqCreate]

    def __iter__(self):
        return iter(self.item)
