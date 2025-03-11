import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from config import DATABASE_PATH

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True, nullable=False)
    sender = Column(String)
    subject = Column(String)
    to_address = Column(String)
    date = Column(DateTime)
    snippet = Column(String)

engine = create_engine(f'sqlite:///{DATABASE_PATH}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_email(email_info):
    email = Email(
        message_id=email_info["message_id"],
        sender=email_info["sender"],
        subject=email_info["subject"],
        to_address=email_info.get("to", "Unknown"),
        date=email_info["date"],
        snippet=email_info["snippet"]
    )

    try:
        session.add(email)
        session.commit()
        print(f"Email saved: {email.subject}")
    except IntegrityError:
        session.rollback()
        print(f"Email already exists in the database: {email.subject}")
