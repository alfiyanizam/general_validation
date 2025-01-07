import re
from fastapi import HTTPException

def validate_pincode(pincode: str) -> None:
    """
    Validates a pincode to ensure it meets the required criteria:
    - Must be exactly 6 digits
    - Must be numeric

    Args:
        pincode (str): The pincode to validate

    Raises:
        HTTPException: If validation fails
    """
    if not re.match(r"^\d{6}$", pincode):
        raise HTTPException(
            status_code=400,
            detail="Invalid pincode: It must be exactly 6 numeric digits."
        )


# validation for address
def validate_address(address: str) -> None:
    """
    Validates an address to ensure it meets the required criteria:
    - Must be at least 5 characters long
    - Must not exceed 100 characters
    - Must not contain special characters other than space, comma, or hyphen

    Args:
        address (str): The address to validate

    Raises:
        HTTPException: If validation fails
    """
    if len(address) < 5 or len(address) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid address: It must be between 5 and 100 characters."
        )
    if not re.match(r"^[a-zA-Z0-9\s,.-]+$", address):
        raise HTTPException(
            status_code=400,
            detail="Invalid address: Only letters, numbers, spaces, commas, periods, and hyphens are allowed."
        )


VALID_GENDERS = {"male", "female", "other"}  # Use lowercase values for consistent validation

def validate_gender(gender: str) -> str:
    """
    Validates the gender field to ensure it matches one of the predefined options
    and has a minimum length of 4 characters. Converts uppercase input to lowercase.

    Args:
        gender (str): The gender value to validate.

    Returns:
        str: The validated and normalized gender value in lowercase.

    Raises:
        HTTPException: If the gender value is invalid.
    """
    # Convert to lowercase
    gender = gender.lower()

    # Check minimum length
    if len(gender) < 4:
        raise HTTPException(
            status_code=400,
            detail="Invalid gender: The value must be at least 4 characters long."
        )

    # Validate against allowed options
    if gender not in VALID_GENDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid gender: Allowed values are {', '.join(VALID_GENDERS)}."
        )

    return gender



# validation for firstname,middlename and lastname 
def validate_name(name: str, field_name: str) -> None:
    """
    Validates a name field (firstname, lastname, middlename).
    
    Args:
        name (str): The name value to validate.
        field_name (str): The name of the field (e.g., firstname, lastname).

    Raises:
        HTTPException: If the name value is invalid.
    """
    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: It must be at least 2 characters long."
        )

    if len(name) > 50:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: It must not exceed 50 characters."
        )

    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: Only alphabetic characters, spaces, hyphens, and apostrophes are allowed."
        )



# validation for password
def validate_password(password: str) -> str:
    """
    Validates the password to ensure it meets the specified criteria.

    Args:
        password (str): The password to validate.

    Returns:
        str: The validated password.

    Raises:
        HTTPException: If any validation fails.
    """
    # 1. Check minimum length
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long."
        )

    # 2. Check if the password includes at least one number
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one number."
        )

    # 3. Check if the password includes at least one lowercase letter
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one lowercase letter."
        )

    # 4. Check if the password includes at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one uppercase letter."
        )

    # 5. Check if the password includes at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one special character."
        )

    return password