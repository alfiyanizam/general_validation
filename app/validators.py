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
        
        # Sanitize the input to prevent XSS
        zipcode = html.escape(zipcode)

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