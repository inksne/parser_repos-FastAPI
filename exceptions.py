from fastapi import HTTPException
from starlette import status


server_exc = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Непредвиденная серверная ошибка. Попробуйте позже.'
)


bad_email_exc = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail='Email некорректен. Введите действительный адрес электронной почты.'
)


bad_token_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f'Неверный токен.'
)


not_found_access_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access токен не найден в куки."
)


not_found_refresh_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Refresh токен не найден в куки."
)


not_found_token_user_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверный токен (пользователь не найден).'
)


unauthed_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный логин или пароль."
)


conflict_name = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Данное имя пользователя уже используется. Попробуйте другое.'
)