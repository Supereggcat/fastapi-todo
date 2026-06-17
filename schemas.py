from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

# --------------------------------------------------
# 用户相关 Schema（数据校验模型）
# --------------------------------------------------

class UserCreate(BaseModel):
    """用户注册请求体"""
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("用户名至少3个字符")
        if len(v) > 20:
            raise ValueError("用户名不能超过20个字符")
        return v

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError("密码至少6个字符")
        return v


class UserResponse(BaseModel):
    """用户信息返回体（隐藏了密码）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    """登录返回的 JWT Token"""
    access_token: str
    token_type: str = "bearer"


# --------------------------------------------------
# Todo 相关 Schema
# --------------------------------------------------

class TodoCreate(BaseModel):
    """创建待办的请求体"""
    title: str
    description: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("标题不能为空")
        return v


class TodoUpdate(BaseModel):
    """更新待办的请求体（所有字段可选）"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    """待办返回体"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    owner_id: int