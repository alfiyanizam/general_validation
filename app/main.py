from fastapi import FastAPI, Query, HTTPException
from app.validators import *

app = FastAPI(title="General Validations",
             description="A FastAPI application for general validations of various fields",
             version="1.0.0")


@app.get("/")
async def root():
    return {
        "status_code": 200,
        "message": "Welcome to the General Validations",
        "data": {
            "version": "1.0.0",
            "documentation": "/docs"
        }
    }

@app.get("/validate-numeric")
async def validate_numeric_field(
    value: str = Query(..., title="Value", description="Enter the value to check if it's numeric.")
):
    """
    Validates if the input is numeric.
    """
    # Initialize the numeric validator
    numeric_validator = NumericValidator()

    try:
        # Validate the value
        validated_value = numeric_validator.validate(value)
    except HTTPException as e:
        raise e

    return {"message": "Value is a valid numeric value.", "validated_value": validated_value}


@app.get("/validate-range")
async def validate_range_field(
    value: str = Query(..., title="Value", description="Enter the value to check if it's within the range."),
    min_value: float = Query(..., title="Min Value", description="Minimum allowed value for the number."),
    max_value: float = Query(..., title="Max Value", description="Maximum allowed value for the number."),
):
    """
    Validates if the numeric value is within a specified range.
    """
    # Initialize the range validator
    range_validator = RangeValidator(min_value=min_value, max_value=max_value)

    try:
        # Validate the value
        validated_value = range_validator.validate(value)
    except HTTPException as e:
        raise e

    return {
        "message": "Value is within the specified range.",
        "validated_value": validated_value,
        "min_value": min_value,
        "max_value": max_value,
    }


@app.get("/validate-age")
async def validate_age_field(
    age: Union[float, int] = Query(..., title="Age", description="Enter the age to check if it's valid."),
    max_age: int = Query(None, title="Max Age", description="Optional maximum age limit."),
):
    """
    Validate the age input by calling the AgeValidator.
    """
    # Initialize the age validator with an optional maximum age
    age_validator = AgeValidator(max_age=max_age)

    try:
        # Validate the age
        validated_age = age_validator.validate(age)
    except HTTPException as e:
        raise e  # If validation fails, it will raise HTTPException
    except ValueError:
        # Catch if non-numeric value is entered
        raise HTTPException(status_code=400, detail="Age must be a valid numeric value.")
    
    return {"message": "Age is valid.", "validated_age": validated_age}

@app.get("/validate-decimal")
async def validate_decimal_field(
    value: str = Query(..., title="Value", description="Enter the value to check if it's a decimal."),
    max_decimal_places: int = Query(None, title="Max Decimal Places", description="Specify the maximum decimal places if needed.")
):
    # Initialize the decimal validator with optional max decimal places
    decimal_validator = DecimalValidator(max_decimal_places=max_decimal_places)
    
    try:
        # Validate the value
        decimal_validator.validate(value)
    except HTTPException as e:
        raise e
    
    return {"message": "Value is a valid decimal number."}


@app.get("/validate-length")
async def validate_length_field(
    value: str = Query(..., title="Value", description="Enter the value to check its length."),
    min_length: int = Query(3, ge=1, title="Minimum Length", description="Specify the minimum length."),
    max_length: int = Query(10, le=100, title="Maximum Length", description="Specify the maximum length.")
):
    # Initialize the length validator with dynamic min and max length from query parameters
    min_max_length_validator = MinMaxLengthValidator(min_length=min_length, max_length=max_length)
    
    try:
        # Validate the value
        min_max_length_validator.validate(value)
    except HTTPException as e:
        raise e
    
    return {"message": "Value is within the valid length range."}

@app.get("/validate-alphanumeric")
async def validate_alphanumeric_field(
    value: str = Query(..., title="Value", description="Enter the value to check if it's alphanumeric.")
):
    # Initialize the alphanumeric validator
    alphanumeric_validator = AlphanumericValidator()
    
    try:
        # Validate the value
        alphanumeric_validator.validate(value)
    except HTTPException as e:
        raise e
    
    return {"message": "Value is a valid alphanumeric string."}


@app.get("/validate-phone-number")
async def validate_phone_number(phonenumber: str, region: str = None):
    """
    API endpoint to validate a phone number globally.
    :param phonenumber: The phone number to validate.
    :param region: Optional region for additional validation (not used in this global implementation).
    """
    phone_number_validator = PhoneNumberValidator(region=region)

    try:
        validation_result = phone_number_validator.validate(phonenumber)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "message": "Phone number is valid.",
        "details": validation_result,
    }

@app.get("/validate-emailid")
async def validate_email(
    emailid: str = Query(..., title="Email ID", description="Enter the email ID to validate.")
):
    """
    Validate email ID by calling the EmailValidator.
    :param emailid: The email ID to validate.
    """
    # Create an instance of the EmailValidator
    email_validator = EmailValidator()  # Adjust lengths as per your needs

    # Validate email ID
    try:
        email_validator.validate(emailid)
    except HTTPException as e:
        raise e  # If validation fails, it will raise HTTPException

    return {"message": "Validation successful!"}

@app.get("/validate-zipcode")
async def validate_zipcode(
    zipcode: str = Query(..., title="Zipcode", description="Enter the zip code to validate.")
):
    """
    Validate zip code by calling the ZipcodeValidator.
    :param zipcode: The zip code to validate.
    """
    # Create an instance of the ZipcodeValidator
    zipcode_validator = ZipcodeValidator()  # Adjust lengths as per your needs

    # Validate zip code
    try:
        zipcode_validator.validate(zipcode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Validation successful!"}


@app.get("/validate-pincode")
async def validate_pincode(
    pincode: str = Query(..., title="Pincode", description="Enter the pincode to validate.")
):
    """
    Validate pincode by calling the PincodeValidator.
    :param pincode: The pincode to validate.
    """
    # Create an instance of the PincodeValidator
    pincode_validator = PincodeValidator()  # Adjust lengths as per your needs

    # Validate pincode
    try:
        pincode_validator.validate(pincode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Validation successful!"}

@app.post("/validate-document")
async def validate_document_file(file: UploadFile):
    """
    Endpoint to validate Document files.
    """
    document_validator = DocumentValidator(max_file_size_mb=2)  # Allow PDFs up to 2 MB
    document_validator.validate(file)
    return {"message": "Document file is valid."}


@app.post("/validate-image")
async def validate_image_file(file: UploadFile):
    """
    Endpoint to validate image files.
    """
    image_validator = ImageValidator(max_file_size_mb=1)  # Allow images up to 1 MB
    image_validator.validate(file)
    return {"message": "Image file is valid."}