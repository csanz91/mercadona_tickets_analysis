from datetime import datetime
import io
import math
from typing import BinaryIO
import fitz  # PyMuPDF
import pandas as pd
import re
import os
from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class Product:
    qty: float
    name: str
    unitary_price: float
    total_price: float


@dataclass
class Ticket:
    number: str
    total_cost: float
    credit_card: str
    date: datetime
    products: list[Product]


pattern_product = (
    r"\n([\d]+)[ \n]{1}([\w|\W][^\n]+)\n(?!.* kg)([\d]+,[\d]+)?\n?([\d]+,[\d]+)"
)
pattern_bulk_product = (
    r"\n([\w|\W][^\n]+)\n([\d]+,[\d]+)\ kg\n([\d]+,[\d]+)\ €/kg\n([\d]+,[\d]+)"
)
pattern_total_price = r"Importe:\ ([\d]+,[\d]+)\ €"
pattern_ticket_number = r"FACTURA SIMPLIFICADA:\ ([\d-]+)\n"
pattern_datetime = r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})"
pattern_credit_card = r"TARJ\. BANCARIA:[* ]+ (\d+)\n"

p_product = re.compile(pattern_product)
p_bulk_product = re.compile(pattern_bulk_product)
p_total_price = re.compile(pattern_total_price)
p_ticket_number = re.compile(pattern_ticket_number)
p_datetime = re.compile(pattern_datetime)
p_credit_card = re.compile(pattern_credit_card)


def price_to_float(text_price) -> float:
    return float(text_price.replace(",", "."))


def get_product(text):
    products = []
    matches = p_product.finditer(text)
    if not matches:
        logger.error("No product matches found")
        return products
    
    for match in matches:
        qty, name, unitary_price, total_price = match.groups()

        total_price = price_to_float(total_price)
        if unitary_price is not None:
            unitary_price = price_to_float(unitary_price)
        else:
            unitary_price = total_price

        product = Product(
            qty=price_to_float(qty),
            name=name,
            unitary_price=unitary_price,
            total_price=total_price,
        )
        products.append(product)
    return products


def get_bulk_products(text):
    products = []
    matches = p_bulk_product.finditer(text)
    if not matches:
        logger.error("No bulk product matches found")
        return products

    for match in matches:
        name, weight, price_per_kg, total_price = match.groups()

        product = Product(
            qty=price_to_float(weight),
            name=name,
            unitary_price=price_to_float(price_per_kg),
            total_price=price_to_float(total_price),
        )
        products.append(product)

    return products


def get_ticket_cost(text):
    match = p_total_price.search(text)
    if not match:
        return 0.0
    price = match.group(1)
    return price_to_float(price)


def get_ticket_number(text):
    match = p_ticket_number.search(text)
    if not match:
        return ""
    ticket_number = match.group(1)
    return ticket_number


def get_ticket_datetime(text):
    match = p_datetime.search(text)
    if not match:
        return datetime.min
    date = match.group(1)
    return datetime.strptime(date, "%d/%m/%Y %H:%M")


def get_credit_card(text):
    match = p_credit_card.search(text)
    if not match:
        return ""
    credit_card = match.group(1)
    return credit_card


def get_ticket(pdf_document) -> Ticket:
    # Extract text blocks from the first page
    page = pdf_document[0]
    blocks = page.get_text("blocks")
    text = "".join([block[4] for block in blocks])

    ticket = Ticket(
        get_ticket_number(text),
        get_ticket_cost(text),
        get_credit_card(text),
        get_ticket_datetime(text),
        get_product(text) + get_bulk_products(text),
    )

    # Make sure the full ticket has been processed correctly
    if (
        not ticket.number
        or not ticket.total_cost
        or not ticket.products
        or not ticket.date
    ):
        logger.error(
            f"Ticket data is incomplete: {ticket.number}, {ticket.total_cost}, {ticket.products}, {ticket.date}"
        )
        logger.error(f"Text: {text}")
        raise ValueError("Incomplete ticket data")

    if not math.isclose(
        sum(p.total_price for p in ticket.products), ticket.total_cost, rel_tol=1e-2
    ):
        logger.error(
            f"Total price mismatch: {ticket.total_cost} != {sum(p.total_price for p in ticket.products)}"
        )
        logger.error(f"Text: {text}")
        raise ValueError("Total price mismatch")
    return ticket


def ticket_to_pandas(tickets: Ticket | list[Ticket]) -> pd.DataFrame:
    if not isinstance(tickets, list):
        tickets = [tickets]

    data = [
        [
            ticket.number,
            ticket.date,
            ticket.credit_card,
            ticket.total_cost,
            product.name,
            product.qty,
            product.unitary_price,
            product.total_price,
        ]
        for ticket in tickets
        for product in ticket.products
    ]

    # Create a DataFrame
    columns = [
        "Ticket_Number",
        "Date",
        "Credit_Card",
        "Total_Price",
        "Product_Name",
        "Product_Qty",
        "Product_Unit_Price",
        "Product_Total_Price",
    ]
    df = pd.DataFrame(columns=columns, data=data)

    return df


def pdf_to_pandas(filepath: str) -> pd.DataFrame:
    pdf_document = fitz.open(filepath)

    ticket = get_ticket(pdf_document)
    pdf_document.close()

    df = ticket_to_pandas(ticket)
    return df


def ticket_from_file(file: BinaryIO):
    with io.BytesIO(file.read()) as pdf_io:
        pdf_document = fitz.open(stream=pdf_io, filetype="pdf")
    file.close()
    ticket = get_ticket(pdf_document)
    return ticket


def folder_to_pandas(folder: str) -> pd.DataFrame:
    tickets: list[Ticket] = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            print(f"Processing file: {filename}")

            filepath = os.path.join(folder, filename)
            pdf_document = fitz.open(filepath)

            ticket = get_ticket(pdf_document)
            tickets.append(ticket)

            pdf_document.close()

    df = ticket_to_pandas(tickets)
    df.sort_values(by=["Date", "Product_Name"], inplace=True)
    return df
