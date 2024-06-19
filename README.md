# Submission Description

## Approach

**Backend**:

- Dockerized microservice.
- Python for its natural benefit of working with AI applications combined with FastAPI for ease of use and performance.
- OpenAI for natural language processing.

**Frontend**:

- Simple static HTML, JS, and CSS served from the backend container itself.

**Database**:

- MariaDB for its compatibility with MySQL and its support for system-versioned tables to allow for queries on past state of the data.

**Infrastructure**:

- AWS EC2 for hosting the application, AWS RDS for the database allowing for free tier usage.
- Github Actions powering CI/CD capabilities.

## Challenges and Trade-offs

- **Availability / Scalability**: Processing webhook events of unknown frequency and volume. Considerations about restructuring the application to support batch processing or refactoring it into multiple microservices or AWS Lambda functions. The trade-off here involves the convenience and rapid development afforded by using Docker containers against the operational and scalability benefits of serverless architecture.

- **Determining the Database Structure**: Opted for a SQL engine because of its ease of use and familiarity, with system-versioned tables to allow for querying past states of the data independently of the tables schema. The trade-off here is that a NoSQL database or a knowledge graph may be a better fit for scalability and general AI use cases; however, the history-tracking capabilities would require more effort, as would building the natural language translator.

- **Translating NL Queries**: Opted to use an LLM (ChatGPT) to externalize that complex responsibility. The trade-off was sanitizing inputs and handling edge cases where unsafe operations might be requested.

## Plan for Further Work

- **Features / Domain Improvements**: Consider using a chain of AIs to power natural language translations and evaluate whether the current database structure and schema is the best fit for the use case.
  
- **Authentication**: Implement authentication for the `accept_webhook` endpoint to ensure that only authorized systems can trigger webhooks.
  
- **Other Security Enhancements**: Add a feature to request ChatGPT to flag potentially unsafe SQL operations and handle these scenarios gracefully in the code.
  
- **Batch and Async Processing**: Enhance the system to support batch and asynchronous processing of webhooks, improving performance and scalability.
  
- **Microservices and Lambda Functions**: Further explore refactoring the application into smaller microservices or AWS Lambda functions to leverage serverless architecture benefits.
  
- **Better Testing**: Improve unit test coverage and develop comprehensive integration / E2E tests to validate the system's behavior and components interactions in a live-like environment.
  
- **DevOps Improvements**: Terraforming resources instead of manual provisioning, restricting AWS security rules, using a non-root database user, serving the frontend from Amazon S3, and adding a reverse proxy with HTTPS support.

By addressing these areas, the project can achieve higher security, performance, and maintainability, making it better suited for production use.

## Further info

The service is hosted at: <http://54.78.7.180/>. Most routes are accessible via traditional REST while there is only one FE route at `/nl-to-sql`.

Example curl request to add a person:

```sh
curl -X POST http://54.78.7.180/accept_webhook \
     -H "Content-Type: application/json" \
     -d '{
           "payload_type": "PersonAdded",
           "payload_content": {
             "person_id": "d59abfc4-3aae-4e29-875b-7b56e021ad63",
             "name": "Jane Austen",
             "timestamp": "2023-10-10T10:00:00Z"
           }
         }'
```

OpenAPI specs can be accessed at the `/docs` endpoint, while other info is dispersed inline in the code.
