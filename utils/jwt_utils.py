import streamlit as st
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = st.secrets["general"]["SECRET_KEY"]

def encode_jwt(user_data):
    if not isinstance(SECRET_KEY, str):
        raise ValueError("SECRET_KEY deve ser uma string.")
    now = datetime.now(timezone.utc)
    payload = {
        "exp": now + timedelta(days=1),  # Token expira em 1 dia
        "iat": now,
        "sub": user_data
    }
    try:
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        print(f"Erro ao codificar o JWT: {e}")
        return None
    
def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        print("Token expirado.")
        return None
    except jwt.InvalidTokenError:
        print("Token inválido.")
        return None