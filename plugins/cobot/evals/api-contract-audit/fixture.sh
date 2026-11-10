#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A hand-written OpenAPI 3.1 document with
# five defects: an API key in the query string, default-only error responses, the 3.0 keyword
# nullable, an unbounded array and an operation without operationId.
set -euo pipefail
mkdir -p api
cat > api/openapi.yaml <<'YAML'
openapi: 3.1.0
info:
  title: Notes API
  version: 1.0.0
security:
  - apiKeyQuery: []
paths:
  /notes:
    get:
      operationId: listNotes
      summary: List notes
      responses:
        "200":
          description: The notes
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Note"
        default:
          description: Error
    post:
      summary: Create a note
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Note"
      responses:
        "201":
          description: Created
        default:
          description: Error
components:
  securitySchemes:
    apiKeyQuery:
      type: apiKey
      in: query
      name: token
  schemas:
    Note:
      type: object
      properties:
        id:
          type: string
        body:
          type: string
          nullable: true
YAML
