from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

from CashFlow.models.Expense import Expense
from CashFlow.models.Earning import Earning 
from CashFlow.models.Budget import Budget

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    type: str

    expenses: List['Expense'] = Relationship(back_populates='category')
    earnings: List['Earning'] = Relationship(back_populates='category')
    budgets: List['Budget'] = Relationship(back_populates='category')