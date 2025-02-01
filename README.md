# FAQ Management System

## Features
### WYSIWYG Editor in Admin Pannel
- The application implements a well maintained WYSIWYG editor for creating FAQs.
- Features such as **searching**, **sorting** and **pagination** are implemented in the editor.

### Authentication
- APIs are classififed into two categories namely **public** and **protected (Admin-Only)**.
- Reading the FAQs(including in any particular language) is public, while creating, updating and deleting the APIs are only restricted to Admin user.

### Pre-Translation of FAQs in top-5 langauges (Seperate threads)
- Application pre-translates the FAQs in top-5 langauges for fast access and better performance.
- Pre-translation is assigned to a new **thread** as it invloves requesting google API for translation and retrying if the the request fails. So the main thread should not be blocked.
- Application supports over **100+ languages** and except the top-5, other languages are translated **dynamically** when the user requests the FAQs in that partcular language.

### Redis for Cache
- Redis cloud is used as cache. It stores the frequent FAQs and returns them whenever requested, reducing the access time for frequently requested FAQs.


## Installation and Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Sonugupta2001/myFAQs.git
   cd faq-management-system
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:

   Create a `.env` file in the project root with the following variables:

   ```plaintext
   REDIS_HOST=your_redis_host
   REDIS_PORT=your_redis_port
   REDIS_PASSWORD=your_redis_password
   ADMIN_USERNAME=admin_username
   ADMIN_PASSWORD=admin_password
   ADMIN_EMAIL=admin_email
   ```

5. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

7. **Build and Run the Docker Container (optional)**:

   ```bash
   docker-compose up --build
   ```


   The application will be available at `http://localhost:8000`.




## API Endpoints

### Public APIs

#### 1. List FAQs
- **Endpoint**: `GET /api/faqs/`
- **Description**: Retrieves a list of all FAQs.
- **Query Parameters**: 
  - `lang` (optional): Language code for translated content (e.g., 'hi', 'bn').

- **Sample Request**:
  ```http
  GET /api/faqs/?lang=hi
  ```
- **Sample Response**:
  ```json
  [
      {
          "id": 1,
          "question": "What is Django",
          "answer": "Django is a web framework for python",
          "created_at": "2024-01-20T10:30:00Z"
      },
      {
          "id": 2,
          "question": "what is REST",
          "answer": "REST is a design framework for creating APIs",
          "created_at": "2024-01-20T10:35:00Z"
      }
  ]
  ```

#### 2. Retrieve FAQ
- **Endpoint**: `GET /api/faqs/<id>/`
- **Description**: Retrieves a specific FAQ by ID.
- **Query Parameters**: 
  - `lang` (optional): Language code for translated content.
- **Sample Request**:
  ```http
  GET /api/faqs/1/?lang=hi
  ```
- **Sample Response**:
  ```json
  {
      "id": 1,
      "question": "Django क्या है?",
      "answer": "Django एक उच्च-स्तरीय Python वेब फ्रेमवर्क है।",
      "created_at": "2024-01-20T10:30:00Z"
  }
  ```


### Restricted(Admin-Only) APIs

#### 1. Create FAQ
- **Endpoint**: `POST /api/faqs/`
- **Description**: Creates a new FAQ. (Admin only)
- **Request Body**:
  ```json
  {
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other."
  }
  ```
- **Sample Response**:
  ```json
  {
      "id": 3,
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other.",
      "created_at": "2024-01-20T11:00:00Z"
  }
  ```

#### 2. Update FAQ
- **Endpoint**: `PATCH /api/faqs/<id>/`
- **Description**: Updates an existing FAQ. (Admin only)
- **Request Body**:
  ```json
  {
      "question": "What is Django Framework?",
      "answer": "Django is a high-level Python web framework that enables rapid development of secure and maintainable websites."
  }
  ```
- **Sample Response**:
  ```json
  {
      "id": 1,
      "question": "What is Django Framework?",
      "answer": "Django is a high-level Python web framework that enables rapid development of secure and maintainable websites.",
      "created_at": "2024-01-20T10:30:00Z"
  }
  ```

#### 3. Delete FAQ
- **Endpoint**: `DELETE /api/faqs/<id>/`
- **Description**: Deletes a specific FAQ. (Admin only)
- **Response**: Returns HTTP 204 No Content on successful deletion.


## Error Responses

1. **Not Found (404)**:
   - **Description**: The requested resource does not exist.
   - **Response**:
     ```json
     {
         "detail": "Not found."
     }
     ```

2. **Unauthorized (401)**:
   - **Description**: Authentication credentials were not provided or are invalid.
   - **Response**:
     ```json
     {
         "detail": "Authentication credentials were not provided."
     }
     ```

3. **Forbidden (403)**:
   - **Description**: The user does not have permission to perform the action (e.g., non-admin trying to create an FAQ).
   - **Response**:
     ```json
     {
         "detail": "You do not have permission to perform this action."
     }
     ```

4. **Rate Limit Exceeded (429)**:
   - **Description**: Too many requests have been made in a short period.
   - **Response**:
     ```json
     {
         "detail": "Request was throttled. Expected available in <X> seconds."
     }
     ```

5. **Bad Request (400)**:
   - **Description**: The request was malformed or invalid.
   - **Response**:
     ```json
     {
         "error": "Invalid request parameters"
     }
     ```



## Testing

- **Run Tests**: Used Django's testing framework to run unit tests for testing API responses and models.

  ```bash
  python manage.py test
  ```



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---