import re

from fastapi import HTTPException, APIRouter, UploadFile
from datetime import datetime
import phonenumbers



class DateValidator:
    """
    A class to validate date inputs in multiple formats, including time:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - MM/DD/YYYY
    - With optional time in HH:mm or HH:mm:ss or HH:mm:ss AM/PM
    """

    def __init__(self, date_string: str):
        self.date_string = date_string
        # Supported date and time formats
        self.supported_formats = [
            "%Y-%m-%d",                  # Date only
            "%Y-%m-%d %H:%M",           # Date and time (24-hour)
            "%Y-%m-%d %H:%M:%S",        # Date and time with seconds
            "%d/%m/%Y",                 # Date only
            "%d/%m/%Y %H:%M",           # Date and time (24-hour)
            "%d/%m/%Y %H:%M:%S",        # Date and time with seconds
            "%m/%d/%Y",                 # Date only
            "%m/%d/%Y %H:%M",           # Date and time (24-hour)
            "%m/%d/%Y %H:%M:%S",        # Date and time with seconds
            "%Y-%m-%d %I:%M %p",        # Date and time (12-hour with AM/PM)
            "%Y-%m-%d %I:%M:%S %p",     # Date and time with seconds and AM/PM
            "%d/%m/%Y %I:%M %p",        # Date and time (12-hour with AM/PM)
            "%d/%m/%Y %I:%M:%S %p",     # Date and time with seconds and AM/PM
            "%m/%d/%Y %I:%M %p",        # Date and time (12-hour with AM/PM)
            "%m/%d/%Y %I:%M:%S %p"      # Date and time with seconds and AM/PM
        ]

    def determine_format(self) -> str:
        """
        Determines the likely format of the date string by attempting to parse it.
        """
        for fmt in self.supported_formats:
            try:
                # Try parsing with the current format
                datetime.strptime(self.date_string, fmt)
                return fmt
            except ValueError:
                continue

        raise HTTPException(
            status_code=400,
            detail="Unable to determine the format of the date."
        )

    def validate_calendar_date(self, date_format: str) -> datetime:
        """
        Ensures the date and time exist in the calendar. Returns the parsed date if valid.
        """
        try:
            return datetime.strptime(self.date_string, date_format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date or time. Ensure the input matches the format {date_format}."
            )

    def validate_not_future_year(self, date_obj: datetime) -> None:
        """
        Ensures the year in the date is not in the future.
        """
        current_year = datetime.now().year
        if date_obj.year > current_year:
            raise HTTPException(
                status_code=400,
                detail="Invalid year. Year cannot be in the future."
            )

    def validate(self) -> None:
        """
        Perform all validations on the date and time.
        """
        date_format = self.determine_format()
        date_obj = self.validate_calendar_date(date_format)
        self.validate_not_future_year(date_obj)
        print(f"Date and time '{self.date_string}' are valid and follow the format {date_format}.")  

class BaseValidator: 
    """Base class for all validators to ensure a unified interface.""" 
 
    def validate(self, value): 
        """This method should be implemented in child classes.""" 
        raise NotImplementedError("Subclasses should implement this method.") 
 
    def raise_validation_error(self, message: str): 
        """Helper method to raise validation error.""" 
        raise HTTPException( 
            status_code=422,  # HTTP status code for Unprocessable Entity 
            detail={"error": message}, 
        ) 
 
 
class NumericValidator(BaseValidator): 
    """Validates if the value is a numeric (integer) value.""" 
 
    def __init__(self, min_value: float = None, max_value: float = None): 
        self.min_value = min_value 
        self.max_value = max_value 
 
    def validate(self, value): 
        try: 
            # Check if the value is a valid numeric type (int or float) 
            float_value = float(value)  # Try to convert to a float 
        except ValueError: 
            self.raise_validation_error("Value must be a valid number.") 
         
        # Check if the value is within the specified min/max range 
        if self.min_value is not None and float_value < self.min_value: 
            self.raise_validation_error(f"Value must be greater than {self.min_value}.") 
        if self.max_value is not None and float_value > self.max_value: 
            self.raise_validation_error(f"Value must be less than {self.max_value}.") 
        return True 
     
class AgeValidator(NumericValidator): 
    """Validates that the value is a valid age (greater than or equal to 18).""" 
 
    def __init__(self, min_age: int = 18, max_age: int = 120): 
        super().__init__(min_value=min_age, max_value=max_age) 
 
    def validate(self, value): 
        super().validate(value) 
        # Additional check for the specific age range 
        if value < self.min_value: 
            self.raise_validation_error(f"Age must be at least {self.min_value}.") 
        elif value > self.max_value: 
            self.raise_validation_error(f"Age must be less than {self.max_value}.") 
        return True 
 
 
class DecimalValidator(BaseValidator): 
    """Validates if the value is a decimal number with optional precision.""" 
 
    def __init__(self, max_decimal_places: int = None): 
        self.max_decimal_places = max_decimal_places 
 
    def validate(self, value): 
        # Ensure value is a string or numeric type 
        value_str = str(value) 
         
        # Update regex pattern to allow negative numbers, integers, and decimals 
        regex = r"^-?\d+(\.\d{1," + (str(self.max_decimal_places) if self.max_decimal_places else "10") + "})?$" 
         
        if not re.match(regex, value_str): 
            self.raise_validation_error("Value must be a valid decimal number.") 
         
        return True 
 
 
class MinMaxLengthValidator(BaseValidator): 
    """Validates the minimum and maximum length of a string.""" 
 
    def __init__(self, min_length: int = None, max_length: int = None): 
        self.min_length = min_length 
        self.max_length = max_length 
 
    def validate(self, value): 
        if not isinstance(value, str): 
            self.raise_validation_error("Value must be a string.") 
 
        if self.min_length and len(value) < self.min_length: 
            self.raise_validation_error(f"String must be at least {self.min_length} characters long.") 
         
        if self.max_length and len(value) > self.max_length: 
            self.raise_validation_error(f"String must be at most {self.max_length} characters long.") 
         
        return True 
 
 
class AlphanumericValidator(BaseValidator): 
    """Validates if the value is alphanumeric (letters and numbers only).""" 
     
    def validate(self, value): 
        # Regex to match only alphanumeric characters (letters and digits) 
        if not re.match(r"^[a-zA-Z0-9]+$", str(value)): 
            self.raise_validation_error("Value must be alphanumeric (letters and numbers only).") 
        return True 
 
class PhoneNumberValidator(BaseValidator): 
    """Validates if the value is a valid phone number using the phonenumbers library.""" 
 
    def validate(self, value): 
        if not value: 
            self.raise_validation_error("Phone number cannot be empty.") 
 
        try: 
            # Parse the phone number using the phonenumbers library 
            parsed_number = phonenumbers.parse(value, None)  # None allows parsing without a default region 
             
            # Check if the phone number is valid 
            if not phonenumbers.is_valid_number(parsed_number): 
                self.raise_validation_error("Invalid phone number.") 
             
            # Optional: Check if it's a mobile number (this part is adjustable) 
            if not phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE: 
                self.raise_validation_error("The provided phone number is not a mobile number.") 
         
        except phonenumbers.NumberParseException as e: 
            self.raise_validation_error(f"Invalid phone number format: {str(e)}") 
         
        return True

# Email validation

        
# Boolean validation
class BooleanValidator:
    """
    A class to validate boolean inputs.
    """

    def __init__(self, value):
        self.value = value

    def validate(self) -> None:
        """
        Validates that the input is a boolean value (True or False).
        """
        if not isinstance(self.value, bool):
            raise HTTPException(
                status_code=400,
                detail="Invalid input. Value must be a boolean (True or False)."
            )

class PasswordValidator:
    """
    A class to validate the strength of passwords.
    """

    def __init__(self, password: str):
        self.password = password

    def validate_length(self) -> None:
        """
        Validates that the password is at least 8 characters long.
        """
        if len(self.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long."
            )

    def validate_numeric(self) -> None:
        """
        Validates that the password includes at least one number.
        """
        if not re.search(r"\d", self.password):
            raise HTTPException(
                status_code=400,
                detail="Password must include at least one number."
            )

    def validate_lowercase(self) -> None:
        """
        Validates that the password includes at least one lowercase letter.
        """
        if not re.search(r"[a-z]", self.password):
            raise HTTPException(
                status_code=400,
                detail="Password must include at least one lowercase letter."
            )

    def validate_uppercase(self) -> None:
        """
        Validates that the password includes at least one uppercase letter.
        """
        if not re.search(r"[A-Z]", self.password):
            raise HTTPException(
                status_code=400,
                detail="Password must include at least one uppercase letter."
            )

    def validate_special_character(self) -> None:
        """
        Validates that the password includes at least one special character.
        """
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.password):
            raise HTTPException(
                status_code=400,
                detail="Password must include at least one special character."
            )

    def validate(self) -> str:
        """
        Perform all validations for the password.
        """
        self.validate_length()
        self.validate_numeric()
        self.validate_lowercase()
        self.validate_uppercase()
        self.validate_special_character()
        return self.password
    
# Cross-site validation
class CrossFieldDateValidator(DateValidator):
    """
    A subclass of DateValidator that validates the relationship between two dates.
    """

    def __init__(self, start_date: str, end_date: str):
        super().__init__(start_date)  # Initialize with the start_date
        self.start_date_string = start_date
        self.end_date_string = end_date

    def validate(self) -> None:
        """
        Validate both dates individually and ensure the start date is before the end date.
        """
        # Validate both dates using the parent class methods
        self.date_string = self.start_date_string  # Set the current date to start_date
        self.validate_date_format()
        start_date_obj = self.validate_calendar_date()

        self.date_string = self.end_date_string  # Set the current date to end_date
        self.validate_date_format()
        end_date_obj = self.validate_calendar_date()

        # Validate the relationship between start_date and end_date
        self.validate_start_before_end(start_date_obj, end_date_obj)

    def validate_start_before_end(self, start_date: datetime, end_date: datetime) -> None:
        """
        Ensure the start date is earlier than the end date.
        """
        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be earlier than end date."
            )



# from PIL import Image  # To check dimensions
# import os
# import dns.resolver

# def validate_pincode(pincode: str) -> None:
#     """
#     Validates a pincode to ensure it meets the required criteria:
#     - Must be exactly 6 digits
#     - Must be numeric

#     Args:
#         pincode (str): The pincode to validate

#     Raises:
#         HTTPException: If validation fails
#     """
#     if not re.match(r"^\d{6}$", pincode):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid pincode: It must be exactly 6 numeric digits."
#         )


# # validation for address
# def validate_address(address: str) -> None:
#     """
#     Validates an address to ensure it meets the required criteria:
#     - Must be at least 5 characters long
#     - Must not exceed 100 characters
#     - Must not contain special characters other than space, comma, or hyphen

#     Args:
#         address (str): The address to validate

#     Raises:
#         HTTPException: If validation fails
#     """
#     if len(address) < 5 or len(address) > 100:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid address: It must be between 5 and 100 characters."
#         )
#     if not re.match(r"^[a-zA-Z0-9\s,.-]+$", address):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid address: Only letters, numbers, spaces, commas, periods, and hyphens are allowed."
#         )


# VALID_GENDERS = {"male", "female", "other"}  # Use lowercase values for consistent validation

# def validate_gender(gender: str) -> str:
#     """
#     Validates the gender field to ensure it matches one of the predefined options
#     and has a minimum length of 4 characters. Converts uppercase input to lowercase.

#     Args:
#         gender (str): The gender value to validate.

#     Returns:
#         str: The validated and normalized gender value in lowercase.

#     Raises:
#         HTTPException: If the gender value is invalid.
#     """
#     # Convert to lowercase
#     gender = gender.lower()

#     # Check minimum length
#     if len(gender) < 4:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid gender: The value must be at least 4 characters long."
#         )

#     # Validate against allowed options
#     if gender not in VALID_GENDERS:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid gender: Allowed values are {', '.join(VALID_GENDERS)}."
#         )

#     return gender



# # validation for firstname,middlename and lastname 
# def validate_name(name: str, field_name: str) -> None:
#     """
#     Validates a name field (firstname, lastname, middlename).
    
#     Args:
#         name (str): The name value to validate.
#         field_name (str): The name of the field (e.g., firstname, lastname).

#     Raises:
#         HTTPException: If the name value is invalid.
#     """
#     if len(name) < 3:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid {field_name}: It must be at least 2 characters long."
#         )

#     if len(name) > 50:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid {field_name}: It must not exceed 50 characters."
#         )

#     if not re.match(r"^[a-zA-Z\s'-]+$", name):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid {field_name}: Only alphabetic characters, spaces, hyphens, and apostrophes are allowed."
#         )



# # validation for password
# def validate_password(password: str) -> str:
#     """
#     Validates the password to ensure it meets the specified criteria.

#     Args:
#         password (str): The password to validate.

#     Returns:
#         str: The validated password.

#     Raises:
#         HTTPException: If any validation fails.
#     """
#     # 1. Check minimum length
#     if len(password) < 8:
#         raise HTTPException(
#             status_code=400,
#             detail="Password must be at least 8 characters long."
#         )

#     # 2. Check if the password includes at least one number
#     if not re.search(r"\d", password):
#         raise HTTPException(
#             status_code=400,
#             detail="Password must include at least one number."
#         )

#     # 3. Check if the password includes at least one lowercase letter
#     if not re.search(r"[a-z]", password):
#         raise HTTPException(
#             status_code=400,
#             detail="Password must include at least one lowercase letter."
#         )

#     # 4. Check if the password includes at least one uppercase letter
#     if not re.search(r"[A-Z]", password):
#         raise HTTPException(
#             status_code=400,
#             detail="Password must include at least one uppercase letter."
#         )

#     # 5. Check if the password includes at least one special character
#     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
#         raise HTTPException(
#             status_code=400,
#             detail="Password must include at least one special character."
#         )

#     return password




# def validate_placename(placename: str):
#     """
#     Validate place name to ensure it contains only alphabets, 
#     meets length requirements, and is not empty.
#     """
#     if not placename:
#         raise HTTPException(
#             status_code=400,
#             detail="Place name cannot be empty."
#         )
    
#     if not re.match(r"^[a-zA-Z\s]+$", placename):
#         raise HTTPException(
#             status_code=400,
#             detail="District name must contain only alphabets and spaces."
#         )
    
#     if len(placename) < 3:
#         raise HTTPException(
#             status_code=400,
#             detail="District name must be at least 3 characters long."
#         )
    
#     if len(placename) > 50:
#         raise HTTPException(
#             status_code=400,
#             detail="Place name cannot exceed 50 characters."
#         )



# def validate_emailid(emailid: str):
#     """
#     Validate email ID to ensure it follows standard email formatting and includes a valid domain.
#     """
#     if not emailid:
#         raise HTTPException(
#             status_code=400,
#             detail="Email ID cannot be empty."
#         )
        
#     # Check if the email length is within the valid range
#     if len(emailid) > 254:
#         raise HTTPException(
#             status_code=400,
#             detail="Email ID exceeds the maximum allowed length of 254 characters."
#         )

#     # Validate email format
#     if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", emailid):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid email ID format."
#         )

#     # Extract domain from the email
#     domain = emailid.split('@')[-1]

#     # Validate if the domain has DNS records (basic check for MX records)
#     try:
#         dns.resolver.resolve(domain, 'MX')
#     except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid domain in email: {domain} does not have MX records."
#         )
    
#     return True
        
# #install and import phonenumbers library version phonenumbers=8.13.52
# def validate_phonenumber(phonenumber: str):
#     """
#     Validate phone number to ensure it follows international standards and is valid.
#     """
#     if not phonenumber:
#         raise HTTPException(
#             status_code=400,
#             detail="Phone number cannot be empty."
#         )

#     try:
#         # Parse the phone number using the phonenumbers library
#         parsed_number = phonenumbers.parse(phonenumber, None)  # None allows parsing without a default region
        
#         # Check if the phone number is valid
#         if not phonenumbers.is_valid_number(parsed_number):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid phone number."
#             )
        
#         # Optional: Check if it's a mobile number
#         if not phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE:
#             raise HTTPException(
#                 status_code=400,
#                 detail="The provided phone number is not a mobile number."
#             )
#     except phonenumbers.NumberParseException as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid phone number format: {str(e)}"
#         )
        
# def validate_image(image: UploadFile):
#     """
#     Validate the uploaded image.
#     - Ensure it's an image file.
#     - Restrict file types to JPEG, PNG, etc.
#     - Check file size.
#     - Optionally validate image dimensions.
#     - Check if the image is corrupted.
#     """
    
#     # 1. Validate file name (no spaces or special characters other than underscores)
#     file_name = image.filename
#     if not re.match(r'^[\w_]+\.[a-zA-Z0-9]+$', file_name):  # Allow only letters, numbers, and underscores
#         raise HTTPException(
#             status_code=400,
#             detail="File name should not contain spaces or special characters other than underscores."
#         )
        
#     # 2. Validate file extension
#     valid_extensions = [".jpg", ".jpeg", ".png",".gif"]
#     file_extension = os.path.splitext(image.filename)[1].lower()

#     if file_extension not in valid_extensions:
#         raise HTTPException(
#             status_code=400, detail=f"Unsupported file type: {file_extension}. Allowed types: {valid_extensions}"
#         )

#     # 3. Validate file size
#     file_size = len(image.file.read())
#     max_size_in_mb = 1  # Set the max size (e.g., 1 MB)
#     if file_size > max_size_in_mb * 1024 * 1024:
#         raise HTTPException(
#             status_code=400, detail=f"File size exceeds {max_size_in_mb} MB limit."
#         )

#     # Reset the file pointer after reading
#     image.file.seek(0)

#     # 4. Validate image dimensions (optional)
#     try:
#         img = Image.open(image.file)
#         img.verify()  # Verifies that the image is not corrupted
        
#         # Reset the file pointer for further processing
#         image.file.seek(0)
#         img = Image.open(image.file)  # Open again for actual processing
#         width, height = img.size
        
#         # Define minimum and maximum allowed dimensions
#         min_width, min_height = 300, 300  # Example minimum dimensions
#         max_width, max_height = 1920, 1080  # Example maximum dimension
       
#        # Validate maximum dimensions
#         if width < min_width or height < min_height:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
#                        f"Uploaded image is {width}x{height}px."
#             )
#         if width > max_width or height > max_height:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Image dimensions exceed {max_width}x{max_height}px limit. Uploaded image is {width}x{height}px.",
#             )
            
#        # Validate minimum dimensions
#         if width < min_width or height < min_height:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
#                        f"Uploaded image is {width}x{height}px."
#             )
#         if width < min_width or height < min_height:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Image dimensions must be at least {min_width}x{min_height}px. "
#                        f"Uploaded image is {width}x{height}px."
#             )
            
#     except Exception:
#         raise HTTPException(
#             status_code=400, detail="Invalid image file."
#         )
#     finally:
#         # Reset the file pointer again after processing with PIL
#         image.file.seek(0)

#     return True


