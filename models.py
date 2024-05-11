from datetime import datetime
from typing import Optional

from sqlalchemy import BIGINT, VARCHAR, func, ForeignKey, Integer, MetaData, DECIMAL
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr
from typing_extensions import Annotated


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class TableNameMixin:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"


int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
user_fk = Annotated[int, mapped_column(BIGINT, ForeignKey('users.telegram_id', ondelete="SET NULL"))]
str_255 = Annotated[str, mapped_column(VARCHAR(255))]


class User(Base, TimestampMixin, TableNameMixin):
    # telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    telegram_id: Mapped[int_pk]
    fullname: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    language_code: Mapped[str] = mapped_column(VARCHAR(10))
    referrer_id: Mapped[Optional[user_fk]]

    orders: Mapped[list["Order"]] = relationship(back_populates='user')


class Product(Base, TableNameMixin, TimestampMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(3000))
    price: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4))


class Order(Base, TableNameMixin, TimestampMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]

    products: Mapped[list["OrderProduct"]] = relationship()
    user: Mapped["User"] = relationship(back_populates="orders")


class OrderProduct(Base, TableNameMixin):
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.product_id', ondelete="CASCADE"),
                                            primary_key=True)
    quantity: Mapped[int]

    product: Mapped["Product"] = relationship()
