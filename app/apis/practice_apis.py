import re
from fastapi import APIRouter, HTTPException, Body, status

router = APIRouter(
    prefix="/practice_api",
    tags=["practice_api"]
)

user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!"
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!"
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@"
    }
]

# [5번 API] 회원정보 삭제 API 
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    # user_list에서 해당 user_id를 가진 회원을 검색
    for user in user_list:
        if user["id"] == user_id:
            user_list.remove(user)  # 리스트에서 해당 회원 삭제
            return {"message": f"성공적으로 삭제되었습니다. (ID: {user_id})"}
    
    # 리스트를 다 돌았는데도 해당 id가 없으면 404 에러 반환
    raise HTTPException(status_code=404, detail="User not found")


# [1번 API] 모든 회원의 정보를 목록으로 조회하는 API
@router.get("/users")
def get_users():
    users = []
    for user in user_list:
        users.append(
            {
                "id": user["id"],
                "name": user["name"],
                "age": user["age"],
                "email": user["email"]
            }
        )
    return users


# [2번 API] 회원 id를 path parameter로 입력받아 해당 회원의 정보를 조회하는 API
@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "name": user["name"],
                "age": user["age"],
                "email": user["email"]
            }
    raise HTTPException(status_code=404, detail="User not found")



# [3번 API] 회원 정보를 Request Body로 입력받아 추가 API
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    name: str = Body(..., min_length=2, max_length=10), # 이름 최소 2글자, 최대 10글자
    age: int = Body(..., ge=14),                       # 나이 최소 14세 이상
    email: str = Body(...),
    password: str = Body(...)
):
    # 1. 이메일 형식 검증 (최대 30자 및 정규표현식)
    if len(email) > 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이메일은 최대 30자까지 가능합니다.")
    
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="올바른 이메일 형식이 아닙니다.")
        
    # 2. 이메일 중복 불가능 검증
    for u in user_list:
        if u["email"] == email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 이메일입니다.")
            
    # 3. 비밀번호 검증 (대소문자, 특수문자 각 1개 필수, 최소 8자~최대 20자)
    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,20}$"
    if not re.match(password_pattern, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호는 대소문자, 특수문자가 각 1개씩 필수이며 8자 이상 20자 이하여야 합니다."
        )
    
    # 4. 입력값이 모두 올바르면 user_list에 추가 (id는 자동으로 1씩 증가)
    next_id = max([u["id"] for u in user_list]) + 1 if user_list else 1
    new_user = {
        "id": next_id,
        "name": name,
        "age": age,
        "email": email,
        "password": password
    }
    user_list.append(new_user)
    
    return {"message": "회원이 성공적으로 추가되었습니다.", "user_id": next_id}


# [4번 API] 회원정보 수정 API
@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    age: int | None = Body(None, ge=14),
    email: str | None = Body(None),
    password: str | None = Body(None)
):
    # age, email, password 중 아무 값도 입력되지 않은 경우 400 에러 반환
    if age is None and email is None and password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 항목을 최소 1개 이상 입력해야 합니다."
        )

    # user_list에서 해당 user_id를 가진 회원을 검색
    for user in user_list:
        if user["id"] == user_id:
            # age가 입력된 경우 나이 수정
            if age is not None:
                user["age"] = age

            # email이 입력된 경우 이메일 검증 후 수정
            if email is not None:
                if len(email) > 30:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="이메일은 최대 30자까지 가능합니다."
                    )

                email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(email_pattern, email):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="올바른 이메일 형식이 아닙니다."
                    )

                user["email"] = email

            # password가 입력된 경우 비밀번호 검증 후 수정
            if password is not None:
                password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,20}$"
                if not re.match(password_pattern, password):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="비밀번호는 대소문자, 특수문자가 각 1개씩 필수이며 8자 이상 20자 이하여야 합니다."
                    )

                user["password"] = password

            return {
                "message": "회원 정보가 성공적으로 수정되었습니다.",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "age": user["age"],
                    "email": user["email"]
                }
            }

    # user_list를 다 돌았는데도 해당 id가 없으면 404 에러 반환
    raise HTTPException(status_code=404, detail="User not found")