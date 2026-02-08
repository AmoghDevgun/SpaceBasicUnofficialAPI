#!/usr/bin/env python3
"""
SpaceBasic Complaint Automation Workflow
- Creates a complaint with room/bathroom cleaning request
- Fetches available time slots and lets you choose
- Automatically gives 5-star rating after complaint is created
"""

import requests
from datetime import datetime

# ============== CONFIGURATION ==============
AUTH_TOKEN = "<Info to put>"
BASE_URL = "https://api.spacebasic.com/api/v3"

# User-specific constants
STUDENT_ID = "<Info to put>"
USER_ID = "<Info to put>"
TENANT_ID = "<Info to put>"
USER_NAME = "<Info to put>"
CATEGORY_ID = "2787"
SUB_CATEGORY_ID = "3201"
PRIORITY_ID = "7"
DESCRIPTION = "Room and Bathroom cleaning"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "authorization": AUTH_TOKEN,
    "origin": "https://portal.spacebasic.com",
    "referer": "https://portal.spacebasic.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


def get_today_date():
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


def fetch_available_time_slots(date: str):
    """Fetch available time slots for a given date"""
    url = f"{BASE_URL}/maintenance/settings/active-time-slab"
    params = {"categoryId": CATEGORY_ID, "date": date}
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    
    data = response.json()
    if data.get("status") == "success":
        return data.get("result", {}).get("values", [])
    return []


def choose_time_slot(slots: list):
    """Display time slots and let user choose one"""
    if not slots:
        print("No available time slots found!")
        return None
    
    print("\nAvailable Time Slots:")
    print("-" * 40)
    for i, slot in enumerate(slots, 1):
        print(f"  {i}. {slot['timeSlab']}")
    print("-" * 40)
    
    while True:
        try:
            choice = int(input(f"\nSelect a time slot (1-{len(slots)}): "))
            if 1 <= choice <= len(slots):
                selected = slots[choice - 1]
                print(f"\nSelected: {selected['timeSlab']}")
                return selected["nextStartTime"]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")


def create_complaint(avl_date: str, avl_time: str):
    """Create a new complaint"""
    url = f"{BASE_URL}/complaints/add"
    
    # Build multipart form data
    form_data = {
        "subCategoryId": SUB_CATEGORY_ID,
        "complaintType": "0",
        "priorityId": PRIORITY_ID,
        "categoryId": CATEGORY_ID,
        "studentId": STUDENT_ID,
        "roleid": "0",
        "assigneeName": "",
        "assigneeId": "",
        "metaId": "0",
        "userType": "2",
        "userName": USER_NAME,
        "tenantId": TENANT_ID,
        "userId": USER_ID,
        "description": DESCRIPTION,
        "hostelId": "null",
        "floorId": "null",
        "blockId": "null",
        "roomId": "null",
        "image1": "undefined",
        "image2": "undefined",
        "image3": "undefined",
        "image4": "undefined",
        "avlTime": avl_time,
        "avlDate": avl_date,
    }
    
    response = requests.post(url, headers=HEADERS, data=form_data)
    response.raise_for_status()
    
    return response.json()


def get_recent_complaints():
    """Get list of recent complaints to find the latest complaint ID"""
    url = f"{BASE_URL}/complaints"
    
    payload = {
        "orderBy": {"fieldName": "created_at", "orderType": "DESC"},
        "archived": 0,
        "tenantId": TENANT_ID,
        "userId": USER_ID,
        "limit": 10,
        "offset": 0,
        "listType": "student"
    }
    
    headers = {**HEADERS, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    # API returns complaints directly in 'result' as an array
    if data.get("status") == "Success":
        return data.get("result", [])
    return []


def submit_rating(complaint_id: str, rating: int = 5):
    """Submit a 5-star rating for a complaint"""
    url = f"{BASE_URL}/complaintsFeedback/rating"
    
    payload = {
        "complaintId": complaint_id,
        "tenantId": TENANT_ID,
        "responsive": rating
    }
    
    headers = {**HEADERS, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()


def main():
    print("=" * 50)
    print("SpaceBasic Complaint Automation")
    print("=" * 50)
    
    # Step 1: Get today's date
    today = get_today_date()
    print(f"\nToday's Date: {today}")
    
    # Step 2: Rate the latest existing complaint first
    print("\nFetching existing complaints...")
    complaints = get_recent_complaints()
    
    if complaints:
        latest_complaint_id = str(complaints[0].get("id"))
        print(f"Latest Complaint ID: {latest_complaint_id}")
        
        print("\nSubmitting 5-star rating for latest complaint...")
        rating_result = submit_rating(latest_complaint_id, rating=5)
        
        if rating_result.get("status") == "success":
            print("5-star rating submitted successfully!")
        else:
            print(f"Rating submission failed: {rating_result}")
    else:
        print("No existing complaints found to rate.")
    
    # Step 3: Fetch available time slots
    print("\nFetching available time slots...")
    slots = fetch_available_time_slots(today)
    
    # Step 4: Let user choose a time slot
    selected_time = choose_time_slot(slots)
    if not selected_time:
        print("Cannot proceed without a time slot.")
        return
    
    # Step 5: Create the new complaint
    print("\nCreating new complaint...")
    result = create_complaint(today, selected_time)
    
    if result.get("status") == "Success":
        print("Complaint created successfully!")
    else:
        print(f"Failed to create complaint: {result}")
    
    print("\n" + "=" * 50)
    print("Workflow completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
