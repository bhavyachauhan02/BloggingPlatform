import pymongo

# Establish a connection to MongoDB (assuming it's running locally on the default port)
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a new database called "blogging_platform"
db = client["blogging_platform"]

# Access or create collections inside the database
users_collection = db["users"]
blog_posts_collection = db["blog_posts"]
comments_collection = db["comments"]

# You now have a database named "blogging_platform" with collections for users, blog posts, and comments.
