import re
import uuid

import streamlit as st

from aria.config import SESSION_PARAM

VALID_UID = re.compile(r"^user_[a-z0-9]{8}$")


def _read_query_uid() -> str:
    raw = st.query_params.get(SESSION_PARAM, "")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    return str(raw).strip()


def get_or_create_user_id() -> str:
    if "user_id" in st.session_state:
        return st.session_state.user_id

    query_uid = _read_query_uid()
    if query_uid and VALID_UID.match(query_uid):
        uid = query_uid
    else:
        uid = "user_" + str(uuid.uuid4())[:8]
        st.query_params[SESSION_PARAM] = uid

    st.session_state.user_id = uid
    return uid
