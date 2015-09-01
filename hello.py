###########################
# Flask 'Hello World' App #
###########################

#### In 3 simple steps ####

# Import and initilize
# the Flask object
from flask import Flask
app = Flask(__name__)

# Add URL routes
@app.route('/')
def index():
    return "Hello World!"

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

###########################
# To run it:
#
# $ source venv/Scripts/activate
# (venv) $ python hello.py
#
###########################
