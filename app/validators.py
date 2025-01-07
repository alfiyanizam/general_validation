import re

from fastapi import HTTPException, APIRouter, UploadFile
import phonenumbers
from PIL import Image  # To check dimensions
import os
import dns.resolver

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




def validate_placename(placename: str):
    """
    Validate place name to ensure it contains only alphabets, spaces, hyphens, and apostrophes,
    meets length requirements, and is not empty.
    """
    if not placename:
        raise HTTPException(
            status_code=400,
            detail="Place name cannot be empty."
        )
    
    # Updated regex to allow alphabets, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s'-]+$", placename):
        raise HTTPException(
            status_code=400,
            detail="Place name must contain only alphabets, spaces, hyphens, and apostrophes."
        )
    
    # Minimum length check
    if len(placename) < 3:
        raise HTTPException(
            status_code=400,
            detail="Place name must be at least 3 characters long."
        )
    
    # Maximum length check
    if len(placename) > 50:
        raise HTTPException(
            status_code=400,
            detail="Place name cannot exceed 50 characters."
        )
    
    return True




def validate_emailid(emailid: str):
    """
    Validate email ID to ensure it follows standard email formatting and includes a valid domain.
    """
    if not emailid:
        raise HTTPException(
            status_code=400,
            detail="Email ID cannot be empty."
        )
        
    # Check if the email length is within the valid range
    if len(emailid) > 254:
        raise HTTPException(
            status_code=400,
            detail="Email ID exceeds the maximum allowed length of 254 characters."
        )
        
    # Check if the email contains uppercase letters
    if any(char.isupper() for char in emailid):
        raise HTTPException(
            status_code=400,
            detail="Email ID must not contain uppercase letters."
        )

    # Validate email format
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", emailid):
        raise HTTPException(
            status_code=400,
            detail="Invalid email ID format."
        )

    # Extract domain from the email
    domain = emailid.split('@')[-1]

    # Validate if the domain has DNS records (basic check for MX records)
    try:
        dns.resolver.resolve(domain, 'MX')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain in email: {domain} does not have MX records."
        )
    
    return True
        
#install and import phonenumbers library version phonenumbers=8.13.52
def validate_phonenumber(phonenumber: str):
    """
    Validate phone number to ensure it follows international standards and is valid.
    """
    if not phonenumber:
        raise HTTPException(
            status_code=400,
            detail="Phone number cannot be empty."
        )

    try:
        # Parse the phone number using the phonenumbers library
        parsed_number = phonenumbers.parse(phonenumber, None)  # None allows parsing without a default region
        
        # Check if the phone number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            raise HTTPException(
                status_code=400,
                detail="Invalid phone number."
            )
        
        # Optional: Check if it's a mobile number
        if not phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE:
            raise HTTPException(
                status_code=400,
                detail="The provided phone number is not a mobile number."
            )
    except phonenumbers.NumberParseException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phone number format: {str(e)}"
        )
        
def validate_image(image: UploadFile):
    """
    Validate the uploaded image.
    - Ensure it's an image file.
    - Restrict file types to JPEG, PNG, etc.
    - Check file size.
    - Optionally validate image dimensions.
    - Check if the image is corrupted.
    """
    
    # 1. Validate file name (no spaces or special characters other than underscores)
    file_name = image.filename
    if not re.match(r'^[\w_]+\.[a-zA-Z0-9]+$', file_name):  # Allow only letters, numbers, and underscores
        raise HTTPException(
            status_code=400,
            detail="File name should not contain spaces or special characters other than underscores."
        )
        
    # 2. Validate file extension
    valid_extensions = [".jpg", ".jpeg", ".png",".gif"]
    file_extension = os.path.splitext(image.filename)[1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file_extension}. Allowed types: {valid_extensions}"
        )

    # 3. Validate file size
    file_size = len(image.file.read())
    max_size_in_mb = 1  # Set the max size (e.g., 1 MB)
    if file_size > max_size_in_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail=f"File size exceeds {max_size_in_mb} MB limit."
        )

    # Reset the file pointer after reading
    image.file.seek(0)

    # 4. Validate image dimensions (optional)
    try:
        img = Image.open(image.file)
        img.verify()  # Verifies that the image is not corrupted
        
        # Reset the file pointer for further processing
        image.file.seek(0)
        img = Image.open(image.file)  # Open again for actual processing
        width, height = img.size
        
        # Define minimum and maximum allowed dimensions
        min_width, min_height = 300, 300  # Example minimum dimensions
        max_width, max_height = 1920, 1080  # Example maximum dimension
       
       # Validate maximum dimensions
        if width < min_width or height < min_height:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
                       f"Uploaded image is {width}x{height}px."
            )
        if width > max_width or height > max_height:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions exceed {max_width}x{max_height}px limit. Uploaded image is {width}x{height}px.",
            )
            
       # Validate minimum dimensions
        if width < min_width or height < min_height:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
                       f"Uploaded image is {width}x{height}px."
            )
        if width < min_width or height < min_height:
            raise HTTPException(
                status_code=400,
                detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
                       f"Uploaded image is {width}x{height}px."
            )
            
    except Exception:
        raise HTTPException(
            status_code=400, detail="Invalid image file."
        )
    finally:
        # Reset the file pointer again after processing with PIL
        image.file.seek(0)

    return True
