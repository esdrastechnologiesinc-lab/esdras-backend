import json, os
from .. import Config

def validate_ownership(user_id, filename, stored_sig):
    if not filename.startswith(f"headmesh_{user_id}_"):
        raise PermissionError("This mesh does not belong to you")

    path = os.path.join(Config.HEADMESH_STORAGE_PATH, filename)
    with open(path, "rb") as f:
        raw = f.read()
    metadata = json.loads(raw.split(b"||SEP||")[0])

    if metadata.get("owner_user_id") != user_id:
        raise PermissionError("Profile belongs to another human")
    if metadata.get("signature") != stored_sig:
        raise PermissionError("Profile has been tampered with")

def load_head_mesh_for_user(user_id):
    from ..models.user import User
    user = User.query.get(user_id)
    if not user.head_mesh_filename:
        raise ValueError("No profile")
    validate_ownership(user_id, user.head_mesh_filename, user.head_mesh_signature)
    # decryption happens here in real app
    return True