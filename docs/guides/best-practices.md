```markdown
# Chapter 6: Best Practices & Error Handling

Guidelines for using the API efficiently and safely.

## 6.1. Understanding HTTP Status Codes

The Flowork API uses standard HTTP status codes to inform you of the result of a request.

-   **`200 OK`**: The request was successful and the server is returning data.
-   **`201 Created`**: The request was successful and a new resource was created.
-   **`202 Accepted`**: The request has been accepted for background processing. You need to check its status later.
-   **`400 Bad Request`**: Something is wrong with your request, such as invalid JSON or missing data.
-   **`404 Not Found`**: The resource you requested does not exist.
-   **`500 Internal Server Error`**: An error occurred inside the Flowork engine. Check the Flowork terminal logs for details.

## 6.2. Error Message Format

In case of an error (4xx or 5xx codes), the server will always try to return a JSON response with this format:

```json
{
    "error": "A description of the problem that occurred here."
}