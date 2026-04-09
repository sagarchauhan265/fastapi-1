

from fastapi import File, HTTPException, UploadFile


async def validate_file(product_image:UploadFile=File(...)):
    allowed = ["image/jpeg","image/png","image/jpg"]
    max_size = 2 * 1024 * 1024  # 2MB
    print(product_image.content_type)
    if product_image.content_type not in allowed:
        raise HTTPException(status_code=400, detail="INVALID_FILE_TYPE")
    contents = await product_image.read()
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="FILE_TOO_LARGE")
    await product_image.seek(0)  # Reset file pointer after reading
    return product_image


