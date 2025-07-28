from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime, date

from CashFlow.models.Category import Category

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_date: date = Field(default_factory=datetime.date())
    amount: float
    description = Optional[str] = None

    category_id: Optional[int] = Field(default=0, foreign_key='category.id')
    category: Optional['Category'] = Relationship(back_populates='expenses')