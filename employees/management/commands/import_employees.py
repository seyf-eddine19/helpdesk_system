import pandas as pd
import secrets
import string
import re

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from datetime import datetime

from employees.models import Employee


User = get_user_model()


class Command(BaseCommand):
    help = "Import Employees + Send Credentials Email"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    # -------------------------------------------------
    @transaction.atomic
    def handle(self, *args, **kwargs):

        df = pd.read_csv(kwargs["file"], sep=';')
        df.columns = df.columns.str.strip() 

        for _, row in df.iterrows():

            email = str(row["email"]).strip()

            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f"Skipped: {email}")
                )
                continue

            username = str(row["username"]).strip()
            username = self.make_valid_username(username)
            password = self.generate_password()

            # ---------- Create User ----------
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            # ---------- Group ----------
            group_name = row.get("group_type")
            if group_name:
                group, _ = Group.objects.get_or_create(
                    name=group_name
                )
                user.groups.add(group)

            # ---------- Employee ----------
            employee = Employee.objects.create(
                user=user,
                full_name_ar=row.get("full_name_ar"),
                full_name_en=row.get("full_name_en"),
                birth_date=row.get("birth_date"),
                id_number=row.get("id_number"),
                address=row.get("address"),
                job_title=row.get("job_title"),
                job_number=row.get("job_number"),
                department=row.get("department"),
                phone_number=row.get("phone_number"),
            )

            # ---------- Reset Link ----------
            uidb64 = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            reset_link = "http://localhost:8000" + reverse(
                    "password_reset_confirm",
                    kwargs={
                        "uidb64": uidb64,
                        "token": token,
                    },
                )

            # ---------- Email HTML ----------
            html_content = render_to_string(
                "account/employee_credentials.html",
                {
                    "user": employee,
                    "username": username,
                    "password": password,
                    "reset_link": reset_link,
                    "year": datetime.now().year,
                },
            )

            subject = "Your HelpDesk Account Credentials"

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body="Account created",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )

            email_msg.attach_alternative(
                html_content,
                "text/html"
            )

            email_msg.send()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created & emailed: {email}"
                )
            )

    # -------------------------------------------------
    def generate_password(self, length=10):

        chars = (
            string.ascii_letters
            + string.digits
            + "!@#$%"
        )

        return "".join(
            secrets.choice(chars)
            for _ in range(length)
        )

    def make_valid_username(self, username):
        """
        Ensure username is valid (alphanumeric + underscores)
        and unique in the database.
        """
        # Remove invalid characters
        username = re.sub(r'[^a-zA-Z0-9_]', '_', username)

        # Make sure it's unique
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1

        return username
    
# python manage.py import_employees employees_random_10.csv
