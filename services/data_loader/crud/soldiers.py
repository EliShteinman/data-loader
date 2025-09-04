from fastapi import APIRouter, HTTPException, status
from typing import List
from .. import models
from ..core.dependencies import data_loader

# Create router for soldiers according to exam requirements
router = APIRouter(
    prefix="/soldiersdb",  # As required by exam: /soldiersdb/
    tags=["Soldiers"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/",
    response_model=List[models.Soldier],
    summary="Get all soldiers",
    description="Retrieve all enemy soldiers from the database"
)
def get_all_soldiers():
    """
    GET /soldiersdb/ - Retrieve all soldiers (שליפה)
    """
    try:
        soldiers = data_loader.get_all_soldiers()
        if isinstance(soldiers, dict) and "error" in soldiers:
            raise HTTPException(status_code=500, detail=soldiers["error"])
        return soldiers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post(
    "/",
    response_model=models.Soldier,
    status_code=status.HTTP_201_CREATED,
    summary="Create new soldier",
    description="Add a new enemy soldier to the database"
)
def create_soldier(soldier: models.SoldierCreate):
    """
    POST /soldiersdb/ - Create new soldier (הוספה)
    """
    try:
        result = data_loader.create_soldier(soldier)
        if isinstance(result, dict) and "error" in result:
            if "duplicate" in result["error"].lower() or "exists" in result["error"].lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Soldier with ID {soldier.ID} already exists"
                )
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get(
    "/{soldier_id}",
    response_model=models.Soldier,
    summary="Get soldier by ID",
    description="Retrieve specific soldier by ID"
)
def get_soldier(soldier_id: int):
    """
    GET /soldiersdb/{id} - Get soldier by ID (שליפה ספציפית)
    """
    try:
        soldier = data_loader.get_soldier_by_id(soldier_id)
        if soldier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soldier with ID {soldier_id} not found"
            )
        if isinstance(soldier, dict) and "error" in soldier:
            raise HTTPException(status_code=500, detail=soldier["error"])
        return soldier
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put(
    "/{soldier_id}",
    response_model=models.Soldier,
    summary="Update soldier",
    description="Update existing soldier information"
)
def update_soldier(soldier_id: int, soldier_update: models.SoldierUpdate):
    """
    PUT /soldiersdb/{id} - Update soldier (עדכון)
    """
    try:
        result = data_loader.update_soldier(soldier_id, soldier_update)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soldier with ID {soldier_id} not found"
            )
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete(
    "/{soldier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete soldier",
    description="Delete soldier from database"
)
def delete_soldier(soldier_id: int):
    """
    DELETE /soldiersdb/{id} - Delete soldier (מחיקה)
    """
    try:
        result = data_loader.delete_soldier(soldier_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soldier with ID {soldier_id} not found"
            )
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return  # 204 No Content - no body returned
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")