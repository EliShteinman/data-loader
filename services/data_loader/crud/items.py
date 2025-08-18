from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from .. import models
from ..core.dependencies import data_loader

# Create a new router object. This acts like a 'mini-FastAPI' application.
router = APIRouter(
    prefix="/items",  # All paths defined in this router will be prefixed with /items
    tags=["CRUD Items"],  # Group these endpoints under 'CRUD Items' in the OpenAPI docs
)


@router.post(
    "/",
    response_model=models.Item,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
)
def create_new_item(item: models.ItemCreate):
    """
    Create a new item in the database.
    - **first_name**: The first name of the person.
    - **last_name**: The last name of the person.
    """
    result = data_loader.create_item(item)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/{item_id}", response_model=models.Item, summary="Get a single item by ID")
def read_item(item_id: int):
    """
    Retrieve a single item from the database by its unique ID.
    """
    db_item = data_loader.get_item_by_id(item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return db_item


@router.get("/", response_model=List[models.Item], summary="Get all items")
def read_all_items():
    """
    Retrieve all items from the database.
    This is an alias for the original /data endpoint, placed here for logical grouping.
    """
    all_data = data_loader.get_all_data()
    if isinstance(all_data, dict) and "error" in all_data:
        raise HTTPException(status_code=500, detail=all_data["error"])
    return all_data


@router.put("/{item_id}", response_model=models.Item, summary="Update an existing item")
def update_existing_item(item_id: int, item: models.ItemCreate):
    """
    Update an existing item in the database by its unique ID.
    """
    result = data_loader.update_item(item_id, item)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found to update"
        )
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete(
    "/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item"
)
def delete_existing_item(item_id: int):
    """
    Delete an item from the database by its unique ID.
    On success, returns a 204 No Content response.
    """
    result = data_loader.delete_item(item_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found to delete"
        )
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # For a 204 response, we should not return any content.
    return
