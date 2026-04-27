from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title = "LearnHub API",
    description = "Backend API for an Online Course Platform with courses, enrollments, and wishlist features",
    version="1.0.0"
)

# --------------------------
# In-Memory Data Storage
# --------------------------
courses = [
    {
        "id": 1,
        "title": "Python for Beginners",
        "instructor": "Ravi Kumar",
        "category": "Web Development",
        "level": "Beginner",
        "price": 0,
        "seats_left": 10
    },
    {
        "id": 2,
        "title": "Data Science Bootcamp",
        "instructor": "Prathibha",
        "category": "Data Science",
        "level": "Intermediate",
        "price": 20000,
        "seats_left": 5
    },
    {
        "id": 3,
        "title": "UI/UX Design",
        "instructor": "Surthi",
        "category": "Design",
        "level": "Beginner",
        "price": 2000,
        "seats_left": 8
    },
    {
        "id": 4,
        "title": "Docker & DevOps",
        "instructor": "Pradeep",
        "category": "DevOps",
        "level": "Advanced",
        "price": 25000,
        "seats_left": 3
    },
    {
        "id": 5,
        "title": "React Mastery",
        "instructor": "Santosh Kumar",
        "category": "Web Development",
        "level": "Advanced",
        "price": 30000,
        "seats_left": 7
    },
    {
        "id": 6,
        "title": "Machine Learning A-Z",
        "instructor": "Deepthi",
        "category": "Data Science",
        "level": "Advanced",
        "price": 40000,
        "seats_left": 2
    }
]

enrollments = []
wishlist = []
enrollment_counter = 1

# --------------------------
# Utility Functions
# --------------------------
def find_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course
    return None

def calculate_enrollment_fee(price: int, seats_left: int, coupon_code: str):
    original_price = price
    total_discount = 0
    current_price = price

    # Early-bird discount first
    if seats_left > 5:
        early_discount = current_price * 0.10
        current_price -= early_discount
        total_discount += early_discount

    # Coupon after early-bird
    if coupon_code == "STUDENT20":
        coupon_discount = current_price * 0.20
        current_price -= coupon_discount
        total_discount += coupon_discount

    elif coupon_code == "FLAT500":
        coupon_discount = 500
        current_price -= coupon_discount
        total_discount += coupon_discount

    # Prevent negative value
    if current_price < 0:
        current_price = 0

    return {
        "original_price": original_price,
        "discount_applied": round(total_discount, 2),
        "final_fee": round(current_price, 2)
    }

def filter_courses_logic(category=None, level=None, max_price=None, has_seats=None):
    result = courses

    if category is not None:
        result = [c for c in result if c["category"].lower() == category.lower()]

    if level is not None:
        result = [c for c in result if c["level"].lower() == level.lower()]

    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]

    if has_seats is not None:
        if has_seats:
            result = [c for c in result if c["seats_left"] > 0]

    return result

# --------------------------
# Request Models
# --------------------------
class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = Field(default="card")
    coupon_code: str = Field(default="")
    gift_enrollment: bool = Field(default=False)
    recipient_name: str = Field(default="")

class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

class EnrollAllRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    payment_method: str = Field(default="card")

# --------------------------
# Home
# --------------------------
@app.get("/", tags=["General"])
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

# --------------------------
# Course APIs
# --------------------------

# Get courses
@app.get("/courses", tags=["Courses"])
def get_courses():
    total_courses = len(courses)
    total_seats = sum(course["seats_left"] for course in courses)

    return {
        "courses": courses,
        "total_courses": total_courses,
        "total_seats_available": total_seats
    }

# Get course summary
@app.get("/courses/summary", tags=["Courses"])
def course_summary():
    total_courses = len(courses)

    # Free courses
    free_courses_count = len([c for c in courses if c["price"] == 0])

    # Most expensive course
    most_expensive_course = max(courses, key=lambda x: x["price"])

    # Total seats
    total_seats = sum(c["seats_left"] for c in courses)

    # Category count
    category_count = {}
    for c in courses:
        category = c["category"]
        category_count[category] = category_count.get(category, 0) + 1

    return {
        "total_courses": total_courses,
        "free_courses": free_courses_count,
        "most_expensive_course": most_expensive_course,
        "total_seats": total_seats,
        "courses_by_category": category_count
    }

# Get courses filter
@app.get("/courses/filter", tags=["Courses"])
def filter_courses(
    category: str = Query(None),
    level: str = Query(None),
    max_price: int = Query(None),
    has_seats: bool = Query(None)
):
    filtered = filter_courses_logic(category, level, max_price, has_seats)

    return {
        "filtered_courses": filtered,
        "total_found": len(filtered)
    }

# Courses search
@app.get("/courses/search", tags=["Courses"])
def search_courses(keyword: str = Query(..., min_length=1)):

    keyword_lower = keyword.lower()

    results = [
        course for course in courses
        if keyword_lower in course["title"].lower()
        or keyword_lower in course["instructor"].lower()
        or keyword_lower in course["category"].lower()
    ]

    return {
        "matched_courses": results,
        "total_found": len(results)
    }

# courses sort
@app.get("/courses/sort", tags=["Courses"])
def sort_courses(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    valid_sort_fields = ["price", "title", "seats_left"]
    valid_order = ["asc", "desc"]

    # Validate sort_by
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Choose from {valid_sort_fields}"
        )

    # Validate order
    if order not in valid_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Choose from {valid_order}"
        )

    reverse = True if order == "desc" else False

    sorted_courses = sorted(
        courses,
        key=lambda x: x[sort_by],
        reverse=reverse
    )

    return {
        "sorted_by": sort_by,
        "order": order,
        "total_courses": len(sorted_courses),
        "courses": sorted_courses
    }

# course page
@app.get("/courses/page", tags=["Courses"])
def paginate_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):

    total_courses = len(courses)

    # Calculate total pages
    total_pages = (total_courses + limit - 1) // limit

    # Validate page range
    if total_pages > 0 and page > total_pages:
        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )

    start = (page - 1) * limit
    end = start + limit

    paginated_courses = courses[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_courses": total_courses,
        "total_pages": total_pages,
        "courses": paginated_courses
    }

# Browse courses with filters, sorting, and pagination
@app.get("/courses/browse", tags=["Courses"])
def browse_courses(
    keyword: str = Query(None),
    category: str = Query(None),
    level: str = Query(None),
    max_price: int = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):

    result = courses

    # Keyword search
    if keyword:
        k = keyword.lower()
        result = [
            c for c in result
            if k in c["title"].lower()
            or k in c["instructor"].lower()
            or k in c["category"].lower()
        ]

    # Category filter
    if category:
        result = [c for c in result if c["category"].lower() == category.lower()]

    # Level filter
    if level:
        result = [c for c in result if c["level"].lower() == level.lower()]

    # Price filter
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]

    # Sorting
    valid_sort_fields = ["price", "title", "seats_left"]
    valid_order = ["asc", "desc"]

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Choose from {valid_sort_fields}"
        )

    if order not in valid_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Choose from {valid_order}"
        )

    reverse = True if order == "desc" else False

    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # Pagination
    total = len(result)
    total_pages = (total + limit - 1) // limit

    if total_pages > 0 and page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "filters": {
            "keyword": keyword,
            "category": category,
            "level": level,
            "max_price": max_price
        },
        "sorting": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total_results": total,
            "total_pages": total_pages
        },
        "courses": paginated
    }

# Get courses 
@app.get("/courses/{course_id}", tags=["Courses"])
def get_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course

    raise HTTPException(status_code=404, detail="Course not found")

# Post courses
@app.post("/courses", tags=["Courses"], status_code=201)
def create_course(course: NewCourse):
    
    for c in courses:
        if c["title"].lower() == course.title.lower():
            raise HTTPException(
                status_code=400,
                detail="Course with this title already exists"
            )

    if courses:
        new_id = max(c["id"] for c in courses) + 1
    else:
        new_id = 1

    new_course = {
        "id": new_id,
        "title": course.title,
        "instructor": course.instructor,
        "category": course.category,
        "level": course.level,
        "price": course.price,
        "seats_left": course.seats_left
    }

    courses.append(new_course)

    return {
        "message": "Course created successfully",
        "course": new_course
    }

# Put courses
@app.put("/courses/{course_id}", tags=["Courses"])
def update_course(
    course_id: int,
    price: int = Query(None),
    seats_left: int = Query(None)
):
    course = find_course(course_id)

    # Course not found
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Apply updates only if provided
    if price is not None:
        if price < 0:
            raise HTTPException(status_code=400, detail="Price must be >= 0")
        course["price"] = price

    if seats_left is not None:
        if seats_left < 0:
            raise HTTPException(status_code=400, detail="Seats must be >= 0")
        course["seats_left"] = seats_left

    return {
        "message": "Course updated successfully",
        "updated_course": course
    }

# Delete course
@app.delete("/courses/{course_id}", tags=["Courses"])
def delete_course(course_id: int):

    course = find_course(course_id)

    # Not found
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if any enrollment exists for this course
    for enrollment in enrollments:
        if enrollment["course_id"] == course_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete course with enrolled students"
            )

    # Delete course
    courses.remove(course)

    return {
        "message": "Course deleted successfully"
    }

# --------------------------
# Enrollment APIs
# --------------------------

# Post enrollments
@app.post("/enrollments", tags=["Enrollments"])
def create_enrollment(data: EnrollRequest):
    global enrollment_counter

    # Check if course exists
    course = find_course(data.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check seats availability
    if course["seats_left"] <= 0:
        raise HTTPException(status_code=400, detail="No seats available")
    
    if data.gift_enrollment and not data.recipient_name:
        raise HTTPException(status_code=400,
                            detail="Recipient name is required for gift enrollment")

    # Calculate fee
    fee_details = calculate_enrollment_fee(
        course["price"],
        course["seats_left"],
        data.coupon_code
    )

    # Reduce seat count
    course["seats_left"] -= 1

    # Create enrollment record
    enrollment = {
        "enrollment_id": enrollment_counter,
        "student_name": data.student_name,
        "email": data.email,
        "course_id": course["id"],
        "course_title": course["title"],
        "instructor": course["instructor"],
        "original_price": fee_details["original_price"],
        "discount_applied": fee_details["discount_applied"],
        "final_fee": fee_details["final_fee"],
        "gift_enrollment": data.gift_enrollment,
        "recipient_name": data.recipient_name if data.gift_enrollment else None,
    }

    enrollments.append(enrollment)
    enrollment_counter += 1

    return {
        "message": "Enrollment successful",
        "enrollment": enrollment
    }

# Get enrollments
@app.get("/enrollments", tags=["Enrollments"])
def get_enrollments():
    return {
        "enrollments": enrollments,
        "total_enrollments": len(enrollments)
    }

# Search enrollments
@app.get("/enrollments/search", tags=["Enrollments"])
def search_enrollments(student_name: str = Query(..., min_length=1)):

    keyword = student_name.lower()

    results = [
        e for e in enrollments
        if keyword in e["student_name"].lower()
    ]

    return {
        "matched_enrollments": results,
        "total_found": len(results)
    }

# Sort enrollments
@app.get("/enrollments/sort", tags=["Enrollments"])
def sort_enrollments(order: str = Query("asc")):

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be 'asc' or 'desc'"
        )

    reverse = True if order == "desc" else False

    sorted_list = sorted(
        enrollments,
        key=lambda x: x.get("final_fee", 0),
        reverse=reverse
    )

    return {
        "sorted_by": "final_fee",
        "order": order,
        "total_enrollments": len(sorted_list),
        "enrollments": sorted_list
    }

# Pagination
@app.get("/enrollments/page", tags=["Enrollments"])
def paginate_enrollments(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):

    total = len(enrollments)

    total_pages = (total + limit - 1) // limit

    if page > total_pages and total_pages != 0:
        raise HTTPException(status_code=404, detail="Page not found")

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_enrollments": total,
        "total_pages": total_pages,
        "enrollments": enrollments[start:end]
    }

# --------------------------
# Wishlist APIs
# --------------------------

# Create wishlist
@app.post("/wishlist/add", tags=["Wishlist"])
def add_to_wishlist(student_name: str = Query(...), course_id: int = Query(...)):

    # Check course exists
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Prevent duplicate (same student + same course)
    for item in wishlist:
        if item["student_name"].lower() == student_name.lower() and item["course_id"] == course_id:
            raise HTTPException(
                status_code=400,
                detail="Course already in wishlist for this student"
            )

    # Add to wishlist
    wishlist.append({
        "student_name": student_name,
        "course_id": course_id
    })

    return {
        "message": "Course added to wishlist",
        "wishlist_item": {
            "student_name": student_name,
            "course_id": course_id,
            "course_title": course["title"]
        }
    }

# Read wishlist
@app.get("/wishlist", tags=["Wishlist"])
def get_wishlist():

    total_value = 0
    detailed_list = []

    for item in wishlist:
        course = find_course(item["course_id"])
        if course:
            total_value += course["price"]
            detailed_list.append({
                "student_name": item["student_name"],
                "course_id": course["id"],
                "course_title": course["title"],
                "price": course["price"]
            })

    return {
        "wishlist": detailed_list,
        "total_items": len(detailed_list),
        "total_value": total_value
    }

# Delete Wishlist
@app.delete("/wishlist/remove/{course_id}", tags=["Wishlist"])
def remove_from_wishlist(course_id: int, 
                         student_name: str = Query(...)):

    for item in wishlist:
        if item["course_id"] == course_id and item["student_name"].lower() == student_name.lower():
            wishlist.remove(item)
            return {"message": "Removed from wishlist"}

    raise HTTPException(
        status_code=404,
        detail="Item not found in wishlist"
    )

# 
@app.post("/wishlist/enroll-all", tags=["Wishlist"])
def enroll_all_from_wishlist(data: EnrollAllRequest):

    global enrollment_counter

    student_items = [
        item for item in wishlist
        if item["student_name"].lower() == data.student_name.lower()
    ]

    if not student_items:
        raise HTTPException(
            status_code=404,
            detail="No wishlist items found for this student"
        )

    enrolled_courses = []
    total_fee = 0

    for item in student_items:
        course = find_course(item["course_id"])

        if not course or course["seats_left"] <= 0:
            continue  # skip unavailable courses

        fee_details = calculate_enrollment_fee(
            course["price"],
            course["seats_left"],
            ""  # no coupon here
        )

        # Reduce seat
        course["seats_left"] -= 1

        enrollment = {
            "enrollment_id": enrollment_counter,
            "student_name": data.student_name,
            "email": data.email,
            "course_id": course["id"],
            "course_title": course["title"],
            "final_fee": fee_details["final_fee"],
            "payment_method": data.payment_method
        }

        enrollments.append(enrollment)
        enrollment_counter += 1

        enrolled_courses.append(enrollment)
        total_fee += fee_details["final_fee"]

    enrolled_course_ids = [e["course_id"] for e in enrolled_courses]

    # Remove enrolled items from wishlist
    wishlist[:] = [
        item for item in wishlist
        if not( item["student_name"].lower() == data.student_name.lower()
        and item["course_id"] in enrolled_course_ids
        )
    ]

    return {
        "message": "Wishlist enrollment completed",
        "total_enrolled": len(enrolled_courses),
        "grand_total_fee": total_fee,
        "enrollments": enrolled_courses
    }