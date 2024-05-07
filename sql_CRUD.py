from sqlalchemy import insert, select, or_
from sqlalchemy.orm import Session

from models import User

class Repo:
    def __init__(self, session: Session):
        self.session: Session = session

    def add_user(self,
                 telegram_id: int,
                 fullname: str,
                 language_code: str,
                 user_name: str = None,
                 referrer_id: int = None):
        stmt = insert(User).values(telegram_id=telegram_id,
                                   fullname=fullname,
                                   language_code=language_code,
                                   user_name=user_name,
                                   referrer_id=referrer_id
                                   )
        print(stmt)
        self.session.execute(stmt)
        self.session.commit()

    def get_user_by_id(self, telegram_id: int):
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = self.session.execute(stmt)
        return result.scalar()

    def get_all_users(self):
        stmt = select(
            User
        ).where(
            or_(User.language_code == 'en', User.language_code == 'fa'),
            User.user_name.ilike("pouria"),
            User.telegram_id > 0  # Replace 'having' with 'where' --> '.having(User.telegram_id > 0)'
        ).order_by(
            User.created_at.desc()
        ).limit(
            10
        )
        result = self.session.execute(stmt)
        return result.scalars().all()


if __name__ == '__main__':
    from sqlalchemy import create_engine,URL,text
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
    session_pool = sessionmaker(bind=engine)
    with session_pool() as session:
        repo = Repo(session=session)
        # test for add_user
        # repo.add_user(telegram_id=1,
        #               fullname='pouria',
        #               language_code='fa',
        #               user_name='pouRIA')
        # test for get_user_by_id
        # user = repo.get_user_by_id(telegram_id=1)
        # print(user.telegram_id, user.fullname, user.language_code, user.user_name, user.referrer_id)
        # test for get_all_users
        users = repo.get_all_users()
        print(users)