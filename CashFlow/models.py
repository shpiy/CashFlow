from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    type: str

    expenses: List['Expense'] = Relationship(back_populates='category')
    earnings: List['Earning'] = Relationship(back_populates='category')
    budgets: List['Budget'] = Relationship(back_populates='category')


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now())
    amount: float
    description: Optional[str] = None

    category_id: Optional[int] = Field(default=0, foreign_key='category.id')
    category: Optional['Category'] = Relationship(back_populates='expenses')


class Earning(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now())
    amount: float
    description: Optional[str] = None
    
    category_id: Optional[int] = Field(default=1024, foreign_key='category.id')
    category: Optional['Category'] = Relationship(back_populates='expenses')

    budgets: List['Budget'] = Relationship(back_populates='category')


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    allocated_amount: float
    month_year: datetime = Field(index=True)

    category_id: int = Field(foreign_key='category.id')
    category: 'Category' = Relationship(back_populates='budgets')