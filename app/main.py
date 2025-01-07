from fastapi import FastAPI,HTTPException
from app.validators import *

app = FastAPI()


@app.get("/")
async def root():
    return {
        "status_code": 200,
        "message": "Welcome to the API",
        "data": {
            "version": "1.0.0",
            "documentation": "/docs"
        }
    }

@app.post("/validate_pincode")
async def validate_pincode_endpoint(pincode: str, address: str):
    """
    API endpoint to validate a pincode.
    """
    # Use the imported validation function
    validate_pincode(pincode)
    validate_address(address)
    return {"message": "Pincode is valid!", "pincode": pincode, "address": address}


@app.post("/validate_address")
async def validate_address_endpoint(address: str):
    """
    API endpoint to validate the address field.
    """
    # Validate and normalize the address
    validated_address = validate_address(address)

    return {"message": "Address is valid!", "address": validated_address}


@app.post("/validate_gender")
async def validate_gender_endpoint(gender: str):
    """
    API endpoint to validate the gender field.
    """
    # Validate and normalize the gender
    validated_gender = validate_gender(gender)

    return {"message": "Gender is valid!", "gender": validated_gender}


@app.post("/validate_names")
async def validate_names(firstname: str, lastname: str, middlename: str = None):
    """
    API endpoint to validate firstname, lastname, and middlename.
    """
    # Validate each name
    validate_name(firstname, "firstname")
    validate_name(lastname, "lastname")
    if middlename:  # Middlename is optional
        validate_name(middlename, "middlename")

    return {
        "message": "All name fields are valid!",
        "firstname": firstname,
        "lastname": lastname,
        "middlename": middlename
    }

@app.post("/validate_password")
async def validate_password_endpoint(password: str):
    """
    API endpoint to validate the password field.
    """
    # Validate the password
    validated_password = validate_password(password)

    return {"message": "Password is valid!", "password": validated_password}