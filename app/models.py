from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Float, default=100.0)
    inventory: Mapped["Inventory"] = relationship(back_populates="player", uselist=False)
    wallet_transactions: Mapped[list["WalletTransaction"]] = relationship(back_populates="player")


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), unique=True, index=True)
    seeds: Mapped[int] = mapped_column(Integer, default=10)
    water: Mapped[int] = mapped_column(Integer, default=5)
    fertilizer: Mapped[int] = mapped_column(Integer, default=3)
    player: Mapped[Player] = relationship(back_populates="inventory")
    items: Mapped[list["InventoryItem"]] = relationship(back_populates="inventory", cascade="all, delete-orphan")


class ItemCatalog(Base):
    __tablename__ = "item_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, index=True)
    inventory_items: Mapped[list["InventoryItem"]] = relationship(back_populates="item")


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("inventory_id", "item_id", name="uq_inventory_item"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventories.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item_catalog.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    inventory: Mapped[Inventory] = relationship(back_populates="items")
    item: Mapped[ItemCatalog] = relationship(back_populates="inventory_items")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    transaction_type: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    player: Mapped[Player] = relationship(back_populates="wallet_transactions")
