from datetime import datetime
import io
import math
from typing import BinaryIO
import fitz  # PyMuPDF
import pandas as pd
import re
import os
from dataclasses import dataclass
from re import Match


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


pattern_product = r"^([\d])[ \n]{1}([\w|\W][^\n]+)\n([\d]+,[\d]+)?\n?([\d]+,[\d]+)\n$"
pattern_bulk_product_a = r"^([\d])[ \n]{1}([\w|\W][^\n]+)\n$"
pattern_bulk_product_b = r"^([\d]+,[\d]+)\ kg\n([\d]+,[\d]+)\ €/kg\n([\d]+,[\d]+)\n$"
pattern_total_price = r"Importe:\ ([\d]+,[\d]+)\ €"
pattern_ticket_number = r"FACTURA SIMPLIFICADA:\ ([\d-]+)\n"
pattern_datetime = r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})"
pattern_credit_card = r"^TARJ. BANCARIA:  \*\*\*\*\ \*\*\*\*\ \*\*\*\*\ ([\d]{4})\n"

p_product = re.compile(pattern_product)
p_bulk_product_a = re.compile(pattern_bulk_product_a)
p_bulk_product_b = re.compile(pattern_bulk_product_b)
p_total_price = re.compile(pattern_total_price)
p_ticket_number = re.compile(pattern_ticket_number)
p_datetime = re.compile(pattern_datetime)
p_credit_card = re.compile(pattern_credit_card)


def price_to_float(text_price) -> float:
    return float(text_price.replace(",", "."))


def get_product(text):
    match: Match[str] | None = p_product.match(text)
    if not match:
        return None

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

    return product


def get_bulk_product_a(text):
    match: Match[str] | None = p_bulk_product_a.match(text)
    if not match:
        return None

    qty, name = match.groups()

    product = Product(
        qty=price_to_float(qty),
        name=name,
        unitary_price=-1.0,
        total_price=-1.0,
    )
    return product


def get_bulk_product_b(text, temp_product):

    match = p_bulk_product_b.match(text)
    if not match:
        return None

    if temp_product is None:
        raise ValueError("No se ha encontrado el nombre del producto a granel")

    weight, price_per_kg, total_price = match.groups()
    temp_product.qty = price_to_float(weight)
    temp_product.unitary_price = price_to_float(price_per_kg)
    temp_product.total_price = price_to_float(total_price)

    return temp_product


def get_ticket_cost(text):
    match = p_total_price.match(text)
    if not match:
        return None
    price = match.group(1)
    return price_to_float(price)


def get_ticket_number(text):
    match = p_ticket_number.match(text)
    if not match:
        return None
    ticket_number = match.group(1)
    return ticket_number


def get_ticket_datetime(text):
    match = p_datetime.match(text)
    if not match:
        return None
    date = match.group(1)
    return datetime.strptime(date, "%d/%m/%Y %H:%M")


def get_credit_card(text):
    match = p_credit_card.match(text)
    if not match:
        return None
    credit_card = match.group(1)
    return credit_card


def get_ticket(pdf_document) -> Ticket:

    ticket = Ticket("", 0.0, "", datetime.now(), [])
    temp_product = None

    # Extract text blocks from the first page
    page = pdf_document[0]
    blocks = page.get_text("blocks")
    for block in blocks:
        x0, y0, x1, y1, text, block_no, x = block

        # Get a product
        product = get_product(text)
        if product:
            ticket.products.append(product)
            continue

        # Get the qty and name of a bulk product
        bulk_product = get_bulk_product_a(text)
        if bulk_product:
            temp_product = bulk_product
            continue

        # Get the weight and price of a bulk product
        bulk_product = get_bulk_product_b(text, temp_product)
        if bulk_product:
            ticket.products.append(bulk_product)
            continue

        # Get the total ticket cost
        ticket_cost = get_ticket_cost(text)
        if ticket_cost:
            ticket.total_cost = ticket_cost
            continue

        # Get the ticket number
        ticket_number = get_ticket_number(text)
        if ticket_number:
            ticket.number = ticket_number
            continue

        # Get the ticket date
        ticket_date = get_ticket_datetime(text)
        if ticket_date:
            ticket.date = ticket_date
            continue

        # Get the ticket credit card
        credit_card = get_credit_card(text)
        if credit_card:
            ticket.credit_card = credit_card
            continue

    # Make sure the full ticket has been processed correctly
    if (
        not ticket.number
        or not ticket.total_cost
        or not ticket.products
        or not ticket.date
    ):
        raise ValueError("Incomplete ticket data")

    if not math.isclose(
        sum(p.total_price for p in ticket.products), ticket.total_cost, rel_tol=1e-2
    ):
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
