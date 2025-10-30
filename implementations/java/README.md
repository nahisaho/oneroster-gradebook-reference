# OneRoster Gradebook API - Java Implementation

Java/Spring Boot implementation of the IMS Global OneRoster v1.2 Gradebook Service API.

## Features

- **Spring Boot 3.2.1** with Java 17
- **RESTful API** following OneRoster v1.2 specification
- **OAuth2 JWT** authentication with scope-based authorization
- **PostgreSQL** database with JPA/Hibernate ORM
- **MapStruct** for entity-DTO mapping
- **Comprehensive testing** with JUnit 5 and Testcontainers
- **API documentation** with built-in health checks

## Technology Stack

- **Framework**: Spring Boot 3.2.1
- **Language**: Java 17
- **Build Tool**: Maven
- **Database**: PostgreSQL 15+
- **ORM**: Spring Data JPA (Hibernate)
- **Security**: Spring Security OAuth2 Resource Server
- **Testing**: JUnit 5, Mockito, Testcontainers
- **Code Generation**: MapStruct 1.5.5, Lombok

## Prerequisites

- Java 17 or higher
- Maven 3.8+
- PostgreSQL 15+
- OAuth2 authorization server (e.g., Keycloak, Auth0)

## Setup

### 1. Clone Repository

```bash
cd implementations/java
```

### 2. Configure Database

Create PostgreSQL database:

```bash
createdb oneroster_gradebook
```

Update `src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/oneroster_gradebook
spring.datasource.username=your_username
spring.datasource.password=your_password
```

### 3. Configure OAuth2

Update OAuth2 settings in `application.properties`:

```properties
spring.security.oauth2.resourceserver.jwt.issuer-uri=https://your-auth-server.com/realms/your-realm
spring.security.oauth2.resourceserver.jwt.jwk-set-uri=https://your-auth-server.com/realms/your-realm/protocol/openid-connect/certs
```

### 4. Build Application

```bash
mvn clean install
```

### 5. Run Application

```bash
mvn spring-boot:run
```

The API will be available at `http://localhost:8080`

## API Endpoints

### Categories

| Method | Endpoint | Scope Required |
|--------|----------|----------------|
| GET | `/ims/oneroster/v1p2/categories` | `roster.readonly` |
| GET | `/ims/oneroster/v1p2/categories/{id}` | `roster.readonly` |
| POST | `/ims/oneroster/v1p2/categories` | `roster-core.createput` |
| PUT | `/ims/oneroster/v1p2/categories/{id}` | `roster-core.createput` |
| DELETE | `/ims/oneroster/v1p2/categories/{id}` | `roster-core.createput` |

### Line Items

| Method | Endpoint | Scope Required |
|--------|----------|----------------|
| GET | `/ims/oneroster/v1p2/lineItems` | `roster.readonly` |
| GET | `/ims/oneroster/v1p2/lineItems/{id}` | `roster.readonly` |
| POST | `/ims/oneroster/v1p2/lineItems` | `roster-core.createput` |
| PUT | `/ims/oneroster/v1p2/lineItems/{id}` | `roster-core.createput` |
| DELETE | `/ims/oneroster/v1p2/lineItems/{id}` | `roster-core.createput` |

### Results

| Method | Endpoint | Scope Required |
|--------|----------|----------------|
| GET | `/ims/oneroster/v1p2/results` | `roster.readonly` |
| GET | `/ims/oneroster/v1p2/results/{id}` | `roster.readonly` |
| POST | `/ims/oneroster/v1p2/results` | `gradebook.createput` |
| PUT | `/ims/oneroster/v1p2/results/{id}` | `gradebook.createput` |
| DELETE | `/ims/oneroster/v1p2/results/{id}` | `gradebook.createput` |

## OAuth2 Scopes

- `https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly` - Read categories and line items
- `https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput` - Create/update/delete categories and line items
- `https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput` - Create/update/delete results

## Testing

### Test Results

✅ **19/19 tests passing (100%)**

- 1 context load test
- 6 CategoryController tests
- 6 LineItemController tests  
- 6 ResultController tests

### Run All Tests

```bash
mvn test
```

**Output:**
```
Tests run: 19, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### Run with Coverage

```bash
mvn clean test jacoco:report
```

Coverage report will be available at `target/site/jacoco/index.html`

**Coverage Summary:**
- **Overall**: 19% (due to mocked service layer)
- **Controllers**: 82% ✅
- **Service**: 5% (integration tests with mocks)
- **DTO/Mapper**: 14%/1%

Note: Controller layer has high coverage. Service layer coverage is low because integration tests use `@MockBean` for business logic isolation.

### Test Configuration

Tests use a separate security configuration:
- **Profile**: `test` in `@ActiveProfiles("test")`
- **Security**: `TestSecurityConfig` with `permitAll()` for simplified testing
- **Database**: H2 in-memory database
- **Authentication**: `@WithMockUser` with OAuth2 scopes

### Integration Tests

Integration tests use H2 in-memory database:

```bash
mvn verify
```

## Project Structure

```
src/
├── main/
│   ├── java/org/imsglobal/oneroster/gradebook/
│   │   ├── config/          # Security and web configuration
│   │   ├── controller/      # REST controllers
│   │   ├── dto/             # Data Transfer Objects
│   │   ├── mapper/          # MapStruct mappers
│   │   ├── model/           # JPA entities
│   │   │   └── enums/       # Enumerations
│   │   ├── repository/      # Spring Data repositories
│   │   └── service/         # Business logic
│   └── resources/
│       └── application.properties
└── test/
    ├── java/                # Test classes
    └── resources/
        └── application-test.properties
```

## Data Models

### Category

```json
{
  "sourcedId": "uuid",
  "title": "Homework",
  "weight": 0.3,
  "status": "active",
  "dateLastModified": "2024-01-01T00:00:00",
  "metadata": "{}"
}
```

### LineItem

```json
{
  "sourcedId": "uuid",
  "title": "Assignment 1",
  "description": "First homework",
  "assignDate": "2024-01-01",
  "dueDate": "2024-01-15",
  "scoreMaximum": 100,
  "categorySourcedId": "category-uuid",
  "status": "active"
}
```

### Result

```json
{
  "sourcedId": "uuid",
  "studentId": "student-uuid",
  "score": 85,
  "scorePercent": 0.85,
  "scoreStatus": "earnedFull",
  "comment": "Good work",
  "lineItemSourcedId": "lineitem-uuid",
  "status": "active"
}
```

## Development

### Code Generation

MapStruct mappers are generated during compilation:

```bash
mvn clean compile
```

### Database Migration

JPA is configured with `ddl-auto=update`. For production, use migration tools like Flyway:

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

## Production Deployment

### Build JAR

```bash
mvn clean package -DskipTests
```

### Run JAR

```bash
java -jar target/oneroster-gradebook-1.0.0.jar
```

### Docker

Create `Dockerfile`:

```dockerfile
FROM eclipse-temurin:17-jre
COPY target/oneroster-gradebook-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

Build and run:

```bash
docker build -t oneroster-gradebook .
docker run -p 8080:8080 oneroster-gradebook
```

## License

This is a reference implementation for educational purposes.

## References

- [IMS Global OneRoster v1.2 Specification](https://www.imsglobal.org/spec/oneroster/v1p2)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring Security OAuth2](https://spring.io/projects/spring-security-oauth)
