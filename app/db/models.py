from datetime import date
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Date, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base_model import BaseModel


class AccountType(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    SAVINGS = "savings"
    CREDIT = "credit"


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")


class Account(BaseModel):
    __tablename__ = "accounts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(SAEnum(AccountType), nullable=False)
    balance = Column(Numeric(12, 2), default=0, nullable=False)
    currency = Column(String(10), default="UAH", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Category(BaseModel):
    __tablename__ = "categories"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    type = Column(SAEnum(CategoryType), nullable=False)
    icon = Column(String, nullable=True)
    color = Column(String(7), nullable=True)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transaction(BaseModel):
    __tablename__ = "transactions"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.uuid", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.uuid", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(SAEnum(TransactionType), nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, default=date.today, nullable=False)

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Budget(BaseModel):
    __tablename__ = "budgets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.uuid", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    limit_amount = Column(Numeric(12, 2), nullable=False)

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


class Goal(BaseModel):
    __tablename__ = "goals"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0, nullable=False)
    deadline = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="goals")
