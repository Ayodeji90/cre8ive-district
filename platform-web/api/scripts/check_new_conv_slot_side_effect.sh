#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/platform-web/api"

if [ ! -x .venv/bin/python3 ]; then
  echo "missing .venv/bin/python3" >&2
  exit 2
fi

.exec .venv/bin/python3 - <<'PY'
import sys, uuid, os, tempfile
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(".").resolve()))
from app.models import NewConvSlot

db_path = Path(tempfile.mktemp(suffix=".db"))
engine = create_engine(f"sqlite:///{db_path}", echo=False)
NewConvSlot.metadata.create_all(engine)

with Session(engine) as s:
    biz = uuid.uuid4()
    owner = uuid.uuid4()
    rid = uuid.uuid4()
    row = s.execute(select(NewConvSlot).where(NewConvSlot.business_id == biz)).scalar_one_or_none()
    assert row is None
    s.execute(
        NewConvSlot.__table__.insert().prefix_with("OR IGNORE"),
        [{"business_id": biz, "owner_id": owner, "conversation_id": rid}],
    )
    s.commit()
    row = s.execute(select(NewConvSlot).where(NewConvSlot.business_id == biz)).scalar_one()
    assert row.conversation_id == rid, (row.conversation_id, rid)
    print("OK sqlite side-effect: row.conversation_id ==", rid)

os.unlink(db_path)
print("OK sqlite side-effect")
PY
