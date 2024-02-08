import httpx
import uvicorn
import sqlalchemy as sa
from collections import defaultdict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from db.models.models import BitcoinAddressModel, TransactionModel
from db.main import Session
from datetime import datetime
from fastapi import HTTPException, Query

from schemas.schemas import (
    BitcoinAddress,
    Transaction,
)

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/add_address/")
async def add_address(address: BitcoinAddress):
    with Session() as session:
        existing_address = (
            session.query(BitcoinAddressModel)
            .filter(BitcoinAddressModel.address == address.address)
            .first()
        )
        if existing_address:
            raise HTTPException(
                status_code=400, detail="Bitcoin address already exists."
            )
        new_address = BitcoinAddressModel(
            address=address.address, user_id=address.user_id, balance=address.balance
        )
        session.add(new_address)
        session.commit()
        return {"message": "Bitcoin address added successfully."}


@app.delete("/remove_address/{address}")
async def remove_address(address: str, user_id: str):
    with Session() as session:
        db_address = (
            session.query(BitcoinAddressModel)
            .filter(BitcoinAddressModel.address == address)
            .filter(BitcoinAddressModel.user_id == user_id)
            .first()
        )
        if not db_address:
            raise HTTPException(status_code=404, detail="Bitcoin address not found.")
        session.delete(db_address)
        session.commit()
        return {"message": "Bitcoin address removed successfully."}


@app.get("/get_wallet_info/{address}")
async def get_wallet_info(
    address: str, limit: int = Query(default=10, le=50), offset: int = 0
):
    with Session() as session:
        bitcoin_address = (
            session.query(BitcoinAddressModel)
            .filter(BitcoinAddressModel.address == address)
            .first()
        )
        if not bitcoin_address:
            raise HTTPException(status_code=404, detail="Bitcoin address not found.")

        transactions_query = (
            session.query(TransactionModel)
            .filter(TransactionModel.bitcoin_address_id == bitcoin_address.id)
            .order_by(TransactionModel.time.desc())
            .offset(offset)
            .limit(limit)
        )
        transactions = transactions_query.all()

        transaction_details = [
            {
                "hash": tx.hash,
                "amount": tx.amount,
                "sender": tx.sender,
                "receiver": tx.receiver,
                "time": tx.time,
            }
            for tx in transactions
        ]

        response_data = {
            "address": address,
            "balance": bitcoin_address.balance,
            "transactions": transaction_details,
            "next_offset": offset + limit,
        }

        return response_data


@app.post("/synchronize/{address}")
async def synchronize_address(address: str, user_id: str):
    with Session() as session:
        # Check if the Bitcoin address exists for the given user ID
        db_address = (
            session.query(BitcoinAddressModel)
            .filter(BitcoinAddressModel.address == address)
            .filter(BitcoinAddressModel.user_id == user_id)
            .first()
        )
        if not db_address:
            raise HTTPException(
                status_code=404, detail="Bitcoin address not found for the given user."
            )

        # Fetch transactions from the blockchain API
        blockchain_url = f"https://blockchain.info/rawaddr/{address}"
        async with httpx.AsyncClient() as client:
            response = await client.get(blockchain_url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch transactions from Blockchain API.",
                )

            data = response.json()
            transactions = data.get("txs", [])

            db_address.balance = (
                data["final_balance"] / 1e8
            )  # Convert satoshi to bitcoin

            for tx in transactions:
                # Simplification: Assuming the first input is the sender and the first output is the receiver
                sender = tx["inputs"][0]["prev_out"]["addr"] if tx["inputs"] else None
                receiver = tx["out"][0]["addr"] if tx["out"] else None
                amount = (
                    tx["out"][0]["value"] / 1e8 if tx["out"] else 0
                )  # Convert satoshi to bitcoin
                time = datetime.utcfromtimestamp(tx["time"])

                existing_tx = (
                    session.query(TransactionModel)
                    .filter(TransactionModel.hash == tx["hash"])
                    .first()
                )
                if not existing_tx:
                    new_tx = TransactionModel(
                        hash=tx["hash"],
                        amount=amount,
                        sender=sender,
                        receiver=receiver,
                        time=time,
                        bitcoin_address_id=db_address.id,
                    )
                    session.add(new_tx)

            session.commit()
            return {"message": "Address synchronized successfully, balance updated."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
