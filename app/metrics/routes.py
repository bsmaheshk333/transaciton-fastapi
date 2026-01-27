from app.core.routes import get_current_user
from app.db.session import get_db
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.schema import WorkItemModelSqlSchema, WorkItemFilterRequestData, WorkItemResponse
from fastapi import HTTPException
from fastapi import Body


router = APIRouter(
    prefix="/metrics",
    dependencies=[Depends(get_current_user)]
)


@router.post("/api/items/date-range", response_model=dict)
def get_items_on_date_range(payload: WorkItemFilterRequestData = Body(...), db: Session = Depends(get_db)):
    print("Getting items by the date range.")
    start_date = payload.start_date
    end_date = payload.end_date
    pid = payload.pid
    work_item_state = payload.state
    work_item_status = payload.status

    print("process id",WorkItemModelSqlSchema.process_id)
    qs = db.query(WorkItemModelSqlSchema).filter(
        WorkItemModelSqlSchema.process_id == pid,  # SQL schema fields is for querying
        WorkItemModelSqlSchema.created_at >= start_date,
        WorkItemModelSqlSchema.created_at <= end_date
    )
    print("here..")
    if work_item_state:
        qs = qs.filter(WorkItemModelSqlSchema).filter(
            WorkItemModelSqlSchema.state == work_item_state,
            WorkItemModelSqlSchema.status == work_item_status
        )

    # to check if state or  state also provided

    result = qs.all()

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

