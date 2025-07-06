from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "a800418a7ef5315ac979f5633286ca8af82d8381a9ea1b3ca925fa2a558ff221"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users_db = {
    "professor-exemplo": {
        "username": "professor-exemplo",
        # password: gerarprovas 
        "hashed_password": "$2b$12$ASjhWwp/y7/Yw6IkCiIx9uSmv5ESIVMdHOsvcfb310Fk8UyxqPjXO"
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

authentication_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Verifica se uma senha em texto plano corresponde ao hash armazenado.

    Args:
        plain_password (str): Senha em texto plano fornecida pelo usuário
        hashed_password (str): Hash da senha armazenado no banco de dados

    Returns:
        bool: True se a senha for válida, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Gera um hash bcrypt para uma senha em texto plano.

    Args:
        password (str): Senha em texto plano a ser criptografada

    Returns:
        str: Hash bcrypt da senha
    """
    return pwd_context.hash(password)

def get_user(db, username: str):
    """
    Busca um usuário na base de dados pelo nome de usuário.

    Args:
        db (dict): Base de dados de usuários
        username (str): Nome de usuário a ser buscado

    Returns:
        UserInDB | None: Instância do usuário se encontrado, None caso contrário
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    """
    Autentica um usuário verificando suas credenciais.

    Args:
        fake_db (dict): Base de dados de usuários
        username (str): Nome de usuário para autenticação
        password (str): Senha em texto plano para verificação

    Returns:
        UserInDB | False: Instância do usuário se autenticado com sucesso, False caso contrário
    """
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Cria um token JWT de acesso com dados do usuário e tempo de expiração.

    Args:
        data (dict): Dados a serem incluídos no token (normalmente {'sub': username})
        expires_delta (timedelta | None): Tempo personalizado de expiração.
                                        Se None, usa 15 minutos como padrão

    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Extrai e valida o usuário atual baseado no token JWT fornecido.

    Args:
        token (str): Token JWT extraído do cabeçalho Authorization

    Returns:
        UserInDB: Instância do usuário autenticado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Verifica se o usuário atual está ativo e não foi desabilitado.

    Args:
        current_user (User): Usuário autenticado obtido do token JWT

    Returns:
        User: Instância do usuário ativo
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@authentication_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Endpoint para autenticação de usuários e geração de tokens JWT.

    Este endpoint recebe credenciais de login (username e password) através de um formulário
    OAuth2 e retorna um token JWT que pode ser usado para acessar rotas protegidas.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulário contendo username e password

    Returns:
        Token: Objeto contendo o access_token JWT e o tipo "bearer"
    """
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@authentication_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Endpoint para obter informações do usuário autenticado.

    Este endpoint retorna as informações do usuário que está atualmente autenticado
    baseado no token JWT fornecido no cabeçalho Authorization.

    Args:
        current_user (User): Usuário autenticado obtido através da dependência

    Returns:
        User: Informações do usuário autenticado (username, disabled)
    """
    return current_user
