# Company finder
## Features
Leverage open data api to look up company data from [Patentti- ja rekisterihallitus](http://avoindata.prh.fi/ytj.html#/)

App uses:
  - Django backend
  - Vagrant
  - Ansible provisioning
  - several python packages found in requirements.txt

## Running the application

Run in root folder:
`vagrant up`

App will be available in localhost port 8080

Look up data using query parameter `?date=yyyy-mm-dd`

example:
`http://localhost:8080/company/?date=2012-12-12`

Result is a list of entries like so:
```json
{
  "businessId": "string",
  "registrationDate": "2020-04-15T18:01:16.376Z",
  "companyForm": "string",
  "detailsUri": "string",
  "name": "string"
}
```
