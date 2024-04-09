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
        cql = "SELECT * FROM Users WHERE UserID=%s"
        user = session.execute(cql, [uuid.UUID(user_id)]).one()
        if user:
            return {'UserID': str(user.UserID), 'Username': user.Username, 'Email': user.Email}, 200
        else:
            return {'message': 'User not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', required=True)
        parser.add_argument('Email', required=True)
        parser.add_argument('PasswordHash', required=True)
        args = parser.parse_args()

        user_id = uuid.uuid4()
        cql = "INSERT INTO Users (UserID, Username, Email, PasswordHash) VALUES (%s, %s, %s, %s)"
        session.execute(cql, (user_id, args['Username'], args['Email'], args['PasswordHash']))
        return {'message': 'User created successfully', 'UserID': str(user_id)}, 201

    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', required=True)
        parser.add_argument('Email', required=True)
        parser.add_argument('PasswordHash', required=True)
        args = parser.parse_args()

        cql = "UPDATE Users SET Username=%s, Email=%s, PasswordHash=%s WHERE UserID=%s"
        session.execute(cql, (args['Username'], args['Email'], args['PasswordHash'], uuid.UUID(user_id)))
        return {'message': 'User updated successfully'}, 200

    def delete(self, user_id):
        cql = "DELETE FROM Users WHERE UserID=%s"
        session.execute(cql, [uuid.UUID(user_id)])
        return {'message': 'User deleted successfully'}, 200

class SnippetResource(Resource):
    def get(self, snippet_id):
        cql = "SELECT * FROM Snippets WHERE SnippetID=%s"
        snippet = session.execute(cql, [uuid.UUID(snippet_id)]).one()
        if snippet:
            return {'SnippetID': str(snippet.SnippetID), 'UserID': str(snippet.UserID), 'Title': snippet.Title, 'Content': snippet.Content, 'Language': snippet.Language, 'CreatedAt': snippet.CreatedAt, 'UpdatedAt': snippet.UpdatedAt}, 200
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
        created_at = datetime.now()
        updated_at = datetime.now()
        cql = "INSERT INTO Snippets (SnippetID, UserID, Title, Content, Language, CreatedAt, UpdatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        session.execute(cql, (snippet_id, uuid.UUID(args['UserID']), args['Title'], args['Content'], args['Language'], created_at, updated_at))
        return {'message': 'Snippet created successfully', 'SnippetID': str(snippet_id)}, 201

    def put(self, snippet_id):
        parser = reqparse.RequestParser()
        parser.add_argument('UserID', required=True)
        parser.add_argument('Title', required=True)
        parser.add_argument('Content', required=True)
        parser.add_argument('Language', required=True)
        args = parser.parse_args()

        updated_at = datetime.now()
        cql = "UPDATE Snippets SET UserID=%s, Title=%s, Content=%s, Language=%s, UpdatedAt=%s WHERE SnippetID=%s"
        session.execute(cql, (uuid.UUID(args['UserID']), args['Title'], args['Content'], args['Language'], updated_at, uuid.UUID(snippet_id)))
        return {'message': 'Snippet updated successfully'}, 200

    def delete(self, snippet_id):
        cql = "DELETE FROM Snippets WHERE SnippetID=%s"
        session.execute(cql, [uuid.UUID(snippet_id)])
        return {'message': 'Snippet deleted successfully'}, 200
    
class TagResource(Resource):
    def get(self, tag_id):
        cql = "SELECT * FROM Tags WHERE TagID=%s"
        tag = session.execute(cql, [uuid.UUID(tag_id)]).one()
        if tag:
            return {'TagID': str(tag.TagID), 'TagName': tag.TagName}, 200
        else:
            return {'message': 'Tag not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('TagName', required=True)
        args = parser.parse_args()

        tag_id = uuid.uuid4()
        cql = "INSERT INTO Tags (TagID, TagName) VALUES (%s, %s)"
        session.execute(cql, (tag_id, args['TagName']))
        return {'message': 'Tag created successfully', 'TagID': str(tag_id)}, 201

    def put(self, tag_id):
        parser = reqparse.RequestParser()
        parser.add_argument('TagName', required=True)
        args = parser.parse_args()

        cql = "UPDATE Tags SET TagName=%s WHERE TagID=%s"
        session.execute(cql, (args['TagName'], uuid.UUID(tag_id)))
        return {'message': 'Tag updated successfully'}, 200

    def delete(self, tag_id):
        cql = "DELETE FROM Tags WHERE TagID=%s"
        session.execute(cql, [uuid.UUID(tag_id)])
        return {'message': 'Tag deleted successfully'}, 200

class SnippetTagResource(Resource):
    def get(self, snippet_id, tag_id):
        cql = "SELECT * FROM SnippetTags WHERE SnippetID=%s AND TagID=%s"
        snippet_tag = session.execute(cql, [uuid.UUID(snippet_id), uuid.UUID(tag_id)]).one()
        if snippet_tag:
            return {'SnippetID': str(snippet_tag.SnippetID), 'TagID': str(snippet_tag.TagID)}, 200
        else:
            return {'message': 'SnippetTag not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('TagID', required=True)
        args = parser.parse_args()

        cql = "INSERT INTO SnippetTags (SnippetID, TagID) VALUES (%s, %s)"
        session.execute(cql, (uuid.UUID(args['SnippetID']), uuid.UUID(args['TagID'])))
        return {'message': 'SnippetTag created successfully'}, 201

    def delete(self, snippet_id, tag_id):
        cql = "DELETE FROM SnippetTags WHERE SnippetID=%s AND TagID=%s"
        session.execute(cql, [uuid.UUID(snippet_id), uuid.UUID(tag_id)])
        return {'message': 'SnippetTag deleted successfully'}, 200

class InteractionResource(Resource):
    def get(self, interaction_id):
        cql = "SELECT * FROM Interactions WHERE InteractionID=%s"
        interaction = session.execute(cql, [uuid.UUID(interaction_id)]).one()
        if interaction:
            return {'InteractionID': str(interaction.InteractionID), 'SnippetID': str(interaction.SnippetID), 'UserID': str(interaction.UserID), 'Type': interaction.Type, 'CreatedAt': interaction.CreatedAt}, 200
        else:
            return {'message': 'Interaction not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Type', required=True)
        args = parser.parse_args()

        interaction_id = uuid.uuid4()
        created_at = datetime.now()
        cql = "INSERT INTO Interactions (InteractionID, SnippetID, UserID, Type, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (interaction_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Type'], created_at))
        return {'message': 'Interaction created successfully', 'InteractionID': str(interaction_id)}, 201

    def delete(self, interaction_id):
        cql = "DELETE FROM Interactions WHERE InteractionID=%s"
        session.execute(cql, [uuid.UUID(interaction_id)])
        return {'message': 'Interaction deleted successfully'}, 200

class SnippetBountyResource(Resource):
    def get(self, bounty_id):
        cql = "SELECT * FROM SnippetBounties WHERE BountyID=%s"
        bounty = session.execute(cql, [uuid.UUID(bounty_id)]).one()
        if bounty:
            return {'BountyID': str(bounty.BountyID), 'SnippetID': str(bounty.SnippetID), 'UserID': str(bounty.UserID), 'Description': bounty.Description, 'Reward': bounty.Reward, 'Status': bounty.Status, 'CreatedAt': bounty.CreatedAt, 'DueDate': bounty.DueDate}, 200
        else:
            return {'message': 'Bounty not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Description', required=True)
        parser.add_argument('Reward', required=True)
        parser.add_argument('Status', required=True)
        parser.add_argument('DueDate', required=True)
        args = parser.parse_args()

        bounty_id = uuid.uuid4()
        created_at = datetime.now()
        cql = "INSERT INTO SnippetBounties (BountyID, SnippetID, UserID, Description, Reward, Status, CreatedAt, DueDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        session.execute(cql, (bounty_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Description'], args['Reward'], args['Status'], created_at, args['DueDate']))
        return {'message': 'Bounty created successfully', 'BountyID': str(bounty_id)}, 201
    
    def put(self, bounty_id):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Description', required=True)
        parser.add_argument('Reward', required=True)
        parser.add_argument('Status', required=True)
        parser.add_argument('DueDate', required=True)
        args = parser.parse_args()

        cql = "UPDATE SnippetBounties SET SnippetID=%s, UserID=%s, Description=%s, Reward=%s, Status=%s, DueDate=%s WHERE BountyID=%s"

        session.execute(cql, (uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Description'], args['Reward'], args['Status'], args['DueDate'], uuid.UUID(bounty_id)))
        return {'message': 'Bounty updated successfully'}, 200
    
    def delete(self, bounty_id):
        cql = "DELETE FROM SnippetBounties WHERE BountyID=%s"
        session.execute(cql, [uuid.UUID(bounty_id)])

class BugBountyResource(Resource):
    def get(self, bounty_id):
        cql = "SELECT * FROM BugBounties WHERE BountyID=%s"
        bounty = session.execute(cql, [uuid.UUID(bounty_id)]).one()
        if bounty:
            return {'BountyID': str(bounty.BountyID), 'UserID': str(bounty.UserID), 'Description': bounty.Description, 'Reward': bounty.Reward, 'Status': bounty.Status, 'CreatedAt': bounty.CreatedAt, 'DueDate': bounty.DueDate}, 200
        else:
            return {'message': 'Bounty not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('UserID', required=True)
        parser.add_argument('Description', required=True)
        parser.add_argument('Reward', required=True)
        parser.add_argument('Status', required=True)
        parser.add_argument('DueDate', required=True)
        args = parser.parse_args()

        bounty_id = uuid.uuid4()
        created_at = datetime.now()
        cql = "INSERT INTO BugBounties (BountyID, UserID, Description, Reward, Status, CreatedAt, DueDate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        session.execute(cql, (bounty_id, uuid.UUID(args['UserID']), args['Description'], args['Reward'], args['Status'], created_at, args['DueDate']))
        return {'message': 'Bounty created successfully', 'BountyID': str(bounty_id)}, 201
    
    def put(self, bounty_id):
        parser = reqparse.RequestParser()
        parser.add_argument('UserID', required=True)
        parser.add_argument('Description', required=True)
        parser.add_argument('Reward', required=True)
        parser.add_argument('Status', required=True)
        parser.add_argument('DueDate', required=True)
        args = parser.parse_args()

        cql = "UPDATE BugBounties SET UserID=%s, Description=%s, Reward=%s, Status=%s, DueDate=%s WHERE BountyID=%s"

        session.execute(cql, (uuid.UUID(args['UserID']), args['Description'], args['Reward'], args['Status'], args['DueDate'], uuid.UUID(bounty_id)))
        return {'message': 'Bounty updated successfully'}, 200
    
    def delete(self, bounty_id):
        cql = "DELETE FROM BugBounties WHERE BountyID=%s"
        session.execute(cql, [uuid.UUID(bounty_id)])

class ReportResource(Resource):
    def get(self, report_id):
        cql = "SELECT * FROM Reports WHERE ReportID=%s"
        report = session.execute(cql, [uuid.UUID(report_id)]).one()
        if report:
            return {'ReportID': str(report.ReportID), 'SnippetID': str(report.SnippetID), 'ReportedByUserID': str(report.ReportedByUserID), 'Reason': report.Reason, 'CreatedAt': report.CreatedAt}, 200
        else:
            return {'message': 'Report not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('ReportedByUserID', required=True)
        parser.add_argument('Reason', required=True)
        args = parser.parse_args()

        report_id = uuid.uuid4()
        created_at = datetime.now()
        cql = "INSERT INTO Reports (ReportID, SnippetID, ReportedByUserID, Reason, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (report_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['ReportedByUserID']), args['Reason'], created_at))
        return {'message': 'Report created successfully', 'ReportID': str(report_id)}, 201
    
    def delete(self, report_id):
        cql = "DELETE FROM Reports WHERE ReportID=%s"
        session.execute(cql, [uuid.UUID(report_id)])

class CommentResource(Resource):
    def get(self, comment_id):
        cql = "SELECT * FROM Comments WHERE CommentID=%s"
        comment = session.execute(cql, [uuid.UUID(comment_id)]).one()
        if comment:
            return {'CommentID': str(comment.CommentID), 'SnippetID': str(comment.SnippetID), 'UserID': str(comment.UserID), 'Content': comment.Content, 'CreatedAt': comment.CreatedAt}, 200
        else:
            return {'message': 'Comment not found'}, 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Content', required=True)
        args = parser.parse_args()

        comment_id = uuid.uuid4()
        created_at = datetime.now()
        cql = "INSERT INTO Comments (CommentID, SnippetID, UserID, Content, CreatedAt) VALUES (%s, %s, %s, %s, %s)"
        session.execute(cql, (comment_id, uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Content'], created_at))
        return {'message': 'Comment created successfully', 'CommentID': str(comment_id)}, 201
    
    def put(self, comment_id):
        parser = reqparse.RequestParser()
        parser.add_argument('SnippetID', required=True)
        parser.add_argument('UserID', required=True)
        parser.add_argument('Content', required=True)
        args = parser.parse_args()

        cql = "UPDATE Comments SET SnippetID=%s, UserID=%s, Content=%s WHERE CommentID=%s"
        session.execute(cql, (uuid.UUID(args['SnippetID']), uuid.UUID(args['UserID']), args['Content'], uuid.UUID(comment_id)))
        return {'message': 'Comment updated successfully'}, 200
    
    def delete(self, comment_id):
        cql = "DELETE FROM Comments WHERE CommentID=%s"
        session.execute(cql, [uuid.UUID(comment_id)])

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