from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_restful_swagger import swagger
import uuid
from datetime import datetime
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.auth import PlainTextAuthProvider
import openai
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key=os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# scylla cloud connection
profile = ExecutionProfile(load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc='GCE_US_EAST_1')))
cluster = Cluster(
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
        contact_points=[
            "node-0.gce-us-east-1.c95c0e415ebf6dc3d47d.clusters.scylla.cloud", "node-1.gce-us-east-1.c95c0e415ebf6dc3d47d.clusters.scylla.cloud", "node-2.gce-us-east-1.c95c0e415ebf6dc3d47d.clusters.scylla.cloud"
        ],
        port=9042,
        auth_provider = PlainTextAuthProvider(username=os.getenv("SCYLLA"), password=os.getenv("SCYLLA_PASSWORD")))
session = cluster.connect()

print('Connected to cluster %s' % cluster.metadata.cluster_name)

app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1')

class UserResource(Resource):
    def get(self, user_id):
        cql = "SELECT * FROM Devspace.Users WHERE UserID=%s"
        user = session.execute(cql, [uuid.UUID(user_id)]).one()
        if user:
            return {'UserID': str(user.userid), 'Username': user.username, 'Email': user.email}, 200
        else:
            return {'message': 'User not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', required=True)
        parser.add_argument('Email', required=True)
        parser.add_argument('PasswordHash', required=True)
        args = parser.parse_args()
        print(args)

        user_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Users (UserID, Username, Email, PasswordHash) VALUES (%s, %s, %s, %s)"
        session.execute(cql, (user_id, args['Username'], args['Email'], args['PasswordHash']))
        return {'message': 'User created successfully', 'UserID': str(user_id)}, 201

    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', required=True)
        parser.add_argument('Email', required=True)
        parser.add_argument('PasswordHash', required=True)
        args = parser.parse_args()

        cql = "UPDATE Users SET Devspace.Username=%s, Email=%s, PasswordHash=%s WHERE UserID=%s"
        session.execute(cql, (args['Username'], args['Email'], args['PasswordHash'], uuid.UUID(user_id)))
        return {'message': 'User updated successfully'}, 200

    def delete(self, user_id):
        cql = "DELETE FROM Devspace.Users WHERE UserID=%s"
        session.execute(cql, [uuid.UUID(user_id)])
        return {'message': 'User deleted successfully'}, 200

class SnippetResource(Resource):
    def get(self, snippet_id):
        cql = "SELECT * FROM Devspace.Snippets WHERE SnippetID=%s"
        snippet = session.execute(cql, [uuid.UUID(snippet_id)]).one()
        if snippet:
            return {'SnippetID': str(snippet.snippetid), 'UserID': str(snippet.userid), 'Title': snippet.title, 'Content': snippet.Content, 'Language': snippet.Language, 'CreatedAt': snippet.CreatedAt, 'UpdatedAt': snippet.UpdatedAt}, 200
        else:
            return {'message': 'Snippet not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('UserID', required=True)
        parser.add_argument('Title', required=True)
        parser.add_argument('Content', required=True)
        parser.add_argument('Language', required=True)
        args = parser.parse_args()

        snippet_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Snippets (SnippetID, UserID, Title, Content, Language, CreatedAt, UpdatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        session.execute(cql, (snippet_id, uuid.UUID(args['UserID']), args['Title'], args['Content'], args['Language'], datetime.now(), datetime.now()))
        return {'message': 'Snippet created successfully', 'SnippetID': str(snippet_id)}, 201
    
    def put(self, snippet_id):
        parser = reqparse.RequestParser()
        parser.add_argument('UserID', required=True)
        parser.add_argument('Title', required=True)
        parser.add_argument('Content', required=True)
        parser.add_argument('Language', required=True)
        args = parser.parse_args()

        cql = "UPDATE Devspace.Snippets SET UserID=%s, Title=%s, Content=%s, Language=%s, UpdatedAt=%s WHERE SnippetID=%s"
        session.execute(cql, (uuid.UUID(args['UserID']), args['Title'], args['Content'], args['Language'], datetime.now(), uuid.UUID(snippet_id)))
        return {'message': 'Snippet updated successfully'}, 200
    
    def delete(self, snippet_id):
        cql = "DELETE FROM Devspace.Snippets WHERE SnippetID=%s"
        session.execute(cql, [uuid.UUID(snippet_id)])
        return {'message': 'Snippet deleted successfully'}, 200
    
class TagResource(Resource):
    def get(self, tag_id):
        cql = "SELECT * FROM Devspace.Tags WHERE TagID=%s"
        tag = session.execute(cql, [uuid.UUID(tag_id)]).one()
        if tag:
            return {'TagID': str(tag.tagid), 'Name': tag.name}, 200
        else:
            return {'message': 'Tag not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', required=True)
        args = parser.parse_args()

        tag_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Tags (TagID, Name) VALUES (%s, %s)"
        session.execute(cql, (tag_id, args['Name']))
        return {'message': 'Tag created successfully', 'TagID': str(tag_id)}, 201
    
    def put(self, tag_id):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', required=True)
        args = parser.parse_args()

        cql = "UPDATE Devspace.Tags SET Name=%s WHERE TagID=%s"
        session.execute(cql, (args['Name'], uuid.UUID(tag_id)))
        return {'message': 'Tag updated successfully'}, 200
    
    def delete(self, tag_id):
        cql = "DELETE FROM Devspace.Tags WHERE TagID=%s"
        session.execute(cql, [uuid.UUID(tag_id)])
        return {'message': 'Tag deleted successfully'}, 200
    
class SnippetTagResource(Resource):
    def get(self, snippet_id, tag_id):
        cql = "SELECT * FROM Devspace.SnippetTags WHERE SnippetID=%s AND TagID=%s"
        snippettags = session.execute(cql, [uuid.UUID(snippet_id), uuid.UUID(tag_id)]).one()
        if snippettags:
            return {'SnippetID': str(snippettags.snippetid), 'TagID': str(snippettags.tagid)}, 200
        else:
            return {'message': 'SnippetTag not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('TagID', required=True)
        args = parser.parse_args()

        cql = "INSERT INTO Devspace.SnippetTags (SnippetID, TagID) VALUES (%s, %s)"
        session.execute(cql, (uuid.UUID(args['SnippetID']), uuid.UUID(args['TagID'])))
        return {'message': 'SnippetTag created successfully'}, 201
    
    def delete(self, snippet_id, tag_id):
        cql = "DELETE FROM Devspace.SnippetTags WHERE SnippetID=%s AND TagID=%s"
        session.execute(cql, [uuid.UUID(snippet_id), uuid.UUID(tag_id)])
        return {'message': 'SnippetTag deleted successfully'}, 200
    
class InteractionResource(Resource):
    def get(self, interaction_id):
        cql = "SELECT * FROM Devspace.Interactions WHERE InteractionID=%s"
        interaction = session.execute(cql, [uuid.UUID(interaction_id)]).one()
        if interaction:
            return {'InteractionID': str(interaction.interactionid), 'SnippetID': str(interaction.snippetid), 'UserID': str(interaction.userid), 'Type': interaction.type, 'CreatedAt': interaction.createdat}, 200
        else:
            return {'message': 'Interaction not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Type', required=True)
        args = parser.parse_args()

        interaction_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Interactions (InteractionID, SnippetID, UserID, Type, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (interaction_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Type'], datetime.now()))
        return {'message': 'Interaction created successfully', 'InteractionID': str(interaction_id)}, 201
    
    def delete(self, interaction_id):
        cql = "DELETE FROM Devspace.Interactions WHERE InteractionID=%s"
        session.execute(cql, [uuid.UUID(interaction_id)])
        return {'message': 'Interaction deleted successfully'}, 200
    
class SnippetBountyResource(Resource):
    def get(self, bounty_id):
        cql = "SELECT * FROM Devspace.SnippetBounties WHERE BountyID=%s"
        bounty = session.execute(cql, [uuid.UUID(bounty_id)]).one()
        if bounty:
            return {'BountyID': str(bounty.bountyid), 'SnippetID': str(bounty.snippetid), 'UserID': str(bounty.userid), 'Amount': bounty.amount, 'CreatedAt': bounty.createdat}, 200
        else:
            return {'message': 'Bounty not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Amount', required=True)
        args = parser.parse_args()

        bounty_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.SnippetBounties (BountyID, SnippetID, UserID, Amount, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (bounty_id, uuid.UUID, args['SnippetID'], uuid.UUID(args['UserID']), args['Amount'], datetime.now()))
        return {'message': 'Bounty created successfully', 'BountyID': str(bounty_id)}, 201
    
    def delete(self, bounty_id):
        cql = "DELETE FROM Devspace.SnippetBounties WHERE BountyID=%s"
        session.execute(cql, [uuid.UUID(bounty_id)])
        return {'message': 'Bounty deleted successfully'}, 200
    
class BugBountyResource(Resource):
    def get(self, bounty_id):
        cql = "SELECT * FROM Devspace.BugBounties WHERE BountyID=%s"
        bounty = session.execute(cql, [uuid.UUID(bounty_id)]).one()
        if bounty:
            return {'BountyID': str(bounty.bountyid), 'SnippetID': str(bounty.snippetid), 'UserID': str(bounty.userid), 'Amount': bounty.amount, 'CreatedAt': bounty.createdat}, 200
        else:
            return {'message': 'Bounty not found'}, 404
        
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Amount', required=True)
        args = parser.parse_args()

        bounty_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.BugBounties (BountyID, SnippetID, UserID, Amount, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (bounty_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Amount'], datetime.now()))
        return {'message': 'Bounty created successfully', 'BountyID': str(bounty_id)}, 201

    def delete(self, bounty_id):
        cql = "DELETE FROM Devspace.BugBounties WHERE BountyID=%s"
        session.execute(cql, [uuid.UUID(bounty_id)])
        return {'message': 'Bounty deleted successfully'}, 200
    
class ReportResource(Resource):
    def get(self, report_id):
        cql = "SELECT * FROM Devspace.Reports WHERE ReportID=%s"
        report = session.execute(cql, [uuid.UUID(report_id)]).one()
        if report:
            return {'ReportID': str(report.reportid), 'SnippetID': str(report.snippetid), 'UserID': str(report.userid), 'Reason': report.reason, 'CreatedAt': report.createdat}, 200
        else:
            return {'message': 'Report not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Reason', required=True)
        args = parser.parse_args()

        report_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Reports (ReportID, SnippetID, UserID, Reason, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (report_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Reason'], datetime.now()))
        return {'message': 'Report created successfully', 'ReportID': str(report_id)}, 201
    
    def delete(self, report_id):
        cql = "DELETE FROM Devspace.Reports WHERE ReportID=%s"
        session.execute(cql, [uuid.UUID(report_id)])
        return {'message': 'Report deleted successfully'}, 200
    
class CommentResource(Resource):
    def get(self, comment_id):
        cql = "SELECT * FROM Devspace.Comments WHERE CommentID=%s"
        comment = session.execute(cql, [uuid.UUID(comment_id)]).one()
        if comment:
            return {'CommentID': str(comment.commentid), 'SnippetID': str(comment.snippetid), 'UserID': str(comment.userid), 'Content': comment.content, 'CreatedAt': comment.createdat}, 200
        else:
            return {'message': 'Comment not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Content', required=True)
        args = parser.parse_args()

        comment_id = uuid.uuid4()
        cql = "INSERT INTO Devspace.Comments (CommentID, SnippetID, UserID, Content, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (comment_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Content'], datetime.now()))
        return {'message': 'Comment created successfully', 'CommentID': str(comment_id)}, 201
    
    def delete(self, comment_id):
        cql = "DELETE FROM Devspace.Comments WHERE CommentID=%s"
        session.execute(cql, [uuid.UUID(comment_id)])
        return {'message': 'Comment deleted successfully'}, 200

class ContentFilter():
    def content_safe(content):
        moderation = client.moderations.create(input=content)
        response = moderation.model_dump()
        return not response['results'][0]['flagged']

api.add_resource(UserResource, '/users', '/users/<string:user_id>')
api.add_resource(SnippetResource, '/snippets', '/snippets/<string:snippet_id>')
api.add_resource(TagResource, '/tags', '/tags/<string:tag_id>')
api.add_resource(SnippetTagResource, '/snippettags', '/snippettags/<string:snippet_id>/<string:tag_id>')
api.add_resource(InteractionResource, '/interactions', '/interactions/<string:interaction_id>')
api.add_resource(SnippetBountyResource, '/snippetbounties', '/snippetbounties/<string:bounty_id>')
api.add_resource(BugBountyResource, '/bugbounties', '/bugbounties/<string:bounty_id>')
api.add_resource(ReportResource, '/reports', '/reports/<string:report_id>')
api.add_resource(CommentResource, '/comments', '/comments/<string:comment_id>')

if __name__ == '__main__':
    app.run(debug=True)