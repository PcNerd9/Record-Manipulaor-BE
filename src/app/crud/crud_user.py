from fastcrud import FastCRUD

from app.model.user import User
from app.schemas.user import UserCreate, UserCreateInternals, UserRead, UserUpdate, Userfilter
 

CRUDUser = FastCRUD[User, UserCreateInternals, UserRead, UserUpdate, Userfilter, UserRead]

crud_users = CRUDUser(User)