# Flask Celery Redis Docker



## Setup
1. Clone the repository: `git clone https://github.com/rajasgs/flask-celery-redis-ocr-docker`
2. Create a container: `sudo docker-compose build`
3. Run the container: `sudo docker-compose run` or `docker-compose up`. To run multiple Celery workers: `sudo docker-compose up --scale worker=N`

The application will be available on http://127.0.0.1:5000/
