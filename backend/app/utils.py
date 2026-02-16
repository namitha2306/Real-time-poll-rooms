import hashlib

def generate_voter_hash(ip: str, user_agent: str, poll_id: str):
    raw = f"{ip}-{user_agent}-{poll_id}"
    return hashlib.sha256(raw.encode()).hexdigest()
