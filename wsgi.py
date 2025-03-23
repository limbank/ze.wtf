# import zewtf Flask application
from models import create_tables
from zewtf import app

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
