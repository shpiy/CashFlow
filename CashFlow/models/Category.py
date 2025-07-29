import logging

from sqlmodel import select, Field, Relationship, SQLModel
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from CashFlow.database import get_session

from CashFlow.models.Expense import Expense
from CashFlow.models.Earning import Earning 
from CashFlow.models.Budget import Budget

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    type: str

    expenses: List['Expense'] = Relationship(back_populates='category')
    earnings: List['Earning'] = Relationship(back_populates='category')
    budgets: List['Budget'] = Relationship(back_populates='category')


def create_category(category_name: str, category_type: str) -> Optional[int]:
    with get_session() as sess:
        try:
            category = Category(name=category_name, type=category_type)

            sess.add(category)
            sess.commit()
            sess.refresh(category)

            logger.info(f'Successfully created category \'{category_name}\' of type \'{category_type}\' with ID: {category.id}')
            return category.id
        except IntegrityError as err:
            logger.warning(f'Failed to create category \'{category_name}\'. A category with that name already exists. Error: {err}')
            return None
        except Exception as err:
            logger.error(f'Failed to create category \'{category_name}\' of type \'{category_type}\': {err}', exc_info=True)
            return None

def get_category_by_name(category_name: str) -> Optional[Category]:
    with get_session() as sess:
        try:
            statement = select(Category).where(Category.name == category_name)
            category = sess.exec(statement).first()

            if category:
                logger.debug(f'Successfully retrieved category \'{category_name}\' with ID: {category.id}')
            else:
                logger.warning(f'Category \'{category_name}\' not found in database')
            
            return category
        except Exception as err:
            logger.error(f'Database error while retrieving category \'{category_name}\': {err}', exc_info=True)
            return None

def get_category_by_id(category_id: int) -> Optional[Category]:
    with get_session() as sess:
        try:
            statement = select(Category).where(Category.id == category_id)
            category = sess.exec(statement).first()
        
            if category:
                logger.debug(f'Successfully retrieved category with ID {category_id}: \'{category.name}\'')
            else:
                logger.warning(f'Category with ID {category_id} not found in database')
            
            return category
        except Exception as err:
            logger.error(f'Database error while retrieving category with ID {category_id}: {err}', exc_info=True)
            return None

def get_all_categories() -> List[Category]:
    with get_session() as sess:
        try:
            statement = select(Category)
            categories = sess.exec(statement).all()
        
            logger.debug(f'Successfully retrieved {len(categories)} categories from database')
            return categories
        except Exception as err:
            logger.error(f'Database error while retrieving all categories: {err}', exc_info=True)
            return []

def get_categories_by_type(category_type: str) -> List[Category]:
    with get_session() as sess:
        try:
            statement = select(Category).where(Category.type == category_type)
            categories = sess.exec(statement).all()
        
            logger.debug(f'Successfully retrieved {len(categories)} categories of type \'{category_type}\'')
            return categories
        except Exception as err:
            logger.error(f'Database error while retrieving categories of type \'{category_type}\': {err}', exc_info=True)
            return []

def update_category(category_id: int, new_name: Optional[str] = None, new_type: Optional[str] = None) -> Optional[Category]:
    with get_session() as sess:
        try:
            category = sess.get(Category, category_id)
            
            if not category:
                logger.warning(f'Cannot update category: Category with ID {category_id} not found in database')
                return None
            
            original_name = category.name
            original_type = category.type
            
            if new_name is not None:
                category.name = new_name
            if new_type is not None:
                category.type = new_type

            sess.add(category)
            sess.commit()
            sess.refresh(category)

            logger.info(f'Successfully updated category ID {category_id}: '
                        f'name changed from \'{original_name}\' to \'{category.name}\', '
                        f'type changed from \'{original_type}\' to \'{category.type}\'')
            return category
        except IntegrityError as err:
            logger.warning(f'Failed to update category \'{original_name}\' to \'{new_name}\'. A category with that name already exists. Error: {err}')
            return None
        except Exception as err:
            logger.error(f'Failed to update category with ID {category_id}: {err}', exc_info=True)
            return None

def delete_category(category_id: int) -> bool:
    with get_session() as sess:
        try:
            category = sess.get(Category, category_id)
            
            if category:
                category_name = category.name
                sess.delete(category)
                sess.commit()

                logger.info(f'Successfully deleted category \'{category_name}\' with ID {category_id}')
                return True
            else:
                logger.warning(f'Cannot delete category: Category with ID {category_id} not found in database')
                return False
        except Exception as err:
            logger.error(f'Failed to delete category with ID {category_id}: {err}', exc_info=True)
            return False