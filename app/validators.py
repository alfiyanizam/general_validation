import re, os
import dns.resolver
import html
# import phonenumbers
# from phonenumbers import parse, is_valid_number, is_possible_number, NumberParseException, PhoneNumberType
from fastapi import HTTPException,  UploadFile
from typing import Union, List


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
    """Validates if the value is numeric (integer or float)."""

    def validate(self, value: Union[str, int, float]):
        try:
            # Try converting the value to a float to check if it's numeric
            float(value)
        except ValueError:
            self.raise_validation_error(
                f"Input '{value}' is not a valid number. Please provide a valid numeric value."
            )
        return True


class RangeValidator(NumericValidator):
    """Validates if the numeric value is within a specified range."""

    def __init__(self, min_value: Union[int, float] = None, max_value: Union[int, float] = None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Union[str, int, float]):
        # First, ensure the value is numeric
        super().validate(value)

        # Convert the value to a float for range comparison
        float_value = float(value)

        # Validate range constraints
        if self.min_value is not None and float_value < self.min_value:
            self.raise_validation_error(f"Value must be greater than or equal to {self.min_value}.")
        if self.max_value is not None and float_value > self.max_value:
            self.raise_validation_error(f"Value must be less than or equal to {self.max_value}.")
        
        return True


class AgeValidator(RangeValidator):
    """Validates that the value is a valid age (18 or older by default)."""

    def __init__(self, min_age: int = 18):
        # Initialize RangeValidator with a fixed minimum age
        super().__init__(min_value=min_age)

    def validate(self, value: Union[str, int, float]):
        # Perform the range validation for age
        super().validate(value)
        return True


class DecimalValidator(BaseValidator):
    """Validates if the value is a decimal number with optional precision."""

    def __init__(self, max_decimal_places: int = None):
        self.max_decimal_places = max_decimal_places

    def validate(self, value):
        
        # Sanitize the input
        value = html.escape(str(value))
        
        # Update regex pattern to allow negative numbers, integers, and decimals
        regex = r"^-?\d+(\.\d{1," + (str(self.max_decimal_places) if self.max_decimal_places else "10") + "})?$"
        
        if not re.match(regex, value):
            self.raise_validation_error("Value must be a valid decimal number.")
        
        return True


class MinMaxLengthValidator(BaseValidator):
    """Validates the minimum and maximum length of a string."""

    def __init__(self, min_length: int = None, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        # Sanitize the input
        value = html.escape(str(value))
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
        if not value:
            self.raise_validation_error("Textfield cannot be empty.")
        # Sanitize the input
        value = html.escape(str(value))
        # Regex to match only alphanumeric characters (letters and digits)
        if not re.match(r"^[a-zA-Z0-9]+$", str(value)):
            self.raise_validation_error("Value must be alphanumeric (letters and numbers only).")
        return True
    
class AlphabetSetValidator(BaseValidator):
    """Validates if the value is alphabets (letters only)."""
    
    def validate(self, value):
        if not value:
            self.raise_validation_error("Textfield cannot be empty.")
        # Sanitize the input
        value = html.escape(str(value))
        # Regex to match only alphanumeric characters (letters and digits)
        if not re.match(r"^[a-zA-Z]+$", str(value)):
            self.raise_validation_error("Value must be alphabets (letters only).")
        return True

class PhoneNumberValidator(MinMaxLengthValidator):
    """Validates global phone numbers using regex."""

    def __init__(self, min_length: int = 8, max_length: int = 14, region: str = None):
        """
        Initialize the validator with optional min_length, max_length, and region.
        :param min_length: Minimum length for the phone number (default: 8).
        :param max_length: Maximum length for the phone number (default: 14).
        :param region: Optional region code for specific validation (not used here for global validation).
        """
        # Call the constructor of MinMaxLengthValidator with the min_length and max_length
        super().__init__(min_length, max_length)
        self.region = region
    def validate(self, phonenumber: str):
        """
        Validate a global phone number, excluding country code.
        :param phonenumber: The phone number to validate.
        """
        if not phonenumber:
            self.raise_validation_error("Phone number cannot be empty.")
            
        # Sanitize the input to prevent XSS
        phonenumber = html.escape(phonenumber)

        # Regex for global phone numbers with optional separators and country code
        regex = r"^\+?[1-9]\d{0,2}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"

        # Match the phone number against the regex
        if not re.fullmatch(regex, phonenumber):
            self.raise_validation_error("Invalid phone number format.")

        # Remove non-digit characters
        digits_only = re.sub(r"[^\d]", "", phonenumber)
        
        # Validate the length using the min_length and max_length passed to the parent class
        super().validate(digits_only)

        return "Valid phone number."
    
class EmailValidator(MinMaxLengthValidator):
    """Validates email IDs to ensure correct formatting and valid domain."""
    
    def __init__(self, min_length: int = 5, max_length: int = 254):
         super().__init__(min_length, max_length)
        

    def validate(self, emailid: str):
        """
        Validate the email ID to ensure it follows standard email formatting and includes a valid domain.
        :param emailid: The email ID to validate.
        """
        # Sanitize the input to prevent XSS
        emailid = html.escape(emailid)
        
        # Reuse MinMaxLengthValidator's checks for email length
        super().validate(emailid)

        if not emailid:
            self.raise_validation_error("Email ID cannot be empty.")

        # Split the email to get the username and domain
        username, domain = emailid.split('@', 1)

        # Check if the username is at least 3 characters long
        if len(username) < 3:
            self.raise_validation_error("Username must be at least 3 characters long.")

        # Check if the email contains uppercase letters
        if any(char.isupper() for char in emailid):
            self.raise_validation_error("Email ID must not contain uppercase letters.")

        # Validate email format using regex
        if not re.match(r"^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$", emailid, re.IGNORECASE):
            self.raise_validation_error("Invalid email ID format.")

        # Validate if the domain has DNS records (basic check for MX records)
        try:
            dns.resolver.resolve(domain, 'MX')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            self.raise_validation_error(f"Invalid domain in email: {domain} does not have MX records.")

        return True
    
class ZipcodeValidator(MinMaxLengthValidator):
    """Validates U.S. zip codes and ZIP+4 format."""

    def __init__(self, min_length: int = 5, max_length: int = 10):
        super().__init__(min_length, max_length)

    def validate(self, zipcode: str):
        """
        Validate a U.S. zip code, including ZIP+4 format.
        :param zipcode: The zip code to validate.
        """
        if not zipcode:
            self.raise_validation_error("Zip code cannot be empty.")
        
        # Sanitize the input to prevent XSS
        zipcode = html.escape(zipcode)
        
        # Check length using the MinMaxLengthValidator
        super().validate(zipcode)

        # Regex for U.S. zip code (5 digits or ZIP+4 format)
        regex = r"^\d{5}(-\d{4})?$"

        if not re.fullmatch(regex, zipcode):
            self.raise_validation_error("Invalid zip code format. Must be 5 digits or ZIP+4 format.")
        
        return "Valid zip code."


class PincodeValidator(MinMaxLengthValidator):
    """Validates Indian pincodes."""

    def __init__(self, min_length: int = 6, max_length: int = 6):
        super().__init__(min_length, max_length)

    def validate(self, pincode: str):
        """
        Validate an Indian pincode.
        :param pincode: The pincode to validate.
        """
        if not pincode:
            self.raise_validation_error("Pincode cannot be empty.")
            
        # Sanitize the input to prevent XSS
        pincode = html.escape(pincode)
        
        # Check length using the MinMaxLengthValidator
        super().validate(pincode)

        # Regex for Indian pincode (6 digits)
        regex = r"^\d{6}$"

        if not re.fullmatch(regex, pincode):
            self.raise_validation_error("Invalid pincode format. Must be exactly 6 digits.")
        
        return "Valid pincode."
    
class FileValidator(BaseValidator):
    """
    Validator for file uploads.
    Includes validation for file name, type, and size.
    """

    def __init__(self, allowed_extensions: List[str], max_file_size_mb: int):
        """
        Initialize the validator with allowed extensions and maximum file size.

        :param allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png']).
        :param max_file_size_mb: Maximum allowed file size in MB.
        """
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        self.max_file_size_mb = max_file_size_mb

    def validate(self, file: UploadFile):
        """
        Validate the file for name, type, and size.
        """
        self.validate_file_name(file.filename)
        self.validate_file_type(file.filename)
        self.validate_file_size(file)

    def validate_file_name(self, file_name: str):
        """
        Validate the file name to ensure it does not contain spaces or special characters.
        """
        if not re.match(r'^[\w_]+\.[a-zA-Z0-9]+$', file_name):
            self.raise_validation_error(
                "File name should not contain spaces or special characters other than underscores."
            )

    def validate_file_type(self, file_name: str):
        """
        Validate the file extension to ensure it matches the allowed extensions.
        """
        file_extension = os.path.splitext(file_name)[1].lower()
        if file_extension not in self.allowed_extensions:
            self.raise_validation_error(
                f"Unsupported file type: {file_extension}. Allowed types: {self.allowed_extensions}"
            )

    def validate_file_size(self, file: UploadFile):
        """
        Validate the file size to ensure it is within the allowed limit.
        """
        file_size = len(file.file.read())  # Read the file to get its size
        if file_size > self.max_file_size_mb * 1024 * 1024:
            self.raise_validation_error(
                f"File size exceeds {self.max_file_size_mb} MB limit."
            )
        file.file.seek(0)  # Reset the file pointer after reading

class DocumentValidator(FileValidator):
    """Validator for Document files."""
    def __init__(self, max_file_size_mb: int = 2):
        super().__init__(allowed_extensions=[".pdf",".docx","xlsx"], max_file_size_mb=max_file_size_mb)


class ImageValidator(FileValidator):
    """Validator for image files."""
    def __init__(self, max_file_size_mb: int = 5):
        super().__init__(allowed_extensions=[".jpg", ".jpeg", ".png", ".gif"], max_file_size_mb=max_file_size_mb)
import re

from fastapi import HTTPException, APIRouter, UploadFile
from datetime import datetime




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
            "%m/%d/%Y %I:%M:%S %p",     # Date and time with seconds and AM/PM
            "%d %b %Y",                 # Date with abbreviated month name (e.g., 23 May 2020)
            "%d %B %Y",                 # Date with full month name (e.g., 23 May 2020)
            "%d %B %Y %H:%M",           # Date and time with full month name
            "%d %B %Y %H:%M:%S",        # Date and time with seconds and full month name
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

    def validate_month(self, date_obj: datetime) -> None:
        """
        Ensures the input contains a valid month name or number.
        """
        try:
            # Extract the month from the datetime object and validate
            if date_obj.month < 1 or date_obj.month > 12:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid month. Please provide a valid month number (01-12) or name."
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Ensure the input contains a valid month."
            )

    def validate(self) -> None:
        """
        Perform all validations on the date and time.
        """
        date_format = self.determine_format()
        date_obj = self.validate_calendar_date(date_format)
        self.validate_not_future_year(date_obj)
        self.validate_month(date_obj)
        print(f"Date and time '{self.date_string}' are valid and follow the format {date_format}.")
 
 

        
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


