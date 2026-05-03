# app/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from llm_p.app.schemas.auth import RegisterRequest, TokenResponse
from llm_p.app.schemas.user import UserPublic
from llm_p.app.usecases.auth import AuthUseCase
from llm_p.app.api.deps import get_auth_usecase, get_current_user_id
from llm_p.app.core.errors import ConflictError, UnauthorizedError, NotFoundError


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Email already exists"},
    }
)

async def register(
    request: RegisterRequest,
    auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):
    """
    Регистрация нового пользователя.
    
    Args:
        request: Данные для регистрации (email, password)
        auth_usecase: Use case для авторизации
        
    Returns:
        UserPublic: Созданный пользователь без пароля
        
    Raises:
        HTTPException: 409 если email уже занят
    """
    try:
        return await auth_usecase.register(request)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/token",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):
    """
    Вход пользователя в систему (OAuth2 формат для Swagger UI).
    
    Args:
        form_data: Форма с username (email) и password
        auth_usecase: Use case для авторизации
        
    Returns:
        TokenResponse: JWT токен
        
    Raises:
        HTTPException: 401 если неверные учетные данные
    """
    try:
        # В OAuth2PasswordRequestForm поле username используется как email
        return await auth_usecase.login(
            email=form_data.username,
            password=form_data.password
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get(
    "/me",
    response_model=UserPublic,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"},
    }
)
async def get_me(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):
    """
    Получить профиль текущего пользователя.
    
    Args:
        user_id: ID текущего пользователя (из JWT токена)
        auth_usecase: Use case для авторизации
        
    Returns:
        UserPublic: Профиль пользователя
        
    Raises:
        HTTPException: 401 если токен невалиден, 404 если пользователь не найден
    """
    try:
        return await auth_usecase.get_profile(user_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )