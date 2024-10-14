#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

class loginUser(Resource):
    def post(self):
        data=request.get_json()
        username= data.get('username')

        user=User.query.filter_by(username=username).first()

        #check if user exist
        if user:
            session['user_id'] = user.id

            return make_response(jsonify({
                'id': user.id,
                'username': user.username
            }), 200)
        return {'error': 'User not found'}, 404
api.add_resource(loginUser,'/login')


class userLogout(Resource):
    def delete(self):
    
        if 'user_id' in session:
    
            session.pop('user_id',None)

            return {},204
        
api.add_resource(userLogout, '/logout')

class check_session(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(id=session['user_id']).first()
            if user:
                return make_response(jsonify(user.to_dict()), 200)
        # Return 401 Unauthorized if no user_id in session or user not found
        return {}, 401
        
api.add_resource(check_session,'/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
