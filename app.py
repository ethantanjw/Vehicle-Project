from flask import Flask
from api.routes import init_routes
from db.database import init_db

# create the Flask application
app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# initialize routes and database
init_routes(app)
init_db()

if __name__ == '__main__':
    app.run(debug=True)
