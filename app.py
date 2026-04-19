"""
CodeCraftHub - A Simple Learning Platform for Developers
=========================================================
This Flask application helps developers track their learning courses.
It uses a JSON file for storage (no database needed).

Key Concepts for Beginners:
- REST API: A way for applications to communicate over HTTP
- JSON: A text format for storing and exchanging data
- Flask Routes: URLs that trigger specific functions
- HTTP Methods: GET (read), POST (create), PUT (update), DELETE (remove)
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Path to our JSON file
DATA_FILE = 'courses.json'

# Valid status options for courses
VALID_STATUSES = ['Not Started', 'In Progress', 'Completed']


def initialize_data_file():
    """
    Creates the courses.json file if it doesn't exist.
    This runs when the application starts.

    Returns:
        bool: True if file was created or already exists
    """
    try:
        if not os.path.exists(DATA_FILE):
            print(f"📁 Creating {DATA_FILE}...")
            with open(DATA_FILE, 'w') as f:
                # Start with an empty list of courses
                json.dump([], f)
            print(f"✅ {DATA_FILE} created successfully!")
        else:
            print(f"✅ {DATA_FILE} already exists.")
        return True
    except Exception as e:
        print(f"❌ Error creating {DATA_FILE}: {str(e)}")
        return False


# Read courses from JSON file
def read_courses():
    """
      Reads all courses from the JSON file.

      Returns:
          list: List of course dictionaries, or empty list if error occurs

      Error Handling:
          - FileNotFoundError: If courses.json doesn't exist
          - JSONDecodeError: If the file contains invalid JSON
          - General exceptions: Any other file read errors
      """
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Write courses to JSON file
def write_courses(courses):
    """
        Writes the courses list to the JSON file.

        Args:
            courses (list): List of course dictionaries to save

        Returns:
            tuple: (success: bool, error_message: str or None)

        Error Handling:
            - IOError: Problems writing to file (permissions, disk space, etc.)
            - TypeError: If courses can't be converted to JSON
        """
    with open(DATA_FILE, 'w') as f:
        json.dump(courses, f, indent=4)


# Generate unique ID for new courses
def generate_id(courses):
    if not courses:
        return 1
    return max(course['id'] for course in courses) + 1


# Validate course status
def is_valid_status(status):
    valid_statuses = ['Not Started', 'In Progress', 'Completed']
    return status in valid_statuses


# ============================================
# REST API ENDPOINTS
# ============================================

# HOME - Welcome endpoint
@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to CodeCraftHub!',
        'endpoints': {
            'GET /api/courses': 'Get all courses',
            'GET /api/courses/stats': 'Get course stats',
            'GET /api/courses/<id>': 'Get a specific course',
            'POST /api/courses': 'Create a new course',
            'PUT /api/courses/<id>': 'Update a course',
            'DELETE /api/courses/<id>': 'Delete a course',
            'GET /api/courses/status/<status>': 'Filter courses by status'
        }
    })


# GET all courses
@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    courses = read_courses()
    return jsonify({
        'success': True,
        'count': len(courses),
        'courses': courses
    }), 200

# GET all courses
@app.route('/api/courses/stats', methods=['GET'])
def get_course_stats():
    courses = read_courses()
    statuses = {
        "Not Started": 0,
        "In Progress": 0,
        "Completed": 0,
    }
    for c in courses:
        if c['status'] in statuses:
            statuses[c['status']] += 1
        else:
            print(f"{c['name']} does not have a valid status: {c['status']}")

    return jsonify({
        'success': True,
        'Number of Courses': len(courses),
        'Courses By Status': statuses
    }), 200


# GET a specific course by ID
@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    courses = read_courses()
    course = next((c for c in courses if c['id'] == course_id), None)

    if course:
        return jsonify({
            'success': True,
            'course': course
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': f'Course with ID {course_id} not found'
        }), 404


# PUT update course
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    courses = read_courses()

    course_index = next((i for i, c in enumerate(courses) if c['id'] == course_id), None)

    if course_index is None:
        return jsonify({'success': False, 'error': 'Course not found'}), 404

    # Update fields if provided
    course = courses[course_index]
    if 'name' in data:
        course['name'] = data['name']
    if 'description' in data:
        course['description'] = data['description']
    if 'target_date' in data:
        course['target_date'] = data['target_date']
    if 'status' in data:
        course['status'] = data['status']

    write_courses(courses)

    return jsonify({
        'success': True,
        'message': 'Course updated successfully',
        'course': course
    }), 200


# DELETE course
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    courses = read_courses()
    course_index = next((i for i, c in enumerate(courses) if c['id'] == course_id), None)

    if course_index is None:
        return jsonify({'success': False, 'error': 'Course not found'}), 404

    deleted_course = courses.pop(course_index)
    write_courses(courses)

    return jsonify({
        'success': True,
        'message': 'Course deleted successfully',
        'deleted_course': deleted_course
    }), 200

# POST - Create a new course
@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'description', 'target_completion_date', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400

    # Validate status
    if not is_valid_status(data['status']):
        return jsonify({
            'success': False,
            'message': 'Invalid status. Use: Not Started, In Progress, or Completed'
        })

    courses = read_courses()

    new_course = {
        'id': generate_id(courses),
        'name': data['name'],
        'description': data['description'],
        'target_completion_date': data['target_completion_date'],
        'status': data['status'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    courses.append(new_course)
    write_courses(courses)

    return jsonify({
        'success': True,
        'message': 'Course added successfully',
        'course': new_course
    }), 201





if __name__ == '__main__':
    print("CodeCraftHub API is starting...")
    print(f"Data will be stored in: {os.path.abspath(DATA_FILE)}")
    print("API will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
