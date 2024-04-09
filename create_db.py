from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.auth import PlainTextAuthProvider
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

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

session.execute("CREATE KEYSPACE IF NOT EXISTS Devspace WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}")

table_commands = [
    """CREATE TABLE IF NOT EXISTS Devspace.Users (
        UserID UUID PRIMARY KEY,
        Username TEXT,
        Email TEXT,
        PasswordHash TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.Snippets (
        SnippetID UUID PRIMARY KEY,
        UserID UUID,
        Title TEXT,
        Content TEXT,
        Language TEXT,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.Tags (
        TagID UUID PRIMARY KEY,
        TagName TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.SnippetTags (
        SnippetID UUID,
        TagID UUID,
        PRIMARY KEY (SnippetID, TagID)
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.Interactions (
        InteractionID UUID PRIMARY KEY,
        SnippetID UUID,
        UserID UUID,
        Type TEXT,
        CreatedAt TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.SnippetBounties (
        BountyID UUID PRIMARY KEY,
        SnippetID UUID,
        UserID UUID,
        Description TEXT,
        Reward INT,
        Status TEXT,
        CreatedAt TIMESTAMP,
        DueDate TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.BugBounties (
        BountyID UUID PRIMARY KEY,
        UserID UUID,
        Description TEXT,
        Reward INT,
        Status TEXT,
        CreatedAt TIMESTAMP,
        DueDate TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.Reports (
        ReportID UUID PRIMARY KEY,
        SnippetID UUID,
        ReportedByUserID UUID,
        Reason TEXT,
        CreatedAt TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS Devspace.Comments (
        CommentID UUID PRIMARY KEY,
        SnippetID UUID,
        UserID UUID,
        Content TEXT,
        CreatedAt TIMESTAMP
    )"""
]

for command in table_commands:
    session.execute(command)

print('Tables created successfully.')