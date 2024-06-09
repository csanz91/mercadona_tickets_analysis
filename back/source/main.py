import logging
import logging.handlers
from typing import BinaryIO
import uuid

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from docker_secrets import getDocketSecrets

import mercadona_ticket
import tickets_analysis

logger = logging.getLogger()
handler = logging.handlers.RotatingFileHandler(
    "../logs/api.log", mode="a", maxBytes=1024 * 1024 * 10, backupCount=2
)
formatter = logging.Formatter(
    "%(asctime)s <%(levelname).1s> %(funcName)s:%(lineno)s: %(message)s"
)
logger.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


app = FastAPI()

# origins = [
#     "http://172.26.80.72:5173",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(SessionMiddleware, secret_key=getDocketSecrets("secret_key"))

# Simple in-memory session storage
session_storage = {}

folder = "tickets_mercadona"


# Dependency to get the current session data
def get_session_data(session_id: str):
    session_data = session_storage.get(session_id)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data


@app.get("/local-tickets")
def get_tariffs():
    df = mercadona_ticket.folder_to_pandas(folder)
    result = tickets_analysis.anaylis(df)
    return result


@app.post("/upload-tickets")
def upload_tickets(files: list[UploadFile] = File(...)):

    # Generate a unique session ID
    session_id = str(uuid.uuid4())

    tickets: list[mercadona_ticket.Ticket] = []
    for file in files:
        content: BinaryIO = file.file
        t: mercadona_ticket.Ticket = mercadona_ticket.ticket_from_file(content)
        tickets.append(t)
    df = mercadona_ticket.ticket_to_pandas(tickets)
    df.sort_values(by=["Date", "Product_Name"], inplace=True)

    # Store DataFrame in session storage
    session_storage[session_id] = df

    return JSONResponse(content={"session_id": session_id})


@app.get("/get-tickets-analysis")
def get_tickets_analysis(session_id: pd.DataFrame = Depends(get_session_data)):
    df = session_id
    result = tickets_analysis.anaylis(df)
    return result


@app.get("/get-product-names")
def get_product_names(session_id=Depends(get_session_data)):
    df: pd.DataFrame = session_id
    result = df["Product_Name"].unique().tolist()
    return JSONResponse(content=result)


@app.get("/price-evolution")
def get_price_evolution(
    product_name: str, session_id: pd.DataFrame = Depends(get_session_data)
):
    df = session_id
    return tickets_analysis.price_evolution(df, product_name)


@app.post("/delete-session")
def clear_session(session_id: str):
    if session_id in session_storage:
        del session_storage[session_id]
        return {"message": "Session cleared"}
    raise HTTPException(status_code=404, detail="Session not found")
