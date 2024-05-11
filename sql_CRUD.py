import random

from faker import Faker
from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, aliased

from models import User, Order, Product, OrderProduct


class Repo:
    def __init__(self, session: Session):
        self.session: Session = session

    def add_user(self,
                 telegram_id: int,
                 fullname: str,
                 language_code: str,
                 user_name: str = None,
                 referrer_id: int = None) -> User:
        stmt = select(User).from_statement(
            insert(User).values(
                telegram_id=telegram_id,
                fullname=fullname,
                language_code=language_code,
                user_name=user_name,
                referrer_id=referrer_id).returning(User)
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_=dict(fullname=fullname, user_name=user_name, )
            )
        )
        result = self.session.scalars(stmt).first()
        self.session.commit()
        return result

    def get_user_by_id(self, telegram_id: int):
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = self.session.execute(stmt)
        return result.scalar()

    def get_all_users(self):
        stmt = select(
            User).order_by(User.created_at.asc())
        # ).where(
        #     or_(User.language_code == 'en', User.language_code == 'fa'),
        #     User.user_name.ilike("pouria"),
        #     User.telegram_id > 0  # Replace 'having' with 'where' --> '.having(User.telegram_id > 0)'
        # ).order_by(
        #     User.created_at.desc()
        # ).limit(
        #     10
        # )
        result = self.session.execute(stmt)
        return result.scalars().all()

    def add_order(self, user_id: int) -> Order:
        stmt = select(Order).from_statement(
            insert(Order).values(user_id=user_id).returning(Order)
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def add_product(self, title: str, description: str, price: float) -> Product:
        stmt = select(Product).from_statement(
            insert(Product)
            .values(title=title, description=description, price=price)
            .returning(Product)
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def add_product_to_order(self, order_id: int, product_id: int, quantity: int):
        stmt = (insert(OrderProduct)
                .values(order_id=order_id, product_id=product_id, quantity=quantity)
                .returning(OrderProduct))

        self.session.execute(stmt)
        self.session.commit()

    def select_all_invited_users(self):
        ParentUser = aliased(User)
        RefferralUser = aliased(User)
        stmt = (select(
            ParentUser.fullname.label("parent_name"),
            RefferralUser.fullname.label("refferal_name"))
        .join(
            RefferralUser, RefferralUser.referrer_id == ParentUser.telegram_id
        )
        .where(
            # ParentUser.referrer_id.isnot(None)
        ))
        result = self.session.execute(stmt)
        return result.all()


    def get_all_user_orders(self, telegram_id: int):
        stmt = (
            select(Order, User, Product, OrderProduct.quantity)
            .join(User.orders)
            .join(Order.products)
            .join(Product)
            .where(User.telegram_id == telegram_id)
        )
        result = self.session.execute(stmt)
        return result.all()


# def seed_fake_data(repo: Repo):
#     Faker.seed(0)  # using seed(0) to generate the same data everytime
#     faker = Faker()
#     users = []
#     orders = []
#     products = []
#     for i in range(10):
#         referrer_id = None if not users else users[-1].telegram_id
#         user = repo.add_user(
#             telegram_id=faker.pyint(),
#             fullname=faker.name(),
#             language_code=faker.language_code(),
#             user_name=faker.user_name(),
#             referrer_id=referrer_id,
#         )
#         users.append(user)
#     for i in range(10):
#         order = repo.add_order(
#             user_id=random.choice(users).telegram_id,
#         )
#         orders.append(order)
#
#     # add products
#     for i in range(10):
#         product = repo.add_product(
#             title=faker.word(),
#             description=faker.sentence(),
#             price=faker.pyint(),
#         )
#         products.append(product)
#     # add products to orders
#     for order in orders:
#         for product in products:
#             repo.add_product_to_order(
#                 order_id=order.order_id,
#                 product_id=product.product_id,
#                 quantity=faker.pyint(),
#             )


if __name__ == '__main__':
    from sqlalchemy import create_engine, URL, text
    from sqlalchemy.orm import sessionmaker
    from environs import Env

    env = Env()
    env.read_env('.env')

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=env.str("POSTGRES_USER"),
        password=env.str("POSTGRES_PASSWORD"),
        host=env.str("DATABASE_HOST"),
        port=5432,
        database=env.str("POSTGRES_DB"),
    ).render_as_string(hide_password=False)

    engine = create_engine(url, echo=True)
    session_pool = sessionmaker(bind=engine, expire_on_commit=False)
    # with session_pool() as session:
    #     repo = Repo(session=session)
    # test for add_user (previous one)
    # repo.add_user(telegram_id=1,
    #               fullname='pouria',
    #               language_code='fa',
    #               user_name='pouRIA')
    # test for get_user_by_id
    # user = repo.get_user_by_id(telegram_id=1)
    # print(user.telegram_id, user.fullname, user.language_code, user.user_name, user.referrer_id)
    # test for get_all_users
    # users = repo.get_all_users()
    # print(users)
    # test for add_user (new one)
    # repo.add_user(telegram_id=2,
    #               fullname='alireza jahan',
    #               language_code='en',
    #               user_name='aliJ')
    # adding fake data
    # with session_pool() as session:
    #     repo = Repo(session)
    #     seed_fake_data(repo)
    #     # todo: learning how to create migration that could be inserting data in database
    # referral users and so on
    # with session_pool() as session:
    #     repo = Repo(session)
    # for row in repo.select_all_invited_users():
    #     print(f"parent : {row.parent_name} | Referral: {row.refferal_name}")
    # select user with related orders and products
    # with session_pool() as session:
    #     repo = Repo(session)
    #     for user in repo.get_all_users():
    #         print(f"User: {user.fullname}({user.telegram_id})")
    #         for order in user.orders:
    #             print(f"    order: {order.order_id}")
    #             for product in order.products:
    #                 print(f"    product: {product.product.title}")

    with session_pool() as session:
        repo = Repo(session)

        user_orders = repo.get_all_user_orders(telegram_id=4969)
        for order, user, product, quantity in user_orders:
            print(f"Order: {order.order_id} - {user.fullname} - {product.title} - amound: {quantity}")



