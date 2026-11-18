import asyncio
import os
from decimal import Decimal
from janzeer import Account, AsyncJanzeerClient, JanzeerRpcWs, TxBuilder

NODE = os.environ.get("JANZEER_NODE_URL", "http://localhost:7019")
WS = os.environ.get("JANZEER_WS_URL", NODE)
MNEMONIC = os.environ.get("JANZEER_E2E_MNEMONIC", "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")
RECIPIENT = os.environ.get("JANZEER_E2E_RECIPIENT", "0x598b1301acef3baba6ce25e38dd17b723f7b98b1")

async def main() -> None:
    invoice_ref = "inv-3f9a2c"
    amount = "0.5"
    me = Account.from_mnemonic(MNEMONIC)
    
    payment_received: asyncio.Future[dict] = asyncio.get_running_loop().create_future()

    async with await JanzeerRpcWs.connect(WS) as ws, AsyncJanzeerClient(NODE) as client:
        async def handler(ev: dict):
            tx = ev["transaction"]
            if tx["to"] == RECIPIENT and tx.get("data") == invoice_ref and Decimal(tx["amount"]) >= Decimal(amount):
                if not payment_received.done():
                    payment_received.set_result(ev)

        sub = await ws.subscribe_address_activity([RECIPIENT], handler)
        network_id = (await client.info())["networkId"]
        tx = me.sign_tx(TxBuilder.transfer(sender=me.address, to=RECIPIENT, amount=amount, nonce=await client.nonce(me.address), data=invoice_ref, network_id=network_id))
        await client.submit(tx)

        try:
            ev = await asyncio.wait_for(payment_received, 90)
            await client.await_finality(ev["blockHeight"])
            print(f"paid: {invoice_ref} {ev['transaction']['amount']} JNZ in block {ev['blockHeight']}")
        except asyncio.TimeoutError:
            print("Error: Payment not received within timeout")
            exit(1)
        finally:
            await sub.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())