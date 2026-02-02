from app.core.routes import get_current_user
from app.db.session import get_db
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.schema import WorkItemModelSqlSchema, WorkItemFilterRequestData, WorkItemResponse
from fastapi import HTTPException
from fastapi import Body
import redis
from datetime import datetime


# create redis obj
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0
)


router = APIRouter(
    prefix="/metrics",
    dependencies=[Depends(get_current_user)]
)

def get_redis_key_single_wid(workitem_id:str):
    key = f"workitem_id: {workitem_id}"
    return key


def get_redis_key_multiple_wid():
    key = ""


@router.post("/api/items/date-range", response_model=dict)
# @router.post("/api/items/date-range", response_model=WorkItemResponse)
def get_items_on_date_range(payload: WorkItemFilterRequestData = Body(...), db: Session = Depends(get_db)):
    print("convert the start and end date to datetime format")
    start_date = datetime.strptime(payload.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(payload.end_date, "%Y-%m-%d")
    end_date = end_date.replace(hour=23, minute=59, second=59)
    pid = payload.pid
    work_item_state = payload.state
    work_item_status = payload.status

    print(f"{start_date=}")

    print(f"{end_date=}")
    print(f"{pid=}")
    print(f"{work_item_state=}")
    print(f"{work_item_status=}")

    print("process id",WorkItemModelSqlSchema.process_id)
    qs = db.query(WorkItemModelSqlSchema).filter(
        WorkItemModelSqlSchema.process_id == pid,  # SQL schema fields is for querying
        WorkItemModelSqlSchema.created_at.between(start_date, end_date)
    )

    print(f"{qs = }")
    if work_item_state:
        qs = qs.filter(WorkItemModelSqlSchema).filter(
            WorkItemModelSqlSchema.state == work_item_state,
            WorkItemModelSqlSchema.status == work_item_status
        )

    # to check if state or  state also provideR
    db_items = qs.all()

    # NOW CONVERT THE SQL SCHEMA TO RESPONSE SCHEMA USING PYDANTIC MODEL TO RETURN RESPONSE
    result = []
    for item in db_items:
        result.append(WorkItemResponse(
            workitem_id=item.workitem_id,
            process_id=item.process_id,
            comment=item.comment,
            state=item.state,
            status=item.status,
            detail=item.detail,
            exception_type=item.exception_type,
            created_at=item.created_at,
            updated_at=item.updated_at
        ))
    print(f"found {len(db_items)}")
    return {
            "count": len(result),
            "result": result
        }


@router.get(path="/api/get/item/by/id/{workitem_id}", response_model=WorkItemResponse)
def get_workitem_by_id(workitem_id: str, db: Session = Depends(get_db)):
    print("getting work-item by its ID...")
    try:
        workitem = db.query(WorkItemModelSqlSchema).filter(
            WorkItemModelSqlSchema.workitem_id == workitem_id).first()
        print(f"{workitem=}")
        if not workitem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    'detail': f'workitem {workitem} not found.'
                }
            )
        return workitem
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An error occurred while fetching the work item"}
        )


