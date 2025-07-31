import logging

from sqlmodel import select, Field, Relationship, SQLModel
from typing import Optional, List
from datetime import datetime, date

from CashFlow.database import get_session

from CashFlow.models.Category import Category, get_category_by_id

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Earning(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_date: date = Field(default_factory=datetime.date)
    amount: float
    description = Optional[str] = None

    category_id: int = Field(foreign_key='category.id', index=True)
    category: Optional['Category'] = Relationship(back_populates='earnings')

def create_earning(transaction_date: date, amount: float, category_id: int, description: Optional[str] = None) -> Optional[int]:
    with get_session() as sess:
        try:
            category = get_category_by_id(category_id=category_id)

            if not category:
                logger.warning(f'Failed to create earning: Category with ID {category_id} not found in database.')
                return None
            if category.type.lower() != 'earning':
                logger.warning(f'Failed to create earning : Category \'{category.name}\' (ID: {category_id}) is of type \'{category.type}\', expected \'earning\'.')
                return None
            
            earning = Earning(transaction_date=transaction_date, amount=amount, description=description, category_id=category_id)
            
            sess.add(earning)
            sess.commit()
            sess.refresh(earning)

            logger.info(f'Successfully created earning \'{description if description else "No description"}\' with ID: {earning.id} for amount {earning.amount} in category \'{category.name}\'.')
            return earning.id
        except Exception as err:
            logger.error(f'Failed to create earning: {err}', exc_info=True)
            return None

def get_earning_by_id(earning_id: int) -> Optional[Earning]:
    with get_session() as sess:
        try:
            statement = select(Earning).where(Earning.id == earning_id)
            earning = sess.exec(statement).first()

            if earning :
                logger.debug(f'Successfully retrieved earning with ID {earning_id}: Amount={earning.amount}, Category ID={earning.category_id}')
            else:
                logger.warning(f'Earning with ID {earning_id} not found in database.')
            
            return earning 
        except Exception as err:
            logger.error(f'Database error while retrieving earning with ID {earning_id}: {err}', exc_info=True)
            return None

def get_earning_by_category(category_id: int) -> List[Earning]:
    with get_session() as sess:
        try:
            category = get_category_by_id(category_id=category_id)

            if not category:
                logger.warning(f'Failed to retrieve earnings: Category with ID {category_id} not found in database.')
                return []
            
            statement = select(Earning).where(Earning.category_id == category_id)
            earnings = sess.exec(statement).all()

            logger.debug(f'Successfully retrieved {len(earnings)} earnings for category \'{category.name}\' (ID: {category_id}).')
            return earnings 
        except Exception as err:
            logger.error(f'Database error while retrieving earnings for category with ID {category_id}: {err}', exc_info=True)
            return []

def get_earnings_by_range(start_date: date, end_date: date) -> List[Earning]:
    with get_session() as sess:
        try:
            statement = select(Earning).where(
                Earning.transaction_date >= start_date,
                Earning.transaction_date <= end_date
            )
            earnings = sess.exec(statement).all()

            logger.debug(f'Successfully retrieved {len(earnings)} earnings between {start_date} and {end_date}.')
            return earnings
        except Exception as err:
            logger.error(f'Database error while retrieving earnings between {start_date} and {end_date}: {err}', exc_info=True)
            return []

# TO-DO: Add a function 'get_all_earnings'

def update_earning(earning_id: int,
                   new_transaction_date: Optional[date] = None,
                   new_amount: Optional[float] = None,
                   new_category_id: Optional[int] = None,
                   new_description: Optional[str] = None) -> Optional[Earning]:
    with get_session() as sess:
        try:
            earning = sess.get(Earning, earning_id)

            if not earning:
                logger.warning(f'Failed to update earning: Earning with ID {earning_id} not found in database.')
                return None

            original_transaction_date = earning.transaction_date
            original_amount = earning.amount
            original_description = earning.description
            original_category_id = earning.category_id

            if new_transaction_date is not None:
                earning.transaction_date = new_transaction_date
            if new_amount is not None:
                earning.amount = new_amount
            if new_description is not None:
                earning.description = new_description

            if new_category_id is not None and new_category_id != original_category_id:
                category = get_category_by_id(category_id=new_category_id)
                if not category:
                    logger.warning(f'Failed to update earning ID {earning_id}: New category with ID {new_category_id} not found.')
                    return None
                elif category.type.lower() != 'earning':
                    logger.warning(f'Failed to update earning ID {earning_id}: New category \'{category.name}\' (ID: {new_category_id}) is of type \'{category.type}\', expected \'earning\'.')
                    return None
                
                earning.category_id = new_category_id

            sess.add(earning)
            sess.commit()
            sess.refresh(earning)

            logger.info(f'Successfully updated earning ID {earning_id}. '
                        f'Changes: date from \'{original_transaction_date}\' to \'{earning.transaction_date}\', '
                        f'amount from \'{original_amount}\' to \'{earning.amount}\', '
                        f'description from \'{original_description}\' to \'{earning.description}\', '
                        f'category ID from \'{original_category_id}\' to \'{earning.category_id}\'.')
            return earning 
        except Exception as err:
            logger.error(f'Failed to update earning with ID {earning_id}: {err}', exc_info=True)
            return None

def delete_earning(earning_id: int) -> bool:
    with get_session() as sess:
        try:
            earning = sess.get(Earning, earning_id)

            if earning:
                earning_description = earning.description if earning.description else 'No description'
                sess.delete(earning)
                sess.commit()
            
                logger.info(f'Successfully deleted earning \'{earning_description}\' with ID {earning_id}.')
                return True
            else:
                logger.warning(f'Failed to delete earning: Earning with ID {earning_id} not found in database.')
                return False
        except Exception as err:
            logger.error(f'Failed to delete earning with ID {earning_id}: {err}', exc_info=True)
            return False