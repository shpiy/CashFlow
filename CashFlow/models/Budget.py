from sqlmodel import Field, Relationship, SQLModel
from typing import Optional 
from datetime import date

from CashFlow.models.Category import Category

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    allocated_amount: float
    month_year: date = Field(index=True)

    category_id: int = Field(foreign_key='category.id')
    category: 'Category' = Relationship(back_populates='budgets')