from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User
from schemas import UserCreate, UserResponse, Token, TodoCreate, TodoUpdate, TodoResponse
from auth import create_access_token, verify_password, get_current_user
from crud import create_user, get_user_todos, create_todo, get_todo, update_todo, delete_todo

# --------------------------------------------------
# 应用初始化
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Todo App",
    description="一个完整的 Todo API，包含用户认证与 CRUD 操作",
    version="1.0.0",
)


# --------------------------------------------------
# 用户认证路由
# --------------------------------------------------

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    '''用户注册
    - **username**: 用户名（3-20个字符）
    - **password**: 密码（至少6个字符）
    密码会自动哈希存储，不会保存明文。
    '''
    return create_user(db, user_data)


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    '''用户登录
    使用 OAuth2 标准密码流。
    返回 JWT Token，后续请求需要在 Header 中携带：
    Authorization: Bearer <token>
    '''
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # Token 中的 sub 使用字符串格式（JWT 标准推荐）
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    '''获取当前登录用户的信息'''
    return current_user


# --------------------------------------------------
# Todo CRUD 路由（需要登录）
# --------------------------------------------------

@app.get("/todos", response_model=list[TodoResponse])
def list_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''获取当前用户的所有待办事项'''
    return get_user_todos(db, current_user)


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo_endpoint(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''创建一条新的待办事项'''
    return create_todo(db, todo_data, current_user)


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo_endpoint(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''获取单条待办详情'''
    return get_todo(db, todo_id, current_user)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo_endpoint(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''更新待办事项（部分更新，只传要改的字段即可）'''
    return update_todo(db, todo_id, todo_data, current_user)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_endpoint(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''删除待办事项'''
    delete_todo(db, todo_id, current_user)


# --------------------------------------------------
# 启动入口
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)