from datetime import datetime

from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    username: str
    password: str


class PlayerLogin(BaseModel):
    username: str
    password: str


class WalletDepositRequest(BaseModel):
    amount: float = Field(gt=0)


class WalletTransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryAddItemRequest(BaseModel):
    item_code: str
    quantity: int = Field(gt=0)


class InventoryItemResponse(BaseModel):
    code: str
    name: str
    category: str
    quantity: int


class InventoryCategoryResponse(BaseModel):
    category: str
    items: list[InventoryItemResponse]


class InventoryResponse(BaseModel):
    id: int
    player_id: int
    capacity_limit: int
    total_quantity: int
    categories: list[InventoryCategoryResponse]


class PlayerResponse(BaseModel):
    id: int
    username: str
    balance: float

    class Config:
        from_attributes = True
