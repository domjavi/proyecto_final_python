from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from crud.report import generate_excel_report, generate_csv_report, generate_pdf_report
from db.database import get_session
from auth.dependencies import require_role

router = APIRouter()

@router.get("/report/excel")
def excel_report(
    order_id: int = Query(None),
    user_id: int = Query(None),
    item_id: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "client":
        user_id = current_user["id"]
    try:
        return generate_excel_report(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/report/csv")
def csv_report(
    order_id: int = Query(None),
    user_id: int = Query(None),
    item_id: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "client":
        user_id = current_user["id"]
    try:
        return generate_csv_report(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/report/pdf")
def pdf_report(
    order_id: int = Query(None),
    user_id: int = Query(None),
    item_id: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "client":
        user_id = current_user["id"]
    try:
        return generate_pdf_report(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))