# FastAPI Todo API

一个基于 **FastAPI + SQLAlchemy + JWT** 的待办事项 RESTful API。

## 技术栈

| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架，自动生成 Swagger 文档 |
| **SQLAlchemy** | ORM，操作 SQLite 数据库 |
| **Pydantic** | 请求/响应数据校验 |
| **JWT (python-jose)** | Token 无状态认证 |
| **bcrypt** | 密码加密存储 |
| **pytest + httpx** | 单元测试 |

## 快速开始

### 1. 安装依赖

`ash
pip install -r requirements.txt
`

### 2. 启动服务

`ash
python main.py
`

访问 **http://localhost:8000/docs** 查看 Swagger API 文档。

### 3. 运行测试

`ash
pytest test_main.py -v
`

## API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /register | 用户注册 | ❌ |
| POST | /login | 用户登录，获取 JWT Token | ❌ |
| GET | /me | 获取当前用户信息 | ✅ |
| GET | /todos | 获取待办列表 | ✅ |
| POST | /todos | 创建待办 | ✅ |
| GET | /todos/{id} | 获取待办详情 | ✅ |
| PUT | /todos/{id} | 更新待办 | ✅ |
| DELETE | /todos/{id} | 删除待办 | ✅ |

## 项目结构

`
├── main.py          # 应用入口，路由注册
├── database.py      # 数据库连接与会话管理
├── models.py        # SQLAlchemy 数据模型
├── schemas.py       # Pydantic 数据校验模型
├── auth.py          # JWT 认证 + bcrypt 密码加密
├── crud.py          # 业务逻辑（增删改查）
├── test_main.py     # 14 个测试用例
└── requirements.txt # 依赖清单
`

## 项目亮点（面试用）

- ✅ 分层架构（路由 / 业务 / 数据分离）
- ✅ JWT 无状态认证
- ✅ 密码 bcrypt 哈希存储（不存明文）
- ✅ 用户数据隔离（只能操作自己的待办）
- ✅ RESTful API 设计规范
- ✅ 14 个单元测试覆盖认证、CRUD、权限场景