import pymongo

# Establish a connection to MongoDB (assuming it's running locally on the default port)
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database called "blogging_platform"
db = client["blogging_platform"]

# Access the "users" collection inside the database
users_collection = db["users"]

# Insert a user document into the "users" collection
user_data = {
    "username": "kashish",
    "email": "john.doe@example.com",
    "password": "hashed_password",  # Note: Password should be hashed for security
    "registration_date": "2023-10-18",
    "role": "admin"  #assign the admin role to this user
}

users_collection.insert_one(user_data)

# Access the "blog_posts" collection inside the database
blog_posts_collection = db["blog_posts"]

# Insert a blog post document into the "blog_posts" collection
blog_post_data = {
    "title": "Sample Blog Post",
    "content": "This is the content of the blog post.",
    "author": "john_doe",  # Reference to the username of the author
    "creation_date": "2023-10-18",
    "tags": ["python", "mongodb"]
}

blog_posts_collection.insert_one(blog_post_data)

# Access the "comments" collection inside the database
comments_collection = db["comments"]

# Insert a comment document into the "comments" collection
comment_data = {
    "commenter_name": "Alice",
    "comment_text": "Great post!",
    "creation_date": "2023-10-18",
    "blog_post_id": blog_post_data["_id"]  # Reference to the _id of the associated blog post
}

comments_collection.insert_one(comment_data)
