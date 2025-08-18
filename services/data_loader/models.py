from pydantic import BaseModel


class ItemBase(BaseModel):
    """
    Base model containing common fields for an item.
    This helps to avoid code duplication (DRY principle).
    """

    first_name: str
    last_name: str


class ItemCreate(ItemBase):
    """
    Model for creating an item (data sent in POST/PUT requests).
    It inherits all fields from ItemBase. The 'pass' statement
    indicates that no additional fields are needed for creation.
    """

    pass


class Item(ItemBase):
    """
    Model representing an item as it is stored and returned from the database.
    It includes the database-generated ID.
    """

    ID: int

    class Config:
        """
        Pydantic model configuration.
        """

        from_attributes = True  # Allows Pydantic to create the model from object attributes (e.g., from an ORM object)
