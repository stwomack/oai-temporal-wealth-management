# React Web App for Wealth Management

An easy to use web based front end for the Wealth Management Agent. 
It uses the [API](../api/README.md) to interact with Temporal.

## Prerequisites 

[Node.js](https://nodejs.org/en/download): Version 14.0.0 or higher.

The web application relies on the API to communicate with Temporal. 
Be sure to follow the instructions to run the API, which can be found [here](../api/README.md)

Note that the web application communicates directly with the API and the API is what 
communicates with Temporal running locally or in the cloud.

## Running the Web App
```bash
cd src/frontend
npm start
```

## Example

Here's an example screenshot of the web application running:

![](../../images/webui.png)

## Comments

This example uses a fixed Workflow ID to simplify some of the functionality for a demo.
