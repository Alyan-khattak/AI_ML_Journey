from flask import Flask
import redis

app = Flask(__name__)

# Connect to Redis
# "redis" is NOT localhost.
# It is the name of the Redis service that we will define
# inside docker-compose.yml.
redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


@app.route("/")
def home():

    # Get the current visit count from Redis
    visits = redis_client.get("visits")

    # If this is the first visit, there is no value yet
    if visits is None:
        visits = 0

    # Increase the visit count
    visits = int(visits) + 1

    # Store the updated count in Redis
    redis_client.set("visits", visits)

    return f"""
    <h1>Hello from Flask!</h1>
    <h2>This page has been visited {visits} times.</h2>
    """


if __name__ == "__main__":

    # 0.0.0.0 allows the Flask application to be
    # accessible from outside the container.
    app.run(host="0.0.0.0", port=5000)