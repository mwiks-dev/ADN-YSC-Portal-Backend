# test_mailer.py — run with: python test_mailer.py
import asyncio
from mailer.service import send_welcome_email

asyncio.run(send_welcome_email("your.test@email.com", "Test User"))