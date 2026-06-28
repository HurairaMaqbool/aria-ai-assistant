from contextvars import ContextVar, Token

from aria.config import ALLOWED_MODELS

_user_id_ctx: ContextVar[str] = ContextVar("user_id", default="default")
_model_ctx: ContextVar[str] = ContextVar("model_name", default=ALLOWED_MODELS[0])


def get_active_user_id() -> str:
    return _user_id_ctx.get()


def get_selected_model() -> str:
    return _model_ctx.get()


def set_request_context(user_id: str, model_name: str | None = None) -> tuple[Token, Token | None]:
    user_token = _user_id_ctx.set(user_id)
    model_token = None
    if model_name is not None:
        model_token = _model_ctx.set(model_name)
    return user_token, model_token


def reset_request_context(user_token: Token, model_token: Token | None = None) -> None:
    _user_id_ctx.reset(user_token)
    if model_token is not None:
        _model_ctx.reset(model_token)
