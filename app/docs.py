# Documentation examples and responses for endpoints

accept_webhook_examples = {
    "PersonAdded": {
        "summary": "A request example for a person added event",
        "description": "Example payload when a person is added.",
        "value": {
            "payload_type": "PersonAdded",
            "payload_content": {
                "person_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "timestamp": "2023-01-01T12:00:00",
            },
        },
    },
    "PersonRenamed": {
        "summary": "A request example for a person renamed event",
        "description": "Example payload when a person is renamed.",
        "value": {
            "payload_type": "PersonRenamed",
            "payload_content": {
                "person_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Jane Doe",
                "timestamp": "2023-01-02T12:00:00",
            },
        },
    },
    "PersonRemoved": {
        "summary": "A request example for a person removed event",
        "description": "Example payload when a person is removed.",
        "value": {
            "payload_type": "PersonRemoved",
            "payload_content": {
                "person_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-01-03T12:00:00",
            },
        },
    },
}

execute_custom_nl_query_examples = {
    "Example 1": {
        "summary": "A custom user query example",
        "description": "Example natural language to SQL query.",
        "value": {
            "natural_language_query": "Get me all the people added after January 1st, 2023."
        },
    }
}

accept_webhook_responses = {
    200: {
        "description": "Webhook processed successfully",
        "content": {
            "application/json": {
                "example": {"detail": "Webhook processed successfully"}
            }
        },
    },
    400: {
        "description": "Invalid input",
        "content": {"application/json": {"example": {"detail": "Invalid input"}}},
    },
    404: {
        "description": "Person not found",
        "content": {"application/json": {"example": {"detail": "Person not found"}}},
    },
    500: {
        "description": "Server error",
        "content": {
            "application/json": {
                "example": {"detail": "Server error: some_error_description"}
            }
        },
    },
}

get_name_responses = {
    200: {
        "description": "Name fetched successfully",
        "content": {"application/json": {"example": {"name": "John Doe"}}},
    },
    404: {
        "description": "Person not found",
        "content": {"application/json": {"example": {"detail": "Person not found"}}},
    },
    422: {
        "description": "Invalid UUID format",
        "content": {"application/json": {"example": {"detail": "Invalid UUID format"}}},
    },
    500: {
        "description": "Server error",
        "content": {"application/json": {"example": {"detail": "Server error"}}},
    },
}

execute_custom_nl_query_responses = {
    200: {
        "description": "Query executed successfully",
        "content": {
            "application/json": {
                "example": {"result": [{"column1": "value1", "column2": "value2"}]}
            }
        },
    },
    400: {
        "description": "Invalid input",
        "content": {"application/json": {"example": {"detail": "Invalid input"}}},
    },
    500: {
        "description": "Server error",
        "content": {"application/json": {"example": {"detail": "some error occurred"}}},
    },
}
