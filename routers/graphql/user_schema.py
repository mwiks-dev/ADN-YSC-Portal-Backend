import datetime
import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload
from typing import Optional
from config.db import SessionLocal
from schemas.graphql.user_type import UpdateUserInput, RegisterInput, LoginInput, TokenType, ResetPasswordInput, LoginPayload, SearchInput, UserListResponse, UploadProfilePicResponse
from schemas.graphql.shared_types import UserType, RoleEnum, UserStatus
from services.user_service import get_user_by_id, get_user_by_email, get_users, create_user, update_user, delete_user, authenticate_user, create_access_token, reset_password
from utils.auth_utils import is_chaplain, is_ysc_coordinator, can_register_users, is_superuser
from passlib.context import CryptContext
from utils.auth_utils import get_current_user, can_register_users
from models.user import User
import imghdr
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    
@strawberry.type
class UserQuery:
    @strawberry.field
    def user(self, info: Info, id: int) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return get_user_by_id(db, id)

    @strawberry.field
    def users(self, info: Info, input: SearchInput) -> UserListResponse:
        user = get_current_user(info)
        if not can_register_users(user):
            raise Exception("Unauthorized!")
        
        db = SessionLocal()
        query = db.query(User).order_by(User.id.desc(), User.parish_id.asc())

        if input.search.strip():  # Only filter by name if search is not empty
            search = f"%{input.search.strip()}%"
            query = query.filter(User.name.ilike(search))  # Case-insensitive match
            
        if input.parish_id is not None:
            query = query.filter(User.parish_id == input.parish_id)

        total_count = query.count()
        offset = (input.page - 1) * input.limit
        users = query.offset(offset).limit(input.limit).all()

        result = []
        for user in users:
            result.append(
                UserType(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phonenumber=user.phonenumber,
                    dateofbirth = user.dateofbirth,
                    idnumber = user.idnumber,
                    baptismref = user.baptismref,
                    profile_pic= user.profile_pic,
                    role=RoleEnum(user.role.value), 
                    status = UserStatus(user.status.value), # Convert from SQLAlchemy Enum to Strawberry Enum
                    parish=user.parish
                )
            )

        return UserListResponse(users = result, totalCount=total_count)
    
@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create_user(self, input: RegisterInput) -> UserType:
        db = SessionLocal()
        return create_user(db, input.name, input.email, input.phonenumber,input.dateofbirth, input.idnumber, input.baptismref, input.password, input.role.value, input.status.value,input.profile_pic, input.parish_id)

    @strawberry.mutation
    def update_user(self, info: Info, input: UpdateUserInput) -> Optional[UserType]:
        user = get_current_user(info)
        if not user:
            raise Exception("Unauthorized")
        if not (is_chaplain(user) or is_superuser(user) or user.id != input.id):
            raise Exception("You can only update your own information!")
        db = SessionLocal()
        return update_user(db, input.id, input.name, input.email, input.phonenumber,input.dateofbirth, input.idnumber, input.baptismref, input.password, input.role.value, input.status.value, input.parish_id)

    @strawberry.mutation
    def delete_user(self, info: Info, id: int) -> Optional[UserType]:
        user = get_current_user(info)
        if not can_register_users(user):
            raise Exception("Unauthorized!")
        db = SessionLocal()
        return delete_user(db, id)
    
    @strawberry.mutation
    def register(self, info:Info, input:RegisterInput) -> UserType:
        db = SessionLocal()
        existing_user = get_user_by_email(db,input.email)
        if existing_user:
            raise Exception("User with this email already exists")
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")
        if not can_register_users(current_user):
            raise Exception("Unauthorized: Only the Chaplain, Coordinators, Deanery or Parish Moderators can register members.")
        user = create_user(db,input.name, input.email, input.phonenumber,input.dateofbirth, input.idnumber, input.baptismref, input.password, input.role.value,input.status.value, input.profile_pic, input.parish_id )
        return UserType(id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,dateofbirth = user.dateofbirth, idnumber = user.idnumber, baptismref=user.baptismref, role= user.role, status=user.status, profile_pic=user.profile_pic, parish=user.parish)

    @strawberry.mutation
    def login(self, input: LoginInput) -> Optional[LoginPayload]:
        db = SessionLocal()
        user = authenticate_user(db, input.email, input.password)
        if not user:
            return None
        token = create_access_token(data={"sub": user.email})
        return LoginPayload(
            token = TokenType(access_token=token, token_type="bearer"),
            user = UserType(id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,dateofbirth=user.dateofbirth, idnumber=user.idnumber, baptismref= user.baptismref, role=user.role,status=user.status, parish=user.parish, profile_pic=user.profile_pic)
        )
    @strawberry.mutation 
    async def upload_profile_pic(self,user_id:int, file:Upload) -> UploadProfilePicResponse:
        db = SessionLocal()
        user = db.query(User).get(user_id)
        if not user:
            raise Exception("User not found.")
        
        allowed_types = ['jpeg','png','jpg']
        file_type = imghdr.what(file.file)
        if file_type not in allowed_types:
            raise Exception("Invalid file type. Only png, jpeg,jpg are allowed.")
        #validate file size(max 500KB)
        file.file.seek(0,2)
        file_size = file.file.tell()
        if file_size > 500 * 1024:
            raise Exception("File too large. Maximum allowed size is 500KB.")
        
        file.file.seek(0)
        contents = await file.read()
        filename = f"user_{user_id}_profile.{file_type}"
        filepath = f"static/profile_pics/{filename}"
        with open(filepath, "wb") as f:
            f.write(contents) 
        # Update the user in DB
      
        user.profile_pic = filename
        db.commit()
        db.refresh(user)

        return UploadProfilePicResponse(
            message="Profile picture updated successfully!",
            user=UserType(
                id=user.id,
                name=user.name,
                email=user.email,
                phonenumber=user.phonenumber,
                dateofbirth=user.dateofbirth,
                idnumber=user.idnumber,
                baptismref=user.baptismref,
                role=user.role,
                parish=user.parish,
                status=user.status,
                profile_pic=user.profile_pic,
        )
    )

    @strawberry.mutation
    def reset_password(self, info:Info, input: ResetPasswordInput) -> UserType:
        user = get_current_user(info)
        if not user or user.email != input.email:
            raise Exception("Unauthorized: Token mismatch or invalid user")
        db = SessionLocal()
        db_user = get_user_by_email(db, input.email)
        if not db_user:
            raise Exception("User not found")
        if not pwd_context.verify(input.old_password, db_user.password):
            raise Exception("Old password is incorrect")

        db_user.password = pwd_context.hash(input.new_password)
        db.commit()
        db.refresh(db_user)
        return UserType(id=user.id,name=user.name,email=user.email,phonenumber=user.phonenumber,role=user.role)
    
    @strawberry.mutation
    def transition_parish_member(self,info:Info,user_id:int) -> UserType:
        db = SessionLocal()
        user = get_user_by_id(info)

        if not (user or can_register_users(user)):
            print(user)
            raise Exception(f"User with id {user_id} not found")

        if user.dateofbirth is None:
            raise Exception("Date of birth not provided")

        current_year = datetime.datetime.now().year
        birth_year = user.dateofbirth.year
        age = current_year - birth_year

        if age > 26:
            user.status = UserStatus.transitioned_member
            db.commit()
            db.refresh(user)

        return user
        

schema = strawberry.Schema(query=UserQuery, mutation=UserMutation)
