from fastapi import FastAPI, Query, File, UploadFile
from app.validators import validate_placename, validate_emailid, validate_phonenumber, validate_image

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

# Route to validate inputs
@app.get("/validate-placename")
async def validate_place(
    placename: str = Query(..., title="Place Name", description="Enter the place name to validate."),
):
    # Validate place name
    validate_placename(placename)
        
    return {"message": "Validation successful!"}

@app.get("/validate-emailid")
async def validate_email(
    emailid: str = Query(..., title="Email ID", description="Enter the email ID to validate.")
):
    
    # Validate email ID
    validate_emailid(emailid)
    
    return {"message": "Validation successful!"}


@app.get("/validate-phonenumber")
async def validate_phone(
    phonenumber: str = Query(..., title="Phone Number", description="Enter the phone number to validate.")
):
    
    # Validate email ID
    validate_phonenumber(phonenumber)
    
    return {"message": "Validation successful!"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to handle image uploads.
    """
    validate_image(file)
    return {"filename": file.filename, "message": "Image is valid and uploaded successfully!"}