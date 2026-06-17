from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User, Todo
from schemas import UserCreate, TodoCreate, TodoUpdate
from auth import hash_password


# --------------------------------------------------
# 用户操作
# --------------------------------------------------

def create_user(db: Session, user_data: UserCreate) -> User:
    """注册新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建用户
    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()      # 提交事务
    db.refresh(user) # 刷新对象，获取数据库生成的 id
    return user


# --------------------------------------------------
# Todo 操作
# --------------------------------------------------

def create_todo(db: Session, todo_data: TodoCreate, user: User) -> Todo:
    """创建待办（属于当前用户）"""
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description or "",
        owner_id=user.id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def get_user_todos(db: Session, user: User) -> list[Todo]:
    """获取当前用户的所有待办"""
    return db.query(Todo).filter(Todo.owner_id == user.id).all()


def get_todo(db: Session, todo_id: int, user: User) -> Todo:
    """获取单个待办（只能获取自己的）"""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在",
        )
    return todo


def update_todo(db: Session, todo_id: int, todo_data: TodoUpdate, user: User) -> Todo:
    """更新待办（只能更新自己的）"""
    todo = get_todo(db, todo_id, user)  # 复用查询，自动校验所有权

    # 只更新用户传了值的字段
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo_id: int, user: User):
    """删除待办（只能删除自己的）"""
    todo = get_todo(db, todo_id, user)
    db.delete(todo)
    db.commit()