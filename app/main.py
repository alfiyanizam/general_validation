from fastapi import FastAPI,HTTPException
from app.validators import *
from fastapi import FastAPI, Query, File, UploadFile
from pydantic import BaseModel


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

class DateInput(BaseModel):
    date: str

@app.post("/validate-date/")
async def validate_date_endpoint(data: DateInput):
    """
    Endpoint to validate a date input.
    """
    # Initialize the DateValidator
    validator = DateValidator(data.date)

    # Perform all validations
    validator.validate()

    return {"message": "Date is valid!", "date": data.date}

class DOBInput(BaseModel):
    date_of_birth: str




@app.get("/validate-numeric") 
async def validate_numeric_field( 
    value: str = Query(..., title="Value", description="Enter the value to check if it's numeric."), 
    min_value: float = Query(None, title="Min Value", description="Minimum allowed value for the number."), 
    max_value: float = Query(None, title="Max Value", description="Maximum allowed value for the number."), 
): 
    # Initialize the numeric validator with optional min and max values 
    numeric_validator = NumericValidator(min_value=min_value, max_value=max_value) 
     
    try: 
        # Validate the value 
        numeric_validator.validate(value) 
    except HTTPException as e: 
        raise e 
     
    return {"message": "Value is a valid numeric integer."} 
 
 
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
async def validate_phone_number_endpoint( 
    phonenumber: str 
): 
    phone_number_validator = PhoneNumberValidator() 
     
    try: 
        phone_number_validator.validate(phonenumber) 
    except HTTPException as e: 
        raise e 
 
    return {"message": "Phone number is valid."}


# Boolean validation

@app.post("/validate-boolean/")
async def validate_boolean_endpoint(agree: bool):
    """
    Endpoint to validate a boolean input (e.g., agree/disagree checkbox).
    """
    validator = BooleanValidator(agree)
    validator.validate()
    return {"message": "Boolean value is valid!", "agree": agree}

# password
@app.post("/validate-password/")
async def validate_password_endpoint(password: str):
    """
    Endpoint to validate password strength.
    """
    # Initialize the PasswordValidator
    validator = PasswordValidator(password)

    # Perform password validation
    validator.validate()

    return {"message": "Password is valid!"}

# cross_Field validation
class DateRangeInput(BaseModel):
    start_date: str
    end_date: str

@app.post("/validate-date-range/")
async def validate_date_range(start_date: str, end_date: str):
    """
    Endpoint to validate a date range.
    """
    validator = CrossFieldDateValidator(start_date, end_date)
    validator.validate()

    return {
        "message": "Date range is valid!",
        "start_date": start_date,
        "end_date": end_date
    }


# @app.post("/validate_pincode")
# async def validate_pincode_endpoint(pincode: str, address: str):
#     """
#     API endpoint to validate a pincode.
#     """
#     # Use the imported validation function
#     validate_pincode(pincode)
#     validate_address(address)
#     return {"message": "Pincode is valid!", "pincode": pincode, "address": address}


# @app.post("/validate_address")
# async def validate_address_endpoint(address: str):
#     """
#     API endpoint to validate the address field.
#     """
#     # Validate and normalize the address
#     validated_address = validate_address(address)

#     return {"message": "Address is valid!", "address": validated_address}


# @app.post("/validate_gender")
# async def validate_gender_endpoint(gender: str):
#     """
#     API endpoint to validate the gender field.
#     """
#     # Validate and normalize the gender
#     validated_gender = validate_gender(gender)

#     return {"message": "Gender is valid!", "gender": validated_gender}


# @app.post("/validate_names")
# async def validate_names(firstname: str, lastname: str, middlename: str = None):
#     """
#     API endpoint to validate firstname, lastname, and middlename.
#     """
#     # Validate each name
#     validate_name(firstname, "firstname")
#     validate_name(lastname, "lastname")
#     if middlename:  # Middlename is optional
#         validate_name(middlename, "middlename")

#     return {
#         "message": "All name fields are valid!",
#         "firstname": firstname,
#         "lastname": lastname,
#         "middlename": middlename
#     }

# @app.post("/validate_password")
# async def validate_password_endpoint(password: str):
#     """
#     API endpoint to validate the password field.
#     """
#     # Validate the password
#     validated_password = validate_password(password)

#     return {"message": "Password is valid!", "password": validated_password}
# # Route to validate inputs
# @app.get("/validate-placename")
# async def validate_place(
#     placename: str = Query(..., title="Place Name", description="Enter the place name to validate."),
# ):
#     # Validate place name
#     validate_placename(placename)
        
#     return {"message": "Validation successful!"}

# @app.get("/validate-emailid")
# async def validate_email(
#     emailid: str = Query(..., title="Email ID", description="Enter the email ID to validate.")
# ):
    
#     # Validate email ID
#     validate_emailid(emailid)
    
#     return {"message": "Validation successful!"}


# @app.get("/validate-phonenumber")
# async def validate_phone(
#     phonenumber: str = Query(..., title="Phone Number", description="Enter the phone number to validate.")
# ):
    
#     # Validate email ID
#     validate_phonenumber(phonenumber)
    
#     return {"message": "Validation successful!"}

# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     """
#     Endpoint to handle image uploads.
#     """
#     validate_image(file)
#     return {"filename": file.filename, "message": "Image is valid and uploaded successfully!"}
