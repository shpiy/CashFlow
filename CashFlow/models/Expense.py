import logging

from sqlmodel import select, Field, Relationship, SQLModel
from typing import Optional, List
from datetime import datetime, date

from CashFlow.database import get_session

from CashFlow.models.Category import Category, get_category_by_id

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_date: date = Field(default_factory=datetime.date)
    amount: float
    description = Optional[str] = None

    category_id: Optional[int] = Field(foreign_key='category.id')
    category: Optional['Category'] = Relationship(back_populates='expenses')

def create_expense(transaction_date: date, amount: float, category_id: int, description: Optional[str] = None) -> Optional[int]:
    with get_session() as sess:
        try:
            category = get_category_by_id(category_id=category_id)

            if not category:
                logger.warning(f'Failed to create expense: Category with ID {category_id} not found in database.')
                return None
            if category.type.lower() != 'expense':
                logger.warning(f'Failed to create expense: Category \'{category.name}\' (ID: {category_id}) is of type \'{category.type}\', expected \'expense\'.')
                return None
            
            expense = Expense(transaction_date=transaction_date, amount=amount, description=description, category_id=category_id)
            
            sess.add(expense)
            sess.commit()
            sess.refresh(expense)

            logger.info(f'Successfully created expense \'{description if description else "No description"}\' with ID: {expense.id} for amount {expense.amount} in category \'{category.name}\'.')
            return expense.id
        except Exception as err:
            logger.error(f'Failed to create expense: {err}', exc_info=True)
            return None
    
def get_expense_by_id(expense_id: int) -> Optional[Expense]:
    with get_session() as sess:
        try:
            statement = select(Expense).where(Expense.id == expense_id)
            expense = sess.exec(statement).first()

            if expense:
                logger.debug(f'Successfully retrieved expense with ID {expense_id}: Amount={expense.amount}, Category ID={expense.category_id}')
            else:
                logger.warning(f'Expense with ID {expense_id} not found in database.')
            
            return expense
        except Exception as err:
            logger.error(f'Database error while retrieving expense with ID {expense_id}: {err}', exc_info=True)
            return None

def get_expenses_by_category(category_id: int) -> List[Expense]:
    with get_session() as sess:
        try:
            category = get_category_by_id(category_id=category_id)

            if not category:
                logger.warning(f'Failed to retrieve expenses: Category with ID {category_id} not found in database.')
                return []
            
            statement = select(Expense).where(Expense.category_id == category_id)
            expenses = sess.exec(statement).all()

            logger.debug(f'Successfully retrieved {len(expenses)} expenses for category \'{category.name}\' (ID: {category_id}).')
            return expenses
        except Exception as err:
            logger.error(f'Database error while retrieving expenses for category with ID {category_id}: {err}', exc_info=True)
            return []

def get_expenses_by_range(start_date: date, end_date: date) -> List[Expense]:
    with get_session() as sess:
        try:
            statement = select(Expense).where(
                Expense.transaction_date >= start_date,
                Expense.transaction_date <= end_date
            )
            expenses = sess.exec(statement).all()

            logger.debug(f'Successfully retrieved {len(expenses)} expenses between {start_date} and {end_date}.')
            return expenses
        except Exception as err:
            logger.error(f'Database error while retrieving expenses between {start_date} and {end_date}: {err}', exc_info=True)
            return []

def update_expense(expense_id: int,
                   new_transaction_date: Optional[date] = None,
                   new_amount: Optional[float] = None,
                   new_category_id: Optional[int] = None,
                   new_description: Optional[str] = None) -> Optional[Expense]:
    with get_session() as sess:
        try:
            expense = sess.get(Expense, expense_id)

            if not expense:
                logger.warning(f'Failed to update expense: Expense with ID {expense_id} not found in database.')
                return None

            original_transaction_date = expense.transaction_date
            original_amount = expense.amount
            original_description = expense.description
            original_category_id = expense.category_id

            if new_transaction_date is not None:
                expense.transaction_date = new_transaction_date
            if new_amount is not None:
                expense.amount = new_amount
            if new_description is not None:
                expense.description = new_description

            if new_category_id is not None and new_category_id != original_category_id:
                category = get_category_by_id(category_id=new_category_id)
                if not category:
                    logger.warning(f'Failed to update expense ID {expense_id}: New category with ID {new_category_id} not found.')
                    return None
                elif category.type.lower() != 'expense':
                    logger.warning(f'Failed to update expense ID {expense_id}: New category \'{category.name}\' (ID: {new_category_id}) is of type \'{category.type}\', expected \'expense\'.')
                    return None
                
                expense.category_id = new_category_id

            sess.add(expense)
            sess.commit()
            sess.refresh(expense)

            logger.info(f'Successfully updated expense ID {expense_id}. '
                        f'Changes: date from \'{original_transaction_date}\' to \'{expense.transaction_date}\', '
                        f'amount from \'{original_amount}\' to \'{expense.amount}\', '
                        f'description from \'{original_description}\' to \'{expense.description}\', '
                        f'category ID from \'{original_category_id}\' to \'{expense.category_id}\'.')
            return expense
        except Exception as err:
            logger.error(f'Failed to update expense with ID {expense_id}: {err}', exc_info=True)
            return None

def delete_expense(expense_id: int) -> bool:
    with get_session() as sess:
        try: 
            expense = sess.get(Expense, expense_id)

            if expense:
                expense_description = expense.description if expense.description else 'No description'
                sess.delete(expense)
                sess.commit()
            
                logger.info(f'Successfully deleted expense \'{expense_description}\' with ID {expense_id}.')
                return True
            else:
                logger.warning(f'Failed to delete expense: Expense with ID {expense_id} not found in database.')
                return False
        except Exception as err:
            logger.error(f'Failed to delete expense with ID {expense_id}: {err}', exc_info=True)
            return False