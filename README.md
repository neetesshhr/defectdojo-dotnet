| TOC                                                       |
|-----------------------------------------------------------|
| [Service Title](#Service-Title)                           |
| [Description](#Description)                               |
| [Service Status](#Service-Status)                         |
| [Intended Service Use Cases](#Intended-Service-Use-Cases) |
| [Pricing](#Pricing)                                       |
| [Assessments](#Assessments)                               |
| [Approvals](#Approvals)                                   |
| [Engineering Considerations](#Engineering-Considerations) |
| [Risks](#Risks)                                           |
| [Risk Acceptance](#Risk-Acceptance)                       |
| [Contributors](#Contributors)                             |


# Service Title 
[AWS Connect](https://docs.aws.amazon.com/connect/)

## Description 
AWS Connect is an AI powered contact center service that's Omnichannel and can provide voice, chat, and task related customer services. There are 4 main types of [personas](https://docs.aws.amazon.com/connect/latest/adminguide/security-bp.html#iam-bp) based on activities they perform with connect. Also, see below for how they map to Fifth Third personas.

| Personnel Roles                                          | 5/3 Cloud Engineering | 5/3 App Team (LOB) | 5/3 Contact Center (LOB) |
|----------------------------------------------------------|-----------------------|--------------------|--------------------------|
| 1. AWS administrator / Connect Platform Owner            |                       | :white_check_mark: |                          |
| 2. Amazon Connect administrator / Connect Platform Owner |                       |                    | :white_check_mark:       |
| 3. Amazon Connect agent                                  |                       |                    | :white_check_mark:       |
| 4. Amazon Connect Service contact (customer)             |                       |                    |                          |
| 5. AWS Platform Owner                                    | :white_check_mark:    |                    |                          |

![amazonconnectpersonas](https://github.info53.com/storage/user/1676/files/fdc1f351-d90d-432c-bc0d-8278febefc58)

It's also not uncommon for companies to have a personnel using connect like this:
- Infrastructure teams (normally just go into connect via aws console, others will use the connect url to login)
- Call center admins
- Supervisors
- Agents
- Customers

### Amazon Connect's Layers
Connect workloads can be separated into these [layers](https://docs.aws.amazon.com/connect/latest/adminguide/workload-layers.html):
1. Telephony (Controls endpoint customer can call into)
2. Amazon Connect interface/API
   - Anything agents, managers, supervisors, or contacts use to access, configure, or manage Amazon Connect components from a web browser or API is considered the Amazon Connect interface layer
     - SSO
     - Custom desktop applications created using the Amazon Connect Streams API or Customer Relationship Management (CRM) integrations
     - Amazon Connect contact-facing chat interface
     - Chat web server hosting Connect Chat API
     - Any API Gateways (APIGW) and Lambdas that are needed to route chat contacts to connect
3. Flows/IVR
   - The Flow/IVR layer is the primary architectural vehicle for Amazon Connect and serves as the point of entry and first line of communication with customers reaching out to your contact center
4. Agent workstation
   - Not managed by AWS
   - Consists of any physical equipment and third-party technologies, services, and endpoints that facilitate the agent’s voice, data, and access the Amazon Connect interface layer
5. Metric and reporting
   - Has components used for delivering, consuming, monitoring, alerting, or processing real-time and historical metrics for your agents, contacts, and contact center
   - Includes all native and 3rd party components

### Amazon Connects Feature Overview
**Customers**
- High quality voice
- Conversational IVR and chatbots
- Chat, SMS, and messaging
- In-app, web, and video calling
- Outbound campaigns
- Voice authentication (uses Voice ID, if enabled/setup)
- Task management

**Agents**
- Agent workspace (integrates agent facing capabilities and features into one page)
- Step-by-step guides (these can be created for agents to use via a no-code editor)
- Generative AI-powered agent assist (Uses Amazon Q)
- Generative AI-powered post-contact summaries
- Unified customer view (can use Connect Customer Profiles to combine info from other external apps with contact history provided by Connect)
- Case management (uses Amazon Connect Cases, if enabled, to manage customer issues if they require follow-ups, multiple interactions, etc.)
- Efficient contact routing (uses Connect's routing profiles, to route customer to the needed agents accordingly)

**Supervisor**
- Real-time and historical reports and dashboards
  - Uses Connects analytics data lake
  - Data includes contact records, Contact Lens conversational analytics, Contact Lens performance evaluations, and [more](https://docs.aws.amazon.com/connect/latest/adminguide/connect-feature-overview.html#connect-intro-reporting)
- Real-time conversational analytics
- Quality and performance management (Includes GenAI powered recommendations, ability to view agent actions when handling contacts via screen recordings, etc.)
- Forecasting, capacity planning, and scheduling

**Administrators**
- Telephony management ([source](https://docs.aws.amazon.com/connect/latest/adminguide/connect-feature-overview.html#connect-intro-telephony))
  - The telephony service allows you to claim and then use direct inward dial (DID) and toll-free phone numbers for more than 110 countries worldwide
  - There are also more than 200 available outbound calling destinations
- Drag-and-drop workflow designer (e.g. used for IVR and chatbot workflows)
  - Flows have native integration with AWS lambda


## Service Status

Being Reviewed

## Intended Service Use Cases
Connect is a Contact Center as a Service Platform. Connect will be used for specific LOB's that require Contact Center communication services (telephony, chat, etc) between 5/3rd and public. Initial use case request from Enterprise Modernization is scoped to chat, customer profiles, along with the forecasting, capacity planning, and scheduling features. No telephony initially, but they do have plans to eventually replace the current genisys IVR system with telephony.

SNOW Request - [RITM0240694](https://fifththird.service-now.com/now/nav/ui/classic/params/target/sc_req_item.do%3Fsys_id%3Dc23959634773ce146dd357ce536d43e0%26sysparm_stack%3D%26sysparm_view%3D)

[Arhitecture diagrams](https://github.info53.com/pages/fitb-enterprise-software/draw-io-renderer/?diagram=https://github.info53.com/pages/Eric-Rolf/workspace/Draw.io/AWS-Connect.drawio) provided for the use case in the SNOW request

## Pricing 
Connect does have a free tier, see more at [pricing](https://aws.amazon.com/connect/pricing/)

There are a number of different features and other parts of the service that can drive cost up and price varies based on region, some examples include:
- Phone Numbers
- Inbound & Outbound Calling
- Shared Trunking

### Notable pricing
Messaging & Chat:
- Chat usage – per message $0.004
- SMS usage - per message	$0.01
- Apple Messages for Business – per message	$0.01
- Chat experiences using step-by-step guides - per message	$0.005

Customer Profiles:
- Profiles using identity resolution or third-party data	$0.0025
- Profiles without identity resolution using only Amazon Connect data*	Free (*There is no charge for profiles that only contain data generated by usage of Amazon Connect.)
- Additional incremental charge for profiles storing over 100 objects	$0.0025

Contact Lens:
- Amazon Connect Contact Lens offers separate pay-as-you-go pricing for the following capabilities: conversational analytics, performance evaluation, and screen recording. [See here for details](https://aws.amazon.com/connect/pricing/)

Forecasting & Scheduling:
- Billed $27 per agent/per month for agents who either 1/ take a contact in a forecasted queue or 2/ receive a schedule. (But there is a 90 day free trial)

# Assessments
## Engineering Feasibility Assessment
### Availability
> **NOTE** At the time of this writing, Connect is not compatible with core rated applications/services. Connect is only offered in one of the 5/3rd sanctioned regions: us-east-1. No dates have been announced for us-east-2

- Connect features are only available in certain regions, each feature does have support in us-east-1. See this [list](https://docs.aws.amazon.com/connect/latest/adminguide/regions.html) for more info. Solutions using Connect should not expect the service to have multi-region DR ability.
- There are various service quota limits for the different features in Connect
  - [This page](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-service-limits.html) defines whether they are adjustable, what their adjustability is (resource, account level, or NA)
  - There are also [API quota throttling limits](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-service-limits.html#api-throttling-quotas) that are by account, and per region, not by user and not by instance
- Connect uses the AWS Global Infrastructure and has [resilience](https://docs.aws.amazon.com/connect/latest/adminguide/disaster-recovery-resiliency.html), when a Connect instance is created within a aws region it's done so with a minimum of 3 AZs in which the instance is propagated across in a active-active-active configuration
  - In the case of a failure in 1 AZ, that node is taken out of the rotation and there should be no impact on production
- See [Single-region telephony and softphone architecture](https://docs.aws.amazon.com/connect/latest/adminguide/disaster-recovery-resiliency.html#telephony-recovery-resiliency)
  - Connect is integrated with multiple telephony providers with dedicated network paths that are redundant to 3+ AZs in each aws region
  - Inbound (US toll-free) and outbound calls in Connect get processed by multiple telecom carriers, each connected to multiple AZs in active-active configurations 
  -  AWS manages the network connectivity to their carriers [see more](https://docs.aws.amazon.com/connect/latest/adminguide/concepts-telephony.html)
  - [Phone Call Media](https://docs.aws.amazon.com/connect/latest/adminguide/data-handled-by-connect.html#phone-call-media-handling)
    - PSTN calls are connected between Amazon Connect and various telecommunications carriers using either private circuits maintained between Amazon Connect and our providers or existing AWS internet connectivity. For PSTN calls routed over the public internet, signaling is encrypted with TLS and the audio media is encrypted with SRTP
    - Softphone calls are established to the agent’s browser with an encrypted WebSocket connection using TLS. The audio media traffic to the browser is encrypted in transit using DTLS-SRTP
- If [global levels of resilience](https://docs.aws.amazon.com/connect/latest/adminguide/setup-connect-global-resiliency.html) is needed, Connect can provide that assuming you have another supported region that can be paired with

### Scalability  
- AWS Connect does have scalability and you only pay for what you use. AWS states, "Capacity, platform resiliency, and scaling are handled as part of the managed service, allowing you to efficiently ramp from 10 to 10,000+ agents without worrying about the management or configuration of underlying platform and telephony infrastructure." [source](https://docs.aws.amazon.com/connect/latest/adminguide/workload-layers.html)
- Connects telephony-as-a service model can also scale up and down

### Durability  
- Data in the contact records are the basis for most real-time and historical metrics in Connect. This data is oftentimes used to create the metric reports. [See this page](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-metrics.html) for more info
  - Contact records are available for 24 months after the associate contact was initiated. Note, you could also stream these contact records to Kinesis to retain them longer
- Some data in Connect is stored in S3 buckets, which contain S3 levels of durability

### IAM policy requirements  
- IAM roles should be used for access to Connect through the console (note, this defers from access to the Connect instance itself)
  - IAM Users should only be granted for applications that require a static user. This will have to follow the normal exception process
- A least-permissive access model should be followed by all teams leveraging these services
- A listing of actions, resources, and condition keys related to AWS Connect, [reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnect.html)

### SCP requirements  
- Known list of actions to add to the allow list for accounts
  - `connect:*`
  - `profile:*`
- Known list of actions to deny:
  - `connect:AdminGetEmergencyAccessToken` (with a `SourceIp` restriction, [see](https://docs.aws.amazon.com/connect/latest/adminguide/authentication-profiles.html#configure-ip-based-ac), to cover a gap in the authentication profiles feature)
- The below are NOT being approved in this evaluation. They can be thought of as other child services of the main connect service. The assumption is enabling any of these features would require their own service evaluation per feature
  - `cases:*`
  - `voiceid:*`
- Restricted OUs will be created specifically for AWS Connect. So, only accounts that are approved to use Connect will get placed in these OUs and have the Connect related SCP permissions applied to them

### Guardrails  
> **Assumption** Appteams will be responsible for designating Connect Admin(s) personnel who will control and setup the security profiles of their agents and other personnel using the Connect instance. With access setting following a least permissive model based on their use case and personnel needs

- A [Data Opt Out policy](https://docs.aws.amazon.com/connect/latest/adminguide/data-opt-out.html) will be enabled at the Org level by default
  - This Opts Fifth Third out from having content stored or used for training and/or improving AI services in AWS
- 3rd part app integrations into AWS Connect (e.g. WhatApp or Facebook Messenger for message channels) will be denied
  - This is already denied in the SCPs, as `app-integrations` are not added to any existing whitelist. So, no SCP changes for this would be needed
- Connect's authentication profiles will have controls around them to control IP access ranges [ref](https://docs.aws.amazon.com/connect/latest/adminguide/authentication-profiles.html)
  - IP address restrictions require agents to sign in only from your VPN, or block access from specific countries or subnets.
  - Session timeouts require agents to log in to Amazon Connect again.
  - This control will be enforced with Sentinel policies, AWS Config Rules, and SCPs (for AdminGetEmergencyAccessToken scenarios that aren't covered by the authentication profiles)
    - A `local-exec` terraform block can be used by teams to run the CLI commands to configure the IP access range restrictions, and the sentinel policies can check this to ensure compliance 
    - **IP access ranges**: The defined range for 5/3rd zscaler pzen are below (*see call out note below):
      - 216.82.182.50-60
      - 216.131.56.50-60
- SAML will be the only allowed value for Connect's identity_management_type (enforced with sentinel and config rules)
- Lambda functions will be required to have a VPC configuration (enforced with sentinel and config rules, or with just with SCPs. Solution will be determined based on testing.)

> **Telephony Notes** The approved service carriers to use at Fifth Third within AWS Connect will be pre-determined. Also, AWS Connect does NOT support "bring your own carrier" at this time, but there is a option to [port your number over](https://docs.aws.amazon.com/connect/latest/adminguide/about-porting.html)

> **Call Out** Adding allowed IPs will require updates to 5/3 PAC file to include connect console URL

## Security Feasibility Assessment

### Security 
> **Appteam Responsibility** Appteams will be responsible for handling and protecting the data, RBAC, and other things created or configured within the connect instance. Denoted by (*AR) throughout this section.

 - Connect has its own RBAC model. Security Profiles within Connect are used to create and define user permissions (separate from IAM)
 - Connect does have logging ability to cloudwatch and cloudtrail, [see here](https://docs.aws.amazon.com/connect/latest/adminguide/logging-and-monitoring.html)
 - Clients must support Transport Layer Security (TLS) 1.2 or later (reference, [infrastructure security](https://docs.aws.amazon.com/connect/latest/adminguide/infrastructure-security.html))
 - Lambda functions connected to Amazon Connect should be configured with a vpc
 - Connect offers Forecasting, Capacity planning, and Scheduling but these features do not support AWS PrivateLink or VPC endpoints. [source](asset/Amazon%20Service%20Approval%20Accelerator_Amazon%20Connect%20Forecasting,%20Capacity%20Planning,%20and%20Schedulin.pdf)
 - Connect Contact Lens has a control plane API that's publicly available
   - But does not have support for any vpc endpoints
   - Agent screen recording does use pre-signed s3 urls. Voice call recordings do not. Presigned urls can just be seen in chrome developer tools and is valid for 14 seconds. You do have the option to turn off agent screen recording through configuration
     - "Pre-signed S3 urls are used to facilitate playback for recording video files from customer S3 bucket on Contact
           details page of Amazon Connect web UI (also known as Connect Admin UI)." [source](asset/Amazon%20Service%20Security%20Accelerator_Amazon%20Connect%20Contact%20Lens%20Screen%20Recording.pdf)


Amazon Connect's security can be divided up into [three layers](https://docs.aws.amazon.com/connect/latest/adminguide/security-bp.html#securityvectors), as seen in this example setup via AWS.
> **Note**: **Amazon Lex** and **Amazon Q** are services often used alongside Connect, but are **NOT** part of being enabled in this evaluation. AWS uses some of these as aids to show flavors of a particular setup to help illustrate the broader picture of what the diagram is representing

![securityvectors](https://github.info53.com/storage/user/1676/files/8cc60e3c-15e9-4d43-afb4-44571345a9ad)


#### Data Protection
AWS recommends to not put confidential or sensitive info into tags or free-form text fields (e.g. Name field) as this data may be used for billing or diagnostic logs. [Reference](https://docs.aws.amazon.com/connect/latest/adminguide/data-protection.html)
> Data held within Amazon Connect is segregated by the AWS account ID and the Amazon Connect instance ID. This ensures that data can be accessed only by the authorized users of a specific Amazon Connect instance. [Source](https://docs.aws.amazon.com/connect/latest/adminguide/data-handled-by-connect.html)
- [Encryption at rest](https://docs.aws.amazon.com/connect/latest/adminguide/encryption-at-rest.html) - Contact data classified as PII, or data that represents customer content being stored by Amazon Connect, is encrypted at rest (that is, before it is put, stored, or saved to a disk) using AWS KMS encryption keys owned by AWS
- [Encryption in transit](https://docs.aws.amazon.com/connect/latest/adminguide/encryption-in-transit.html) - All data exchanged with Amazon Connect is protected in transit between the user’s web browser and Amazon Connect using industry-standard TLS encryption

For data that moves through the Connect Flow blocks created by appteams within the connect instance itself, the appteams are responsible for encrypting the data accordingly:
There are 4 data fields that must be cryptographically protected at rest beyond the underlying storage and must be cryptographically protected at the field level. FTCS-CSS-011 Those 4 data fields include the following:
- Primary Account Number (PAN) (aka Credit Card Number)
- Pin Number (CVC/CVV)
- Social Security Number (SSN)
- Customer Bank Account Number


##### Connect Contact lens
- Data processed by Contact Lens in real-time is encrypted at rest and in transit with keys owned by Contact Lens.
- Inter-Service Data Flow - this service allows data to be moved to other AWS services within the local account. [source](asset/Amazon%20Service%20Security%20Accelerator_Amazon%20Connect%20Contact%20Lens%20Screen%20Recording.pdf)
- Metadata - Screen recording service metadata includes client information/identifiers (connect instance-id, aws account-id, connect user-id, user name). [source](asset/Amazon%20Service%20Security%20Accelerator_Amazon%20Connect%20Contact%20Lens%20Screen%20Recording.pdf)
- [PII Redaction](https://docs.aws.amazon.com/connect/latest/adminguide/enable-analytics.html#enable-redaction), Within the flow block, redaction of sensitive data should be enabled to protect it from getting included in the call transcript (*AR)
  - AWS notes the redaction is ML/prediction based so it might not remove all the data you need. So, customers should review the redaction file to see if it's working okay. [source](https://docs.aws.amazon.com/connect/latest/adminguide/sensitive-data-redaction.html)

##### Publishing Reports
- Reports can be created off data Connect captures from calls. These reports can be shared and/or published out to everyone in your aws Org (*AR)
  - However, it does appear access to the reports are based on permissions that can be set within the Connect's instance itself to determine who has access to what according to their connect security profile. [source](https://docs.aws.amazon.com/connect/latest/adminguide/publish-reports.html)

##### Customer Profiles
A customer profile is a record that stores contact history combined with information about customers, such as account number, additional information, birth date, email, multiple addresses, name, and party type. [source](https://docs.aws.amazon.com/connect/latest/adminguide/customer-profiles-what-data.html)
- Profiles can be accessed from within flows
- Profiles can be integrated with other data sources, including 3rd party sources (*AR for handling sensitive data accordingly, if these integrations are setup)
- Amazon Connect does not replace or update the data in the external application. If a data source is removed, the data from the external application is no longer available in the customer profile for every voice contact
- All user data stored in Amazon Connect Customer Profiles is encrypted at rest
- Profiles can export data in real time to [kinesis](https://docs.aws.amazon.com/connect/latest/adminguide/set-up-real-time-export.html) along with [bulk exports](https://docs.aws.amazon.com/connect/latest/adminguide/set-up-bulk-export.html) to s3
  - Data is NOT encrypted by default with kinesis, but can be enabled to use SSE (Server-side encryption)

##### Forecasts, capacity plans, and schedules
- [Encryption at rest](https://docs.aws.amazon.com/connect/latest/adminguide/encryption-at-rest.html#forecasts-encryption-at-rest-)  - When you create forecasts, capacity plans, and schedules, all data are encrypted at rest using AWS owned key encryption keys stored in AWS Key Management Service.

##### Contact Metadata
The following data stored by Amazon Connect is treated as sensitive, [source](https://docs.aws.amazon.com/connect/latest/adminguide/data-handled-by-connect.html#contact-metadata):
- Origination phone number
- Outbound phone number
- External numbers dialed by agents for transfers
- External numbers transferred to by a flow
- Contact name
- Contact description
- All contact attributes
- All contact references

##### VPC Endpoints
You can establish a private connection between your VPC and a subset of endpoints in Amazon Connect by creating an interface VPC endpoint. Following are the supported endpoints: [Source](https://docs.aws.amazon.com/connect/latest/adminguide/vpc-interface-endpoints.html)
- Amazon AppIntegrations
- Customer Profiles
- Outbound campaigns
- Voice ID
- Amazon Q in Connect

> *Note:* The core Amazon Connect service does not support AWS PrivateLink or VPC endpoints.

#### Best Practices for Compliance (*AR)
- [PII](https://docs.aws.amazon.com/connect/latest/adminguide/compliance-validation-best-practices-PII.html)
- [PCI](https://docs.aws.amazon.com/connect/latest/adminguide/compliance-validation-best-practices-PCI.html)
  - Includes PCI data scrubbing in log recordings
- For [sensitive data](https://docs.aws.amazon.com/connect/latest/adminguide/operational-excellence.html) in general:
  - Use the **store customer input** block, for sensitive DTMF input from contacts, with encryption
  - Use the **set logging behavior** flow block so logging is disabled if sensitive info is referenced
  - Use the **set contact attributes** flow block Clean-up method to remove, cleanup, or obfuscate sensitive data

  
### Cloud Security Controls
    *Note: Assessment of security related controls that will be in place  
    Include any visibility CSPM provides*


# Approvals

> Cloud Engineering Approval

*Note:Cloud Engineering final approval*

> Cloud Security Approval

*Note:Cloud Security final approval*

# Engineering Considerations 
- SCPs might need adjusted overtime to allow certain Connect features (use case dependent) that aren't initially mentioned in the SNOW ticket's use case requesting Connect
  - e.g. Allowing [Amazon Q in connect](https://docs.aws.amazon.com/connect/latest/adminguide/security-iam-amazon-connect-permissions.html#wisdom-page) would require allowing some unique pre-fix iam actions that SCPs wouldn't initially allow. Similar situations for allowing "campaigns" in Connect
- Enforce all Kinesis data streams have encryption enabled. Can be done with a combination of Sentinel policies and AWS Config Rules

# Risks

# Risk Acceptance
Section to be used when high-level risks have been identified and require sign off acknowledgement.

- **Business Controls**
- **Enterprise Architecture**
- **Info Security**
- **CTO**

Section to be used when high-level risks have been identified and require sign off acknowledgement.

# Contributors

List of groups that have been contacted for input/review/concerns regarding the eval along with a short write up regarding the context of that meeting# defectdojo-dotnet
