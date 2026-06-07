# SyanoURL

A URL Shortener with authentication, click analysis, custom short codes and QR Code Generation.
Made for VRIT TECHNLOGIES Intern Task.

Built with:
Django REST Framework (Backend)
HTML/JS (Fronted)

#### Important Note and disclaimer:

    The Frontend is not reactive. Please refresh to update the click count and analytics.
    CORS_ALLOW_ALL_ORIGINS = True in settings.py. This should be tightened in a real environment.
    DEBUG = True, and SECRET_KEY is still hardcoded in settings.py. Proper environment variables should be used.

## Installation (Setup and running the project):

### 1. Clone the reposistory.

```bash
git clone <repo-url>
cd SyanoURL
```

### 2. Create and activate the virtual environment inside the backend folder.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate #for mac and linux
# .venv\Scripts\activate #for windows
```

### 3. Install dependencies for the backend.

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create a superuser for the Django admin panel

```bash
python manage.py createsuperuser
```

### 6. Start the backend server

```bash
python manage.py runserver
```

Note that the server runs on PORT 8000 by default.
If you wish to use another port, you must change the PORT constants in /frontend/index.html, /frontend/login.html, and /frontend/dash.html

### 7. Open the frontend

Open '/frontend/index.html' in your browser directly.

## API DOCUMENTATION

All API endpoints are prefixed with: "http://localhost:8000".

### Authentication Endpoints

#### POST /api/auth/signup/

    Public API.
    Registers a new user.
    Issues access and refresh tokens immediately on signup, so the user is logged in right away.

Example request:

```json
{
  "username": "vibhab",
  "email": "vibhab@example.com",
  "password": "securepassword123",
  "password2": "securepassword123"
}
```

Example response 201 Created:

```json
{
  "user": {
    "id": 1,
    "username": "vibhab",
    "email": "vibhab@example.com"
  },
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### POST /api/auth/login/

    Public API.
    Logs a user in.
    Returns JWT access and refresh tokens along with basic user info.

Example request:

```json
{
  "username": "vibhab",
  "password": "securepassword123"
}
```

Example response 200 OK:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "vibhab",
    "email": "vibhab@example.com"
  }
}
```

#### POST /api/auth/logout/

    Protected API.
    Logs the user out.
    Blacklists the refresh token so it cannot be used to issue new access tokens.

#### POST /api/auth/token/refresh/

    Public API.
    Issues a new access token using a valid refresh token.
    Provided by SimpleJWT. Also returns a new refresh token since ROTATE_REFRESH_TOKENS is enabled.

#### GET /api/auth/me/

    Protected API.
    Returns the currently logged in user's info.

Example response `200 OK`:

```json
{
  "id": 1,
  "username": "vibhab",
  "email": "vibhab@example.com"
}
```

### URL Shortener Endpoints

#### GET /api/shorter/

    Protected API.
    Returns all short links owned by the currently logged in user.

Example response:

```json
[
  {
    "id": 1,
    "og_url": "https://example.com/very/long/url",
    "short_code": "aB3kX9z",
    "is_custom": false,
    "expires_at": "2026-06-17T10:00:00Z",
    "created_at": "2026-06-07T10:00:00Z",
    "click_count": 5,
    "is_expired": false
  },
  {
    "id": 2,
    "og_url": "https://another.com/long/url",
    "short_code": "mylink",
    "is_custom": true,
    "expires_at": "2026-06-17T10:00:00Z",
    "created_at": "2026-06-07T10:00:00Z",
    "click_count": 0,
    "is_expired": false
  }
]
```

---

#### POST /api/shorter/

    Protected API.
    Creates a new short link for the logged in user.
    custom_code and expires_at are optional.
    If custom_code is omitted, a random 7-character Base62 code is generated.
    If expires_at is omitted, the link expires 10 days from creation.
    custom_code must be alphanumeric only (a-z, 0-9), between 3 and 50 characters.

Example request:

```json
{
  "og_url": "https://example.com/very/long/url",
  "custom_code": "mylink",
  "expires_at": "2026-12-31T23:59:00Z"
}
```

Example response `201 Created`:

```json
{
  "id": 3,
  "og_url": "https://example.com/very/long/url",
  "short_code": "mylink",
  "is_custom": true,
  "expires_at": "2026-12-31T23:59:00Z",
  "created_at": "2026-06-07T10:00:00Z",
  "click_count": 0,
  "is_expired": false
}
```

#### GET /api/shorter/\<id\>/

    Protected API.
    Returns the details of a single short link owned by the logged in user.
    Includes the full list of click timestamps for analytics.

Example response:

```json
{
  "id": 1,
  "og_url": "https://example.com/very/long/url",
  "short_code": "aB3kX9z",
  "is_custom": false,
  "expires_at": "2026-06-17T10:00:00Z",
  "created_at": "2026-06-07T10:00:00Z",
  "click_count": 3,
  "is_expired": false,
  "clicks": [
    { "id": 3, "clicked_at": "2026-06-07T12:30:00Z" },
    { "id": 2, "clicked_at": "2026-06-07T11:15:00Z" },
    { "id": 1, "clicked_at": "2026-06-07T10:05:00Z" }
  ]
}
```

---

#### DELETE /api/shorter/\<id\>/

    Protected API.
    Deletes a short link owned by the logged in user.
    Also deletes all associated click records (cascade).

    Returns 204 No Content on success.

---

#### GET /api/shorter/\<id\>/qr/

    Protected API.
    Generates and returns a QR code for the short link as a PNG image.
    The QR code encodes the public redirect URL (http://localhost:8000/r/<code>/)
    so that every scan is recorded as a click in analytics.

    Returns: image/png

---

#### GET /r/\<code\>/

    Public API.
    Resolves a short code, records a click, and redirects the user to the original URL.
    Returns 302 Found on success.
    Returns 410 Gone with an HTML page if the link has expired.
    Returns 404 Not Found if the short code does not exist.

## Features:

## 1. Short Code Generation Algorithm

- Uses **Base62 encoding** — an alphabet of 62 characters (0-9, a-z, A-Z)
- Generates codes that are exactly **7 characters long**, giving around 3.5 trillion possible combinations
- A random integer is picked in the full 62^7 range, then converted to Base62 by repeatedly dividing by 62 and mapping each remainder to a character in the alphabet
- Left-padded with 0 to ensure consistent length
- On creation, the server checks if the generated code already exists in the database and retries up to 10 times in the unlikely event of a collision

---

## 2. Custom Short Codes

- Users can optionally supply their own short code instead of getting a randomly generated one
- Custom codes are validated for two things: **format** (alphanumeric only, a-z and 0-9) and **uniqueness** (checked against existing codes in the database)
- If validation passes, the custom code is used directly as the short_code — the Base62 generator is skipped entirely
- A boolean is_custom flag is stored on the link so the dashboard can visually distinguish custom-coded links from auto-generated ones if needed, although I have not distinguished between them visually

---

## 3. Expiry

- Every short link has an expires_at datetime stored in the database
- If the user does not provide one, it defaults to **10 days from the moment of creation**
- On every redirect request, the server checks if the current time is past `expires_at`
- If expired, a **410 Gone** HTML page is served instead of redirecting — 410 is used over 404 because the resource existed but is intentionally no longer available
- If a user provides an expiry date in the past, the serializer rejects it with a validation error

---

## 4. QR Code Generation

- QR codes are generated on demand that means nothing is stored on the server, the image is created fresh on every request
- The QR code encodes the **short URL** (e.g. `localhost:8000/r/<code>/`), not the original long URL — this ensures every scan goes through the redirect endpoint and is counted as a click in analytics
- The image is generated in memory and returned directly as a image/png response
- On the frontend, because the endpoint requires an auth token and browsers do not send custom headers for regular image requests, the PNG is fetched manually with the token attached, converted to a blob URL, and then displayed inline
- The same blob URL doubles as the download link, so the user can both view and save the QR code from the same button click
