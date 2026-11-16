import uuid
import pytest
from app.models import Business
from app.services import credits as credits_service
from app.services.billing import apply_charge_success, initialize_payment
from app.services.paystack import PaystackClient
from app.schemas.billing import BillingInitializeRequest
from tests.conftest import auth_headers


class MockPaystack(PaystackClient):
    def __init__(self):
        super().__init__("sk_test_123")
        self.initialized = []

    async def initialize_transaction(self, **kwargs):
        self.initialized.append(kwargs)
        return {
            "authorization_url": f"https://checkout.paystack.com/{kwargs['reference']}",
            "access_code": "code_xyz",
            "reference": kwargs["reference"],
        }

    async def verify_transaction(self, reference: str):
        return {"status": "success", "reference": reference}


@pytest.mark.asyncio
async def test_credits_add_and_deduct(session_factory, customer):
    async with session_factory() as db:
        biz = Business(name="Lekki Coffee", slug="lekki-coffee", plan="free", credit_balance=50, owner_id=customer.id)
        db.add(biz)
        await db.commit()
        await db.refresh(biz)
        biz_id = biz.id

        # 1. Initial balance check
        balance = await credits_service.get_credit_balance(db, biz_id)
        assert balance == 50

        # 2. Add credits
        new_balance, tx = await credits_service.add_credits(
            db, biz_id, 100, transaction_type="topup", description="Purchased 100 credits"
        )
        assert new_balance == 150
        assert tx.amount == 100
        assert tx.balance_after == 150

        # 3. Deduct credits for a task
        bal_after_deduct, tx2 = await credits_service.deduct_credits(
            db, biz_id, 20, description="Competitor research analysis", reference_id="task-123"
        )
        assert bal_after_deduct == 130
        assert tx2.amount == -20
        assert tx2.balance_after == 130

        # 4. Check insufficient credits raises error
        with pytest.raises(credits_service.InsufficientCreditsError):
            await credits_service.deduct_credits(
                db, biz_id, 500, description="Over-budget task"
            )

        # 5. Check ledger history
        txs, total = await credits_service.list_transactions(db, biz_id)
        assert total == 2
        tx_ids = {t.id for t in txs}
        assert tx.id in tx_ids
        assert tx2.id in tx_ids


@pytest.mark.asyncio
async def test_credit_pack_payment_grants_credits(session_factory, customer):
    """When a user buys a credit pack, charge.success grants the credits to the business."""
    async with session_factory() as db:
        biz = Business(name="Nairobi Wear", slug="nairobi-wear", plan="free", credit_balance=25, owner_id=customer.id)
        db.add(biz)
        await db.commit()
        await db.refresh(biz)
        biz_id = biz.id

        mock_paystack = MockPaystack()
        from app.config import get_settings

        # Initialize payment for 200 credits
        req = BillingInitializeRequest(
            plan="credits_200",
            business_id=biz_id,
            email="founder@example.com",
        )
        order, paystack_data = await initialize_payment(db, mock_paystack, get_settings(), req)
        assert order.plan == "credits_200"
        assert order.amount == 18000.00
        assert order.status == "pending"

        # Apply charge success (simulate Paystack webhook)
        paid_order = await apply_charge_success(db, str(order.id))
        assert paid_order is not None
        assert paid_order.status == "paid"

        # Verify business now has 25 + 200 = 225 credits!
        current_credits = await credits_service.get_credit_balance(db, biz_id)
        assert current_credits == 225

        # Check transaction in ledger
        txs, total = await credits_service.list_transactions(db, biz_id)
        assert total == 1
        assert txs[0].amount == 200
        assert txs[0].transaction_type == "topup"
        assert "credits_200" in txs[0].description


@pytest.mark.asyncio
async def test_billing_credit_api_endpoints(client, customer, session_factory):
    headers = auth_headers(customer)

    # Create business for customer
    async with session_factory() as db:
        biz = Business(
            name="Accra Botanicals",
            slug="accra-botanicals",
            plan="starter",
            credit_balance=60,
            owner_id=customer.id,
        )
        db.add(biz)
        await db.commit()
        await db.refresh(biz)
        biz_id = biz.id

    # 1. GET credits
    res = await client.get(f"/api/billing/{biz_id}/credits", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"business_id": str(biz_id), "balance": 60}

    # 2. POST deduct credits
    deduct_res = await client.post(
        f"/api/billing/{biz_id}/credits/deduct",
        json={"amount": 15, "description": "Social Media Campaign Generation", "reference_id": "run-456"},
        headers=headers,
    )
    assert deduct_res.status_code == 200
    data = deduct_res.json()
    assert data["amount_deducted"] == 15
    assert data["new_balance"] == 45
    assert "transaction_id" in data

    # 3. GET ledger
    ledger_res = await client.get(f"/api/billing/{biz_id}/credits/ledger", headers=headers)
    assert ledger_res.status_code == 200
    ledger = ledger_res.json()
    assert ledger["balance"] == 45
    assert ledger["total"] == 1
    assert ledger["transactions"][0]["amount"] == -15
    assert ledger["transactions"][0]["description"] == "Social Media Campaign Generation"

    # 4. Deduct more than balance -> 402 Payment Required
    over_res = await client.post(
        f"/api/billing/{biz_id}/credits/deduct",
        json={"amount": 200, "description": "Over budget"},
        headers=headers,
    )
    assert over_res.status_code == 402
