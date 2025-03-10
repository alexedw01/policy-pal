# End-to-End Testing with Cypress

This guide explains how to set up and run end-to-end tests using Cypress for your project.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Node.js](https://nodejs.org/) (version 12 or higher)
- [npm](https://www.npmjs.com/) (version 6 or higher)

## Installation

1. **Install Cypress**:

   Navigate to your project directory and install Cypress as a development dependency:

   ```sh
   npm install --save-dev cypress

2. **Running Tests**:
You can run Cypress tests in two ways:

Cypress Test Runner:

Open the Cypress Test Runner to run tests interactively:

This will open the Cypress Test Runner, where you can select and run individual test files.

Headless Mode:

Run Cypress tests in headless mode (useful for CI/CD pipelines):

This will run all tests in the cypress/e2e directory and output the results in the terminal.

3. **TO EDIT/CREATE TESTS**:

Use the Cypress Test Runner to create specs