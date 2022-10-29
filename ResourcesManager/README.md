# VPilot - Resources Manager

## Description and Scope
The Resources Manager Service stores and manages all information related to the resources that will be used by VPilot to validate and certify a NetApp. Among these resources, you’ll find information regarding the Testbeds and all their local resources, such as (i) the CI/CD Agent, (ii) the Local Test Repository (LTR), (iii) the LTR Monitoring Service, (iv) the Infrastructure Monitoring Service, etc. Considering the CI/CD Agents, for instance, the Resources Manager will store their location, credentials, and a plethora of additional information, if needed.


## REST API Standardization

The API of this Service is standardized with the TM632 - Party Management REST API specification. More information on this TMF standard can be found [here](https://www.tmforum.org/resources/standard/tmf632-party-management-api-rest-specification-r19-0-0/), and its OpenAPI 3 specification is available [here](https://tmf-open-api-table-documents.s3.eu-west-1.amazonaws.com/OpenApiTable/4.0.0/swagger/TMF632-Party-v4.0.0.swagger.json) .

This standard was further extended to allow authentication and authorization operations, such as enforcing RBAC on the TMF632 base endpoints. Through this extension, it is now possible to manage the users that can get information on a specific organization, update and delete it. To this end, the following endpoints are provided:

![TMF632 Standard Extension](Docs/img/TMF632ExpansionNewEndpoints.png "TMF632 Standard Extension")


## REST API Authentication and Authorization Mechanisms

Currently, the Resources Manager Service doesn’t store any information regarding the system’s users, rather then its id. To this end, an external Identity Provider was used. The chosen IDP was Keycloak, and its thorough integration with the Resources Manager Service was achieved. 
 
To interact with the Resources Manager, a user must first get an access token from Keycloak (OpenID Connect specification). Then, the user should add this token to the Authorization Header of all requests to the Resources Manager.
