from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite 数据库文件路径
DATABASE_URL = "sqlite:///./todos.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False} 是 SQLite 特有的配置
# 因为 FastAPI 可能多线程访问 SQLite，需要允许跨线程
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal 是一个工厂函数
# 每次调用 SessionLocal() 都会创建一个新的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有 ORM 模型的基类
# 继承这个类的子类会自动映射到数据库表
class Base(DeclarativeBase):
    pass

# 依赖注入函数 -- FastAPI 的核心特性
# 每次请求时创建一个新的数据库会话，请求结束后关闭
# yield 关键字让 FastAPI 的依赖注入系统管理生命周期
def get_db():
    db = SessionLocal()  # 创建新会话
    try:
        yield db          # 把会话注入到路由函数
    finally:
        db.close()        # 请求结束后关闭会话