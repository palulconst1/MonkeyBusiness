# Smart Lamp

## Introduction
Smart Lamp is a smart IOT device that can be 
programmed using HTTP/MQTT protocols. Functionalities include:
* Setting RGB lights to shuffle
* Automatic turn on/off depending on proximity
and light sensors
* Remote turning on/off
* Reading mode
* Remote intensity of light

## Documentation
AsyncAPI and OpenAPI specification files are provided. To access swagger documentation, please
start the application, and navigate to ```/docs```.

## Prerequisites
* Python3
* Pip
* MQTT broker, preferably a local one

## Used libraries
* FastAPI
* pydantic
* numpy
* fastapi_mqtt

## Installation
All of the required packages are provided in ```requirements.txt```. You can install those using:

```bash
pip install -r requirements.txt
```

For MQTT installation please refer to the steps specific to your operating system.

## Running the application
First of all, create an MQTT user:password pair, using the following credentials: ```test:test```.

The application can be ran using uvicorn.

```bash
uvicorn app:app --reload
```

## Runing tests
Tests can be ran after starting the application, using the following command:

```bash
python tests.py
```

If no errors are present, then the tests ran succesfully.

## Usage
Please refer to the Swagger documentation page.

