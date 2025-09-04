from pydantic import BaseModel, Field
from typing import Optional


class SoldierBase(BaseModel):
    """
    Base model containing common fields for a soldier record.
    Based on the exam requirements for enemy soldiers database.
    """
    first_name: str = Field(..., description="Soldier's first name")
    last_name: str = Field(..., description="Soldier's last name")
    phone_number: int = Field(..., description="Soldier's phone number")
    rank: str = Field(..., description="Soldier's military rank")


class SoldierCreate(SoldierBase):
    """
    Model for creating a soldier (data sent in POST/PUT requests).
    Includes the unique ID field required by the exam.
    """
    ID: int = Field(..., description="Unique soldier identifier")


class SoldierUpdate(BaseModel):
    """
    Model for updating soldier information with partial updates.
    All fields are optional to allow partial updates.
    """
    first_name: Optional[str] = Field(None, description="Updated first name")
    last_name: Optional[str] = Field(None, description="Updated last name")
    phone_number: Optional[int] = Field(None, description="Updated phone number")
    rank: Optional[str] = Field(None, description="Updated military rank")


class Soldier(SoldierBase):
    """
    Model representing a soldier as stored and returned from database.
    Includes the database-generated/provided ID.
    """
    ID: int = Field(..., description="Unique soldier identifier")

    class Config:
        """
        Pydantic model configuration.
        """
        from_attributes = True


# Legacy models for backward compatibility with existing data
class ItemBase(BaseModel):
    """Legacy model - keeping for backward compatibility"""
    first_name: str
    last_name: str


class ItemCreate(ItemBase):
    """Legacy model - keeping for backward compatibility"""
    pass


class Item(ItemBase):
    """Legacy model - keeping for backward compatibility"""
    ID: int

    class Config:
        from_attributes = True