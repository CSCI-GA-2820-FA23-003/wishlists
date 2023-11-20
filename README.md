# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-FA23-003/wishlists/actions/workflows/tdd-tests.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-003/wishlists/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA23-003/wishlists/graph/badge.svg?token=)](https://codecov.io/gh/CSCI-GA-2820-FA23-003/wishlists)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```
## Running the App

After opening vscode in our running container.  Execute the following command in the terminal.

```flask run```

## Running tests

To run all tests in the project, use the following at the command line.

```green```

### Wishlist Endpoints
​
1. **Create Wishlist**
   - **Endpoint**: `POST /wishlists`
   - **Description**: Create a new wishlist for a customer.
   - **Request JSON**:
     ```json
     {
         "customer_id": 1,
         "wishlist_name": "My Wishlist",
         "created_date": "2023-10-12"
     }
     ```
   - **Response**:
     - **Status Code**:
       - 201 (Created) - Successfully created a new wishlist.
     - **Header**: Return a header for the wishlist created. 
       - Location: `/wishlists/<wishlist_id>`
     - **Body**: Return the newly created wishlist with its ID.
​
2. **Get Wishlist**
   - **Endpoint**: `GET /wishlists?id=<wishlist_id>`
   - **Description**: Retrieve information about a specific wishlist.
   - **Response**:
     - **Status Codes**:
       - 200 (OK) - Successfully retrieved the wishlist.
       - 404 (Not Found) - Wishlist not found.
​
3. **Delete Wishlist**
   - **Endpoint**: `DELETE /wishlists/<wishlist_id>`
   - **Description**: Delete a specific wishlist.
   - **Response**:
     - **Status Codes**:
       - 204 (No Content) - Successfully deleted the wishlist.
       - 404 (Not Found) - Wishlist not found.
​
4. **List Wishlists**
   - **Endpoint**: `GET /wishlists`
   - **Description**: Retrieve meta information about a list of all wishlists.
   - **Response**:
     - **Status Code**:
       - 200 (OK) - Successfully retrieved the list of wishlists.
​
### Item Endpoints
​
1. **Create Item**
   - **Endpoint**: `POST /wishlists/<wishlist_id>/items`
   - **Description**: Add an item to a specific wishlist.
   - **Request JSON**:
     ```json
     {
         "id": 1,
         "wishlist_id": 2,
         "product_id": 3,
         "product_name": "DevOps for Dummies",
         "product_price": 29.99,
         "quantity": 2,
         "created_date": "2023-10-12"
     }
     ```
   - **Response**:
     - **Status Code**:
       - 201 (Created) - Successfully created a new item in the wishlist.
     - **Header**: Return a header for the wishlist item created.
       - Location: `/wishlists/<wishlist_id>/items/<item_id>`
     - **Body**: Return the newly created item with its ID.
​
1. **Get Item**
   - **Endpoint**: `GET /wishlists/<wishlist_id>/items?id=<item_id>`
   - **Description**: Retrieve information about a specific item within a wishlist.
   - **Response**:
     - **Status Codes**:
       - 200 (OK) - Successfully retrieved the item.
       - 404 (Not Found) - Item not found.
​
1. **Update Item**
   - **Endpoint**: `PUT /wishlists/<wishlist_id>/items/<item_id>`
   - **Description**: Update the details of an existing item within a wishlist.
   - **Request JSON**:
     ```json
     {
         "quantity": 3
     }
     ```
   - **Response**:
     - **Status Codes**:
       - 200 (OK) - Successfully updated the item.
       - 404 (Not Found) - Item not found.
​
1. **Delete Item**
   - **Endpoint**: `DELETE /wishlists/<wishlist_id>/items/<item_id>`
   - **Description**: Delete a specific item from a wishlist.
   - **Response**:
     - **Status Codes**:
       - 204 (No Content) - Successfully deleted the item.
       - 404 (Not Found) - Item not found.
​
1. **List Items in Wishlist**
   - **Endpoint**: `GET /wishlists/<wishlist_id>/items`
   - **Description**: Retrieve a list of all items within a specific wishlist.
   - **Response**:
     - **Status Code**:
       - 200 (OK) - Successfully retrieved the list of items in the wishlist.

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
