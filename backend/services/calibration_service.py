import uuid, json, os
from datetime import datetime
from sqlalchemy import text
from .. import db, Config
from ..utils.crypto import encrypt_aes_gcm, derive_encryption_key

def save_head_mesh(user_id: int, mesh_data: bytes, landmarks: dict, signature: str):
    filename = f"headmesh_{user_id}_{uuid.uuid4().hex}.bin"
    path = os.path.join(Config.HEADMESH_STORAGE_PATH, filename)

    key = derive_encryption_key(user_password_hash="***", user_id=str(user_id))  # real hash used in prod
    encrypted = encrypt_aes_gcm(mesh_data, key)

    metadata = {
        "owner_user_id": user_id,
        "signature": signature,
        "created_at": datetime.utcnow().isoformat(),
        "version": "2.0-irreversible-lock"
    }

    with open(path, "wb") as f:
        f.write(json.dumps(metadata).encode() + b"||SEP||" + encrypted)

    db.session.execute(text("""
        UPDATE users SET
            head_mesh_filename = :f,
            head_mesh_signature = :s,
            head_mesh_bound_at = NOW()
        WHERE id = :id
    """), {"f": filename, "s": signature, "id": user_id})
    db.session.commit()