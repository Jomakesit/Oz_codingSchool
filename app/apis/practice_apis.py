
# app/apis/practice_apis.py

from fastapi import APIRouter, HTTPException

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

# 회원정보 삭제 API 
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    # user_list에서 해당 user_id를 가진 회원을 검색
    for user in user_list:
        if user["id"] == user_id:
            user_list.remove(user)  # 리스트에서 해당 회원 삭제
            return {"message": f"성공적으로 삭제되었습니다. (ID: {user_id})"}
    
    # 리스트를 다 돌았는데도 해당 id가 없으면 404 에러 반환
    raise HTTPException(status_code=404, detail="User not found")

# 전체 회원 목록 조회 API
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

# ⭐️ 특정 회원 조회 API
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
