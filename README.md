# Wholesale company


## Overview
---

This a sample project created using django and DRF this project has some API which are indented to make the workflow of an wholesale company as simple as possible.


## Requirements
---
1. Python (3.6, 3.7, 3.8, 3.9)
2. Django (2.2, 3.0, 3.1)
3. Django REST Framework (3.12)


## Get started
---

Step 1: Install requirements

`pip install -r requirements.txt`

Step 2: Make migration for the models

`python manage.py makemigrations`

Step 3: Run migration on the database

`python manage.py migrate`

Step 4: Run server

`python manage.py runserver`

Step 5: Goto the link http://localhost:8000/api/ to see the API root

## Features
---

### 1. To get the list of products and its available stocks.
---
Goto http://localhost:8000/product/ we will get something like

```json
{
    "count": 64,
    "next": "http://localhost:8000/api/product/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "url": "http://localhost:8000/api/product/1000/",
            "name": "0 Product 0",
            "price": 9771,
            "quantity": 24966
        },
        {
            "url": "http://localhost:8000/api/product/1001/",
            "name": "1 Product 1",
            "price": 8301,
            "quantity": 24884
        },
        .................
```

### 2. To refill the godown stocks
---
Send a post request to the respective product to update the stock count.

```bash
curl --location --request POST 'http://localhost:8000/api/product/<product id>/refill/' \
--data-raw '{
    "refill_count": <refill count>
}'
```

### 3. To update available stocks in the godown
---
**You can do this two different ways**

#### _A. Upload the csv file and update the purchases_

You can refer that method in following postman GUI

[Click here](https://documenter.getpostman.com/view/2969258/TWDTMyu9#0ff30a18-3da9-4a57-96fa-85236e05a2d6)

#### _B. Read the uploaded file from the media (SSH files to media folder)_

1. By going to the link http://localhost:8000/api/purchase/existing_files/ you could see the list of file which are already there in the media folder with the created date.

2. On sending a post request to the URL http://localhost:8000/api/purchase/existing_files/ the latest file from the media folder will be taken and data will be saved.

```bash
curl --location --request POST 'http://localhost:8000/api/purchase/existing_files/'
```

The saving of the data will be done with the following actions: 
- The products which are not already there in the database but it is present in the csv file will be added as a new product
- The newly created products will have a defualt stocks of 25000.
- The Purchases with the same Id will be updated with the latest data.
- The Purchases which are not present will be added as new purchases.

### 4. Add new product
---

You can add new products by sending a post request to the API http://localhost:8000/api/product/

Example: 

```bash
curl --location --request POST 'http://localhost:8000/api/product/' \
--data-raw '{
    "id": 1,
    "name": "A product",
    "price": 100,
    "quantity": 100
}'
```


> NOTE: If a purchase is updated or deleted the stocks count will be update accordingly. Example: if the initial stock count is 10 and had a purchase of 1 qty, if the qty 1 purchase is delete the overall qty of the product will be increased by 1 that is 11.

> NOTE: A validation to check if the pruchase stocks does not make the overall product stock negavite is not yet done.