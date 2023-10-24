from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import jwt
from functools import wraps
import bcrypt  # Import the bcrypt library for password hashing

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["blogging_platform"]
users_collection = db["users"]
blog_posts_collection = db["blog_posts"]
comments_collection = db["comments"]

# Secret key for JWT
SECRET_KEY = 'your_secret_key'

# Authentication and Authorization Logic

def generate_token(username, role):
    payload = {
        'username': username,
        'role': role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        decoded_token = decode_token(token)
        if decoded_token:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized'}), 401  # Unauthorized
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        decoded_token = decode_token(token)
        if decoded_token and decoded_token.get('role') == 'admin':
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized'}), 403  # Forbidden
    return decorated_function

# Routes

# User Registration
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Validate email format
    if not email or not email.strip():
        return jsonify({"error": "Email is required"}), 400

    # Validate password format (at least one capital letter, one small letter, one special character, one number, and minimum 8 characters)
    if not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password) or len(password) < 8:
        return jsonify({"error": "Password must contain at least one capital letter, one small letter, one special character, one number, and be at least 8 characters long"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Check if the username is already taken
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Username already taken"}), 400

    # Register the user with hashed password
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,  # Store hashed password in the database
        "role": "user"  # Assigning user role by default
    }
    users_collection.insert_one(user_data)

    return jsonify({"message": "User registered successfully"}), 201

# User Authentication
@app.route("/login", methods=["POST"])
def authenticate_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})

    # Check if the user exists and verify the password
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = generate_token(username, user['role'])
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Authentication failed"}), 401
    
# Get All Users (only for admin users)
@app.route("/users", methods=["GET"])
@admin_required
def get_users():
    users = list(users_collection.find({}, {"password": 0}))  # Exclude password field from the response
    return jsonify(users), 200

# Create Blog Post (only for authenticated users)
@app.route("/blog_posts", methods=["POST"])
@login_required
def create_blog_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")

    # Validate input data
    if not title or not title.strip() or not content or not content.strip():
        return jsonify({"error": "Title and content are required"}), 400

    # Check if the author exists
    if not users_collection.find_one({"username": author}):
        return jsonify({"error": "Invalid author"}), 400

    # Create the blog post
    blog_post_data = {
        "title": title,
        "content": content,
        "author": author,
        "tags": data.get("tags", []),
    }
    blog_posts_collection.insert_one(blog_post_data)

    return jsonify({"message": "Blog post created successfully"}), 201

# Get All Blog Posts
@app.route("/blog_posts", methods=["GET"])
def get_blog_posts():
    blog_posts = list(blog_posts_collection.find())
    return jsonify(blog_posts), 200

# Get Blog Post by ID
@app.route("/blog_posts/<string:post_id>", methods=["GET"])
def get_blog_post_by_id(post_id):
    try:
        post_object_id = ObjectId(post_id)
        blog_post = blog_posts_collection.find_one({"_id": post_object_id})

        if blog_post:
            blog_post["_id"] = str(blog_post["_id"])
            return jsonify(blog_post), 200
        else:
            return jsonify({"error": "Blog post not found"}), 404

    except Exception as e:
        return jsonify({"error": "Invalid post ID"}), 400

# Update Blog Post by ID (only for authenticated users)
@app.route("/blog_posts/<string:post_id>", methods=["PUT"])
@login_required
def update_blog_post(post_id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")

    # Validate input data
    if not title or not title.strip() or not content or not content.strip():
        return jsonify({"error": "Title and content are required"}), 400

    # Check if the post exists
    post_object_id = ObjectId(post_id)
    existing_post = blog_posts_collection.find_one({"_id": post_object_id})

    if not existing_post:
        return jsonify({"error": "Blog post not found"}), 404

    # Check if the author exists
    if not users_collection.find_one({"username": author}):
        return jsonify({"error": "Invalid author"}), 400

    # Update the blog post
    blog_post_data = {
        "title": title,
        "content": content,
        "author": author,
        "tags": data.get("tags", []),
    }
    blog_posts_collection.update_one({"_id": post_object_id}, {"$set": blog_post_data})

    return jsonify({"message": "Blog post updated successfully"}), 200

# Delete Blog Post by ID (only for admin users)
@app.route("/blog_posts/<string:post_id>", methods=["DELETE"])
@admin_required
def delete_blog_post(post_id):
    try:
        post_object_id = ObjectId(post_id)
        result = blog_posts_collection.delete_one({"_id": post_object_id})

        if result.deleted_count > 0:
            return jsonify({"message": "Blog post deleted successfully"}), 200
        else:
            return jsonify({"error": "Blog post not found"}), 404

    except Exception as e:
        return jsonify({"error": "Invalid post ID"}), 400

# Create Comment (only for authenticated users)
@app.route("/comments", methods=["POST"])
@login_required
def create_comment():
    data = request.get_json()
    commenter_name = data.get("commenter_name")
    comment_text = data.get("comment_text")
    blog_post_id = data.get("blog_post_id")

    # Validate input data
    if not commenter_name or not commenter_name.strip() or not comment_text or not comment_text.strip():
        return jsonify({"error": "Commenter name and comment text are required"}), 400

    # Check if the blog post exists
    post_object_id = ObjectId(blog_post_id)
    if not blog_posts_collection.find_one({"_id": post_object_id}):
        return jsonify({"error": "Invalid blog post ID"}), 400

    # Create the comment
    comment_data = {
        "commenter_name": commenter_name,
        "comment_text": comment_text,
        "blog_post_id": blog_post_id,
    }
    comments_collection.insert_one(comment_data)

    return jsonify({"message": "Comment created successfully"}), 201

# Get All Comments
@app.route("/comments", methods=["GET"])
def get_comments():
    comments = list(comments_collection.find())
    return jsonify(comments), 200

# Get Comment by ID
@app.route("/comments/<string:comment_id>", methods=["GET"])
def get_comment_by_id(comment_id):
    try:
        comment_object_id = ObjectId(comment_id)
        comment = comments_collection.find_one({"_id": comment_object_id})

        if comment:
            comment["_id"] = str(comment["_id"])
            return jsonify(comment), 200
        else:
            return jsonify({"error": "Comment not found"}), 404

    except Exception as e:
        return jsonify({"error": "Invalid comment ID"}), 400

# Update Comment by ID (only for authenticated users)
@app.route("/comments/<string:comment_id>", methods=["PUT"])
@login_required
def update_comment_by_id(comment_id):
    data = request.get_json()
    commenter_name = data.get("commenter_name")
    comment_text = data.get("comment_text")
    blog_post_id = data.get("blog_post_id")

    # Validate input data
    if not commenter_name or not commenter_name.strip() or not comment_text or not comment_text.strip():
        return jsonify({"error": "Commenter name and comment text are required"}), 400

    # Check if the comment exists
    comment_object_id = ObjectId(comment_id)
    existing_comment = comments_collection.find_one({"_id": comment_object_id})

    if not existing_comment:
        return jsonify({"error": "Comment not found"}), 404

    # Check if the associated blog post exists
    post_object_id = ObjectId(blog_post_id)
    if not blog_posts_collection.find_one({"_id": post_object_id}):
        return jsonify({"error": "Invalid blog post ID"}), 400

    # Update the comment
    comment_data = {
        "commenter_name": commenter_name,
        "comment_text": comment_text,
        "blog_post_id": blog_post_id,
    }
    comments_collection.update_one({"_id": comment_object_id}, {"$set": comment_data})

    return jsonify({"message": "Comment updated successfully"}), 200

# Delete Comment by ID (only for authenticated users)
@app.route("/comments/<string:comment_id>", methods=["DELETE"])
@login_required
def delete_comment_by_id(comment_id):
    try:
        comment_object_id = ObjectId(comment_id)
        result = comments_collection.delete_one({"_id": comment_object_id})

        if result.deleted_count > 0:
            return jsonify({"message": "Comment deleted successfully"}), 200
        else:
            return jsonify({"error": "Comment not found"}), 404

    except Exception as e:
        return jsonify({"error": "Invalid comment ID"}), 400
    


@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    admin_user = users_collection.find_one({"username": username, "role": "admin"})

    if admin_user and bcrypt.checkpw(password.encode('utf-8'), admin_user['password'].encode('utf-8')):
        admin_token = generate_token(username, role="admin")
        return jsonify({"message": "Admin logged in successfully", "token": admin_token}), 200
    else:
        return jsonify({"message": "Invalid admin credentials"}), 401

@app.route("/admin/users", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({"message": "Username or email already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": "user"
    }
    users_collection.insert_one(user_data)

    return jsonify({"message": "User created successfully"}), 201

@app.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    users = list(users_collection.find({}, {"password": 0}))
    return jsonify(users), 200

@app.route("/admin/users/<user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = users_collection.find_one({"_id": user_id}, {"password": 0})
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route("/admin/users/<user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    data = request.get_json()
    users_collection.update_one({"_id": user_id}, {"$set": data})
    return jsonify({"message": "User updated successfully"}), 200

@app.route("/admin/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    users_collection.delete_one({"_id": user_id})
    return jsonify({"message": "User deleted successfully"}), 200


@app.route("/admin/blogs", methods=["POST"])
@admin_required
def create_blog():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    blog_data = {
        "title": title,
        "content": content,
        "author": request.decoded_token.get("username"),
        "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    blog_posts_collection.insert_one(blog_data)

    return jsonify({"message": "Blog post created successfully"}), 201

@app.route("/admin/blogs", methods=["GET"])
@admin_required
def get_all_blogs():
    blogs = list(blog_posts_collection.find())
    return jsonify(blogs), 200

@app.route("/admin/blogs/<blog_id>", methods=["GET"])
@admin_required
def get_blog(blog_id):
    blog = blog_posts_collection.find_one({"_id": ObjectId(blog_id)})
    if blog:
        return jsonify(blog), 200
    else:
        return jsonify({"message": "Blog post not found"}), 404

@app.route("/admin/blogs/<blog_id>", methods=["PUT"])
@admin_required
def update_blog(blog_id):
    data = request.get_json()
    blog_posts_collection.update_one({"_id": ObjectId(blog_id)}, {"$set": data})
    return jsonify({"message": "Blog post updated successfully"}), 200

@app.route("/admin/blogs/<blog_id>", methods=["DELETE"])
@admin_required
def delete_blog(blog_id):
    blog_posts_collection.delete_one({"_id": ObjectId(blog_id)})
    return jsonify({"message": "Blog post deleted successfully"}), 200

# Admin Comment Routes

@app.route("/admin/comments", methods=["GET"])
@admin_required
def get_all_comments():
    comments = list(comments_collection.find())
    return jsonify(comments), 200

@app.route("/admin/comments/<comment_id>", methods=["GET"])
@admin_required
def get_comment(comment_id):
    comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    if comment:
        return jsonify(comment), 200
    else:
        return jsonify({"message": "Comment not found"}), 404

@app.route("/admin/comments/<comment_id>", methods=["PUT"])
@admin_required
def update_comment(comment_id):
    data = request.get_json()
    comments_collection.update_one({"_id": ObjectId(comment_id)}, {"$set": data})
    return jsonify({"message": "Comment updated successfully"}), 200

@app.route("/admin/comments/<comment_id>", methods=["DELETE"])
@admin_required
def delete_comment(comment_id):
    comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return jsonify({"message": "Comment deleted successfully"}), 200


# Serve the index.html file for the root URL
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
