import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahyre_project.settings')
django.setup()

import random
from faker import Faker
from users.models import CustomUser
from api.models import Spam

fake = Faker()

def populate_users(num_users=20):
    print("Starting user population...")
    fake.unique.clear()  # Reset Faker's unique constraints
    for i in range(num_users):
        try:
            name = fake.name()
            phone_number = fake.unique.msisdn()  # Generate realistic phone numbers
            email = fake.email()
            password = "password123"
            user = CustomUser.objects.create_user(
                username=phone_number,
                name=name,
                phone_number=phone_number,
                email=email,
                password=password
            )
            print(f"User {i+1}/{num_users} created: {user}")
        except Exception as e:
            print(f"Error creating user {i+1}: {e}")

def populate_contacts():
    print("Starting contact population...")
    users = list(CustomUser.objects.all())
    if len(users) < 2:
        print("Not enough users to populate contacts.")
        return

    for user in users:
        try:
            num_contacts = random.randint(3, 5)
            contacts = random.sample(users, min(num_contacts, len(users) - 1))
            for contact in contacts:
                if contact != user:  # Avoid self as contact
                    user.contacts.add(contact)
            print(f"Contacts added for user: {user}")
        except Exception as e:
            print(f"Error adding contacts for user {user}: {e}")

def populate_spam(num_spam=30):
    print("Starting spam population...")
    users = list(CustomUser.objects.all())
    if not users:
        print("No users found to mark spam.")
        return

    for i in range(num_spam):
        try:
            # Use existing phone numbers to ensure valid spam entries
            spam_number = random.choice(users).phone_number
            marked_by = random.choice(users)
            Spam.objects.create(phone_number=spam_number, marked_by=marked_by)
            print(f"Spam {i+1} created for number: {spam_number}")
        except Exception as e:
            print(f"Error creating spam {i+1}: {e}")

if __name__ == "__main__":
    print("Populating database...")
    populate_users(50)
    populate_contacts()
    populate_spam(100)
    print("Database population complete!")
