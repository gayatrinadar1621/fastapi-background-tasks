# create engine
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config

engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True
)

# logic for generating session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

asyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with asyncSessionLocal() as session:
        yield session