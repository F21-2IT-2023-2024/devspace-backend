import requests
import uuid
import json

# Base URL of the Flask application
BASE_URL = "http://127.0.0.1:5000"

# api code

# Functions to test the API sorted in groups

def test_create_user():
    # Create a new user
    response = requests.post(BASE_URL + "/users", json={"Username": "test", "Email": "test@gmail.com", "PasswordHash": "12345678"})
    assert response.status_code == 201
    user_id = response.json()["UserID"]
    return user_id

def test_get_user(user_id):
    # Get the user
    response = requests.get(BASE_URL + "/users/" + user_id)
    assert response.status_code == 200
    assert response.json()["Username"] == "test"
    assert response.json()["Email"] == "test@gmail.com"

def test_update_user(user_id):
    # Update the user
    response = requests.put(BASE_URL + "/users/" + user_id, json={"Username": "test2", "Email": "test2@gmail.com", "PasswordHash": "12345678"})
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/users/" + user_id)
    assert response.json()["Username"] == "test2"
    assert response.json()["Email"] == "test2@gmail.com"

def test_delete_user(user_id):
    # Delete the user
    response = requests.delete(BASE_URL + "/users/" + user_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/users/" + user_id)
    assert response.status_code == 404

def test_create_snippet(user_id):
    # Create a new snippet
    response = requests.post(BASE_URL + "/snippets", json={"UserID": user_id, "Title": "test", "Content": "test", "Language": "test"})
    assert response.status_code == 201
    snippet_id = response.json()["SnippetID"]
    return snippet_id

def test_get_snippet(snippet_id):
    # Get the snippet
    response = requests.get(BASE_URL + "/snippets/" + snippet_id)
    assert response.status_code == 200
    assert response.json()["Title"] == "test"
    assert response.json()["Content"] == "test"
    assert response.json()["Language"] == "test"

def test_update_snippet(snippet_id, user_id):
    # Update the snippet
    response = requests.put(BASE_URL + "/snippets/" + snippet_id, json={"UserID": user_id, "Title": "test2", "Content": "test2", "Language": "test2"})
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/snippets/" + snippet_id)
    assert response.json()["Title"] == "test2"
    assert response.json()["Content"] == "test2"
    assert response.json()["Language"] == "test2"

def test_delete_snippet(snippet_id):
    # Delete the snippet
    response = requests.delete(BASE_URL + "/snippets/" + snippet_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/snippets/" + snippet_id)
    assert response.status_code == 404

def test_create_tag():
    # Create a new tag
    response = requests.post(BASE_URL + "/tags", json={"Name": "test"})
    assert response.status_code == 201
    tag_id = response.json()["TagID"]
    return tag_id

def test_get_tag(tag_id):
    # Get the tag
    response = requests.get(BASE_URL + "/tags/" + tag_id)
    assert response.status_code == 200
    assert response.json()["Name"] == "test"

def test_update_tag(tag_id):
    # Update the tag
    response = requests.put(BASE_URL + "/tags/" + tag_id, json={"Name": "test2"})
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/tags/" + tag_id)
    assert response.json()["Name"] == "test2"

def test_delete_tag(tag_id):
    # Delete the tag
    response = requests.delete(BASE_URL + "/tags/" + tag_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/tags/" + tag_id)
    assert response.status_code == 404

def test_create_snippet_tag(snippet_id, tag_id):
    # Create a new snippet tag
    response = requests.post(BASE_URL + "/snippettags", json={"SnippetID": snippet_id, "TagID": tag_id})
    assert response.status_code == 201

def test_delete_snippet_tag(snippet_id, tag_id):
    # Delete the snippet tag
    response = requests.delete(BASE_URL + "/snippettags/" + snippet_id + "/" + tag_id)
    assert response.status_code == 200

def test_create_interaction(snippet_id, user_id):
    # Create a new interaction
    response = requests.post(BASE_URL + "/interactions", json={"SnippetID": snippet_id, "UserID": user_id, "Type": "like"})
    assert response.status_code == 201
    interaction_id = response.json()["InteractionID"]
    return interaction_id

def test_get_interaction(interaction_id):
    # Get the interaction
    response = requests.get(BASE_URL + "/interactions/" + interaction_id)
    assert response.status_code == 200
    assert response.json()["Type"] == "like"

def test_delete_interaction(interaction_id):
    # Delete the interaction
    response = requests.delete(BASE_URL + "/interactions/" + interaction_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/interactions/" + interaction_id)
    assert response.status_code == 404

def test_create_snippet_bounty(snippet_id, user_id):
    # Create a new snippet bounty
    response = requests.post(BASE_URL + "/snippetbounties", json={"SnippetID": snippet_id, "UserID": user_id, "Amount": 10})
    assert response.status_code == 201
    bounty_id = response
    return bounty_id

def test_get_snippet_bounty(bounty_id):
    # Get the snippet bounty
    response = requests.get(BASE_URL + "/snippetbounties/" + bounty_id)
    assert response.status_code == 200
    assert response.json()["Amount"] == 10

def test_delete_snippet_bounty(bounty_id):
    # Delete the snippet bounty
    response = requests.delete(BASE_URL + "/snippetbounties/" + bounty_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/snippetbounties/" + bounty_id)
    assert response.status_code == 404

def test_create_bug_bounty(snippet_id, user_id):
    # Create a new bug bounty
    response = requests.post(BASE_URL + "/bugbounties", json={"SnippetID": snippet_id, "UserID": user_id, "Amount": 10})
    assert response.status_code == 201
    bounty_id = response
    return bounty_id

def test_get_bug_bounty(bounty_id):
    # Get the bug bounty
    response = requests.get(BASE_URL + "/bugbounties/" + bounty_id)
    assert response.status_code == 200
    assert response.json()["Amount"] == 10

def test_delete_bug_bounty(bounty_id):
    # Delete the bug bounty
    response = requests.delete(BASE_URL + "/bugbounties/" + bounty_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/bugbounties/" + bounty_id)
    assert response.status_code == 404

def test_create_report(snippet_id, user_id):
    # Create a new report
    response = requests.post(BASE_URL + "/reports", json={"SnippetID": snippet_id, "UserID": user_id, "Reason": "test"})
    assert response.status_code == 201
    report_id = response.json()["ReportID"]
    return report_id

def test_get_report(report_id):
    # Get the report
    response = requests.get(BASE_URL + "/reports/" + report_id)
    assert response.status_code == 200
    assert response.json()["Reason"] == "test"

def test_delete_report(report_id):
    # Delete the report
    response = requests.delete(BASE_URL + "/reports/" + report_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/reports/" + report_id)
    assert response.status_code == 404

def test_create_comment(snippet_id, user_id):
    # Create a new comment
    response = requests.post(BASE_URL + "/comments", json={"SnippetID": snippet_id, "UserID": user_id, "Content": "test"})
    assert response.status_code == 201
    comment_id = response.json()["CommentID"]
    return comment_id

def test_get_comment(comment_id):
    # Get the comment
    response = requests.get(BASE_URL + "/comments/" + comment_id)
    assert response.status_code == 200
    assert response.json()["Content"] == "test"

def test_delete_comment(comment_id):
    # Delete the comment
    response = requests.delete(BASE_URL + "/comments/" + comment_id)
    assert response.status_code == 200
    response = requests.get(BASE_URL + "/comments/" + comment_id)
    assert response.status_code == 404

# Test the API in logical order so all the functions can be tested

user_id = test_create_user()
test_get_user(user_id)
test_update_user(user_id)

snippet_id = test_create_snippet(user_id)
test_get_snippet(snippet_id)
test_update_snippet(snippet_id, user_id)

tag_id = test_create_tag()
test_get_tag(tag_id)
test_update_tag(tag_id)

test_create_snippet_tag(snippet_id, tag_id)
test_delete_snippet_tag(snippet_id, tag_id)

interaction_id = test_create_interaction(snippet_id, user_id)
test_get_interaction(interaction_id)
test_delete_interaction(interaction_id)

bounty_id = test_create_snippet_bounty(snippet_id, user_id)
test_get_snippet_bounty(bounty_id)
test_delete_snippet_bounty(bounty_id)

bounty_id = test_create_bug_bounty(snippet_id, user_id)
test_get_bug_bounty(bounty_id)
test_delete_bug_bounty(bounty_id)

report_id = test_create_report(snippet_id, user_id)
test_get_report(report_id)
test_delete_report(report_id)

comment_id = test_create_comment(snippet_id, user_id)
test_get_comment(comment_id)
test_delete_comment(comment_id)

test_delete_snippet(snippet_id)
test_delete_tag(tag_id)
test_delete_user(user_id)