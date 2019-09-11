JWT Authorized RESTful api using flask
======================================


Installation
-------------

    pip install -r requirements.txt


How to run flask app
--------------------

    python app.py


How to test with Curl
---------------------

    - GET JWT token

        curl -X POST -d "{\"email\": \"test1@test.com\", \"password\": \"password\"}" -H "Content-Type:application/json" http://127.0.0.1:5000/login

    - GET new JWT token using refresh_token

        curl -X POST  -H "Authorization: Bearer <refresh_token>" http://127.0.0.1:5000/refresh

    - GET dogs list with obtained jwt token

        curl -H "Authorization: Bearer <token>" http://localhost:5000/dog

