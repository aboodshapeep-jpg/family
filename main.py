from flask import Flask

app = Flask(__name__)

# Register blueprints here
# from your_blueprint import your_blueprint
# app.register_blueprint(your_blueprint)

if __name__ == '__main__':
    app.run(debug=True)