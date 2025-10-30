# OneRoster Gradebook Service - Node.js Implementation

Node.js implementation of IMS Global OneRoster v1.2 Gradebook Service.

## Features

- ✅ **OneRoster 1.2 Compliant**: Full implementation of Gradebook Service specification
- ✅ **OAuth 2.0**: Client Credentials Grant authentication
- ✅ **RESTful API**: 16 endpoints for Categories, LineItems, and Results
- ✅ **Database**: PostgreSQL with Sequelize ORM
- ✅ **Security**: Helmet, CORS, Rate Limiting, Scope-based authorization
- ✅ **Validation**: Express-validator with OneRoster data models
- ✅ **Logging**: Winston logger with multiple transports
- ✅ **Testing**: Jest and Supertest for unit and integration tests

## Requirements

- Node.js >= 18.0.0
- PostgreSQL >= 12.0
- npm >= 8.0.0

**OR**

- Docker >= 20.10
- Docker Compose >= 2.0

## Quick Start with Docker

```bash
# Build and start services
make build
make up

# API will be available at http://localhost:3000
# View logs
make logs

# Run tests
make test

# Stop services
make down
```

## Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env
```

## Database Setup

```bash
# Create database
createdb oneroster_gradebook

# Run schema from shared folder
psql -d oneroster_gradebook -f ../../shared/database/schema.sql

# Or use Sequelize sync (development only)
# Set DB_SYNC=true in .env
```

## Environment Variables

Key configuration in `.env`:

```env
# Server
NODE_ENV=development
PORT=3000
HOST=0.0.0.0

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=oneroster_gradebook
DB_USER=postgres
DB_PASSWORD=your_password

# OAuth 2.0
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_TOKEN_LIFETIME=3600

# API
API_BASE_URL=http://localhost:3000/ims/oneroster/v1p2
ROSTERING_SERVICE_BASE_URL=http://localhost:3001/ims/oneroster/v1p2
```

## Running the Application

```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm start

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run format
```

## API Endpoints

Base URL: `http://localhost:3000/ims/oneroster/v1p2`

### Authentication

```bash
# Get access token
curl -X POST http://localhost:3000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret" \
  -d "scope=https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly"
```

### Categories

| Method | Endpoint | Description | Required Scope |
|--------|----------|-------------|----------------|
| GET | `/categories` | Get all categories | `roster.readonly` |
| GET | `/categories/{id}` | Get category by ID | `roster.readonly` |
| PUT | `/categories/{id}` | Update category | `lineitem` |
| DELETE | `/categories/{id}` | Delete category | `lineitem` |
| GET | `/categories/{id}/lineItems` | Get line items for category | `roster.readonly` |

### Line Items

| Method | Endpoint | Description | Required Scope |
|--------|----------|-------------|----------------|
| GET | `/lineItems` | Get all line items | `lineitem.readonly` |
| GET | `/lineItems/{id}` | Get line item by ID | `lineitem.readonly` |
| POST | `/lineItems` | Create line item | `lineitem` |
| PUT | `/lineItems/{id}` | Update line item | `lineitem` |
| DELETE | `/lineItems/{id}` | Delete line item | `lineitem` |
| GET | `/lineItems/{id}/results` | Get results for line item | `result.readonly` |

### Results

| Method | Endpoint | Description | Required Scope |
|--------|----------|-------------|----------------|
| GET | `/results` | Get all results | `result.readonly` |
| GET | `/results/{id}` | Get result by ID | `result.readonly` |
| POST | `/results` | Create result | `result` |
| PUT | `/results/{id}` | Update result | `result` |
| DELETE | `/results/{id}` | Delete result | `result` |

### Students

| Method | Endpoint | Description | Required Scope |
|--------|----------|-------------|----------------|
| GET | `/students/{studentId}/results` | Get all results for student | `result.readonly` |

## Query Parameters

All GET endpoints support:

- **Pagination**: `?limit=100&offset=0`
- **Filtering**: `?filter=status==active,title~Math`
- **Sorting**: `?sort=-dateLastModified,title`
- **Field Selection**: `?fields=sourcedId,title,status`

### Filter Operators

- `==` - Equals
- `!=` - Not equals
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `~` - Contains (LIKE)

### Examples

```bash
# Get active categories
GET /categories?filter=status==active

# Get line items due after 2024-01-01
GET /lineItems?filter=dueDate>2024-01-01

# Get fully graded results
GET /results?filter=scoreStatus==fully%20graded

# Pagination and sorting
GET /categories?limit=50&offset=0&sort=-dateLastModified

# Select specific fields
GET /lineItems?fields=sourcedId,title,dueDate
```

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run specific test file
npm test -- categoryController.test.js
```

## Project Structure

```
implementations/nodejs/
├── src/
│   ├── config/          # Configuration files
│   │   ├── database.js  # Sequelize configuration
│   │   └── oauth.js     # OAuth 2.0 configuration
│   ├── controllers/     # Request handlers
│   │   ├── categoryController.js
│   │   ├── lineItemController.js
│   │   └── resultController.js
│   ├── middleware/      # Express middleware
│   │   ├── auth.js      # OAuth authentication
│   │   ├── errorHandler.js
│   │   └── validators.js
│   ├── models/          # Sequelize models
│   │   ├── index.js
│   │   ├── category.js
│   │   ├── lineItem.js
│   │   └── result.js
│   ├── routes/          # Express routes
│   │   ├── categories.js
│   │   ├── lineItems.js
│   │   ├── results.js
│   │   └── students.js
│   ├── utils/           # Utility functions
│   │   └── logger.js
│   ├── app.js           # Express application
│   └── index.js         # Server entry point
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── .env.example         # Environment variables template
├── .eslintrc.js         # ESLint configuration
├── .sequelizerc         # Sequelize CLI configuration
├── package.json         # Dependencies and scripts
└── README.md            # This file
```

## OAuth 2.0 Scopes

| Scope | Description |
|-------|-------------|
| `https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly` | Read roster data |
| `https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly` | Read core roster data |
| `https://purl.imsglobal.org/spec/or/v1p2/scope/lineitem` | Read/write line items and categories |
| `https://purl.imsglobal.org/spec/or/v1p2/scope/lineitem.readonly` | Read line items |
| `https://purl.imsglobal.org/spec/or/v1p2/scope/result` | Read/write results |
| `https://purl.imsglobal.org/spec/or/v1p2/scope/result.readonly` | Read results |

## Error Handling

All errors follow OneRoster error format:

```json
{
  "imsx_codeMajor": "failure",
  "imsx_severity": "error",
  "imsx_description": "Resource not found: category-123",
  "imsx_codeMinor": "not_found"
}
```

### Common Error Codes

- `400` - `invalid_data` - Validation error
- `401` - `unauthorized` - Authentication failed
- `403` - `forbidden` - Insufficient scope
- `404` - `not_found` - Resource not found
- `409` - `conflict` - Resource conflict
- `429` - `rate_limit_exceeded` - Too many requests
- `500` - `server_error` - Internal server error

## Performance

- Response time target: < 500ms for GET requests
- Throughput: 100+ requests/second
- Database connection pooling (max: 10, min: 2)
- Rate limiting: 100 requests per minute per IP

## Security Features

- **Helmet**: HTTP security headers
- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: Prevent abuse
- **OAuth 2.0**: Industry-standard authentication
- **Scope-based Authorization**: Fine-grained access control
- **Input Validation**: Prevent injection attacks
- **SQL Injection Protection**: Parameterized queries via Sequelize

## Development

```bash
# Install development dependencies
npm install --include=dev

# Run linter
npm run lint

# Fix linting errors
npm run lint:fix

# Format code with Prettier
npm run format

# Watch mode for development
npm run dev
```

## License

This is a reference implementation for educational purposes.

## References

- [IMS Global OneRoster v1.2 Specification](https://www.imsglobal.org/spec/oneroster/v1p2)
- [OneRoster Gradebook Service](https://www.imsglobal.org/spec/oneroster/v1p2#gradebook-service)
- [OAuth 2.0 Client Credentials Grant](https://oauth.net/2/grant-types/client-credentials/)
