import re
from fastapi import HTTPException, APIRouter, UploadFile
import phonenumbers
from PIL import Image  # To check dimensions
import os
import dns.resolver

router = APIRouter()

def validate_placename(placename: str):
    """
    Validate place name to ensure it contains only alphabets, 
    meets length requirements, and is not empty.
    """
    if not placename:
        raise HTTPException(
            status_code=400,
            detail="Place name cannot be empty."
        )
    
    if not re.match(r"^[a-zA-Z\s]+$", placename):
        raise HTTPException(
            status_code=400,
            detail="District name must contain only alphabets and spaces."
        )
    
    if len(placename) < 3:
        raise HTTPException(
            status_code=400,
            detail="District name must be at least 3 characters long."
        )
    
    if len(placename) > 50:
        raise HTTPException(
            status_code=400,
            detail="Place name cannot exceed 50 characters."
        )



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