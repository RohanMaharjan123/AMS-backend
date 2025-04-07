# users/services.py
import uuid
from django.db import connection, IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from core.models import UserProfile  # Import UserProfile


def get_raw_login_queries(email, password):
    """
    Retrieves a user from the database by email and verifies the password.

    Args:
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        User or None: The User object if the credentials are valid, None otherwise.
    """
    User = get_user_model()
    user = None

    with connection.cursor() as cursor:
        try:
            # Retrieve user data from the database
            user_query = f"""
                SELECT id, password, email, role, is_staff, is_active, is_superuser
                FROM {User._meta.db_table}
                WHERE email = %s;
            """
            cursor.execute(user_query, (email,))
            user_data = cursor.fetchone()

            if user_data:
                (
                    user_id,
                    hashed_password,
                    user_email,
                    user_role,
                    is_staff,
                    is_active,
                    is_superuser,
                ) = user_data

                # Verify the password against the hashed password
                if check_password(password, hashed_password):
                    # Password is correct, create a user object
                    user = User(
                        id=user_id,
                        email=user_email,
                        role=user_role,
                        is_staff=is_staff,
                        is_active=is_active,
                        is_superuser=is_superuser,
                    )
                    user.password = hashed_password
                else:
                    user = None  # Password incorrect
            else:
                user = None  # User not found

        except Exception as e:
            print(f"An error occurred during login: {e}")
            user = None

    return user


def get_raw_register_queries(
    first_name, last_name, email, password, phone, dob, gender, address, role
):
    """
    Registers a new user and their profile in the database.

    Args:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (str): The user's email.
        password (str): The user's password.
        phone (str): The user's phone number.
        dob (str): The user's date of birth.
        gender (str): The user's gender.
        address (str): The user's address.
        role (str): The user's role.

    Returns:
        tuple: (success, data) where success is a boolean indicating success,
               and data is a dictionary containing either the user ID or an error message.
    """
    User = get_user_model()
    with connection.cursor() as cursor:
        try:
            # Check if the email already exists
            email_check_query = f"""
                SELECT 1 FROM {User._meta.db_table}
                WHERE email = %s;
            """
            cursor.execute(email_check_query, (email,))
            email_exists = cursor.fetchone()

            if email_exists:
                return False, {"email": ["This email already exists."]}

            # Insert the new user into the database
            insert_user_query = f"""
                INSERT INTO {User._meta.db_table} (id, email, password, is_staff, is_active, date_joined, role, created, modified, is_superuser)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            user_id = uuid.uuid4()
            hashed_password = make_password(password)  # Hash the password
            is_staff = False
            is_active = True
            is_superuser = False
            date_joined = timezone.now()
            created = timezone.now()
            modified = timezone.now()

            params = (
                user_id,
                email,
                hashed_password,
                is_staff,
                is_active,
                date_joined,
                role,
                created,
                modified,
                is_superuser,
            )
            cursor.execute(insert_user_query, params)

            # Insert the user profile into the database
            insert_profile_query = f"""
                INSERT INTO core_userprofile (id, user_id, first_name, last_name, phone, date_of_birth, gender, address, created, modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            profile_id = uuid.uuid4()
            profile_params = (
                profile_id,
                user_id,
                first_name,
                last_name,
                phone,
                dob,
                gender,
                address,
                created,
                modified,
            )
            cursor.execute(insert_profile_query, profile_params)

            return True, {"id": str(user_id)}  # Registration successful

        except IntegrityError as e:
            return False, {"error": "An error occurred during registration."}
        except Exception as e:
            return False, {"error": str(e)}


def get_raw_user_list_queries():
    """
    Retrieves a list of users from the database (excluding super admins).

    Returns:
        list: A list of dictionaries, where each dictionary represents a user.
    """
    User = get_user_model()
    with connection.cursor() as cursor:
        query = f"""
            SELECT id, email, is_staff, is_active, date_joined, role
            FROM {User._meta.db_table}
            WHERE role != 'super_admin';
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return users


def get_raw_user_detail_queries(user_id):
    """
    Retrieves a single user from the database by ID.

    Args:
        user_id (str): The ID of the user to retrieve.

    Returns:
        dict or None: A dictionary representing the user, or None if not found.
    """
    User = get_user_model()
    with connection.cursor() as cursor:
        query = f"""
            SELECT id, email, is_staff, is_active, date_joined, role
            FROM {User._meta.db_table}
            WHERE id = %s;
        """
        cursor.execute(query, (user_id,))
        columns = [col[0] for col in cursor.description]
        user = cursor.fetchone()
        if user:
            return dict(zip(columns, user))
        return None


def update_raw_user_queries(user_id, data):
    """
    Updates an existing user in the database.

    Args:
        user_id (str): The ID of the user to update.
        data (dict): A dictionary containing the fields to update.

    Returns:
        tuple: (success, data) where success is a boolean indicating success,
               and data is a dictionary containing either the updated user data or an error message.
    """
    User = get_user_model()
    with connection.cursor() as cursor:
        try:
            update_query = f"""
                UPDATE {User._meta.db_table}
                SET email = %s, is_staff = %s, is_active = %s, role = %s, modified = NOW()
                WHERE id = %s;
            """
            params = (
                data.get("email"),
                data.get("is_staff"),
                data.get("is_active"),
                data.get("role"),
                user_id,
            )
            cursor.execute(update_query, params)
            return True, {}  # Update successful
        except IntegrityError as e:
            return False, {"error": "An error occurred during user update."}
        except Exception as e:
            return False, {"error": str(e)}


def delete_raw_user_queries(user_id):
    """
    Deletes a user from the database.

    Args:
        user_id (str): The ID of the user to delete.

    Returns:
        bool: True if the user was deleted, False otherwise.
    """
    User = get_user_model()
    with connection.cursor() as cursor:
        delete_query = f"""
            DELETE FROM {User._meta.db_table}
            WHERE id = %s;
        """
        cursor.execute(delete_query, (user_id,))
        return cursor.rowcount > 0  # True if at least one row was deleted

