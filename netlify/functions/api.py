import sys
import os

# Add project root and Backend to Python path
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BACKEND_DIR)

from app import app


def handler(event, context):
    from awsgi import response
    return response(app, event, context)