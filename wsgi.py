"""
ResumeIQ — WSGI Entrypoint for Production Serving
Exposes the Flask application instance as `application` for WSGI servers like Waitress or Gunicorn.
"""

import os
from app import app as application

if __name__ == "__main__":
    from waitress import serve

    port = int(os.environ.get("PORT", 5000))
    serve(application, host="0.0.0.0", port=port)
