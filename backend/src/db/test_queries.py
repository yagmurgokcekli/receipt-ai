from src.db.session import SessionLocal
from src.db.models.receipt import Receipt


def run():
    db = SessionLocal()
    try:
        receipts = db.query(Receipt).order_by(Receipt.created_at.desc()).limit(5).all()

        for r in receipts:
            print(
                r.id,
                r.merchant,
                r.total,
                r.currency,
                r.source,
                r.created_at,
            )
    finally:
        db.close()


if __name__ == "__main__":
    run()
