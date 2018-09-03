Fitness web application
=======
 The project includes `fitness` web application with core `Werkzeug`, `Jinja2` and `redis`.
 ## Getting Started
1. Clone this repo on your local machine.
1. Assuming you are having Python 3.7 already in your machine.
1. Setup environment:
    ```
    cd bmi_app
    virtualenv -p python3.7 ~/.virtualenvs/bmi_app
    source ~/.virtualenvs/bmi_app/bin/activate
    pip install -r requirements.txt
    ```
1. Make sure `redis` server running on your local machine. 
    * If you are on OS X, you can use brew to install it:
    ```
    brew install redis
    ```
     * If you are on Ubuntu or Debian, you can use apt-get:
     ```
     sudo apt-get install redis-server
     ```

1. Run app:
    1. python fitness.py
    
1. To clean environment following commands can be used:
    1. deactivate
    1. rm -rf ~/.virtualenvs/bmi_app
    1. find . -name "*.pyc" -exec rm -f {} \;