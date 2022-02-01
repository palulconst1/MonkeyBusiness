from http.client import HTTPException
from urllib import response
from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel
import threading
from time import sleep
import numpy as np
from fastapi_mqtt import FastMQTT, MQQTConfig
import json

f = open('./data.json', "r")
data = json.load(f)
f.close()

stop_threads = False

# sensors
is_day = False
is_nearby = False

# lamp state
last_intensity = data["last_intensity"]
intensity = data["intensity"]
RGB = data["RGB"]
reading_mode = data["reading_mode"]
wave = data["wave"]
off = data["off"]


class LampStatus(BaseModel):
    last_intensity: int
    intensity: int
    RGB: List[int] = [0, 0, 0]
    reading_mode: bool
    wave: bool

class Message(BaseModel):
    message: str

class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }



app = FastAPI()


# mqtt
mqtt_config = MQQTConfig(username="test", password="test")

mqtt = FastMQTT(
    config=mqtt_config
)

mqtt.init_app(app)

def simulate_sensors(): 
    global mqtt
    global is_day
    global is_nearby
    sleep(10)

    while True:

        global stop_threads
        if stop_threads:
            break

        is_day = np.random.poisson(1, 1)[0] <= 2
        is_nearby = np.random.uniform(0, 1, 1)[0] <= 0.5

        sleep(10)

def simulate_lamp():
    global mqtt
    global is_day, is_nearby, intensity, RGB, reading_mode, wave, last_intensity
    global off
    sleep(10)

    mqtt.subscribe(["lampcomm"])

    while True:
        global stop_threads
        if stop_threads:
            break

        if not off:
            if (not reading_mode):
                if (is_day and not is_nearby):
                    mqtt.publish("lamp", "lamp automatically turned off")
                    if intensity > 0:
                        last_intensity = intensity
                    intensity = 0
                
                if (not is_day and is_nearby):
                    mqtt.publish("lamp automatically turned on")
                    intensity = last_intensity

            if (wave):
                RGB = [np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)]

            mqtt.publish("lamp", f"Lamp intensity-{intensity} R-{RGB[0]} G-{RGB[1]} B-{RGB[2]} reading_mode-{reading_mode} wave-{wave} last_intensity-{last_intensity} is_day-{is_day} is_nearby-{is_nearby}")

        sleep(10)

sensor_thread = threading.Thread(target=simulate_sensors)
sensor_thread.start()

lamp_thread = threading.Thread(target=simulate_lamp)
lamp_thread.start()

# mqtt routes
@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("lampcontrol")
    print("Connected: ", client, flags, rc, properties)

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ",topic, payload.decode(), qos, properties)

    if topic == "lampcontrol":
        payload = payload.decode("utf-8")

        if payload == "toggle":
            await lamp_toggle()
        elif payload == "reading_mode":
            await lamp_reading_mode()
        elif payload == "wave":
            await lamp_wave()
        elif payload == "off":
            await lamp_off()
        elif payload.split()[0] == "RGB":
            msg = payload.split()
            await lamp_rgb(int(msg[1]), int(msg[2]), int(msg[3]))
        elif payload.split()[0] == "intensity":
            msg = payload.split()

            await lamp_intensity(int(msg[1]))

    return 0

@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)



@app.get("/", response_model=Message)
async def root():
    return {"message": "Hello world!"}

@app.get("/status", response_model=LampStatus)
async def lamp_status():
    return {
        "last_intensity": last_intensity,
        "intensity": intensity,
        "RGB": RGB,
        "reading_mode": reading_mode,
        "wave": wave
    }

@app.post("/lamp/toggle", response_model=Message)
async def lamp_toggle():
    global last_intensity, intensity

    toggledOn = False

    if intensity == 0:
        intensity = last_intensity if last_intensity > 0 else 255
        toggledOn = True
    else:
        last_intensity = intensity if intensity > 0 else 255
        intensity = 0

    mqtt.publish("lamp", f"Lamp toggled {'on' if toggledOn else 'off'}")

    return {
        "message": f"Lamp toggled {'on' if toggledOn else 'off'}"
    }

@app.post("/lamp/rgb", response_model=Message, responses={500: {"model": HTTPError}})
async def lamp_rgb(r: int, g: int, b: int):
    if (r < 0 or r > 255):
        raise HTTPException(status_code=500, detail="Red must be between 0 and 255")
    
    if (g < 0 or g > 255):
        raise HTTPException(status_code=500, detail="Green must be between 0 and 255")

    if (b < 0 or b > 255):
        raise HTTPException(status_code=500, detail="Blue must be between 0 and 255")

    global RGB

    RGB = [r, g, b]

    mqtt.publish("lamp", f"Lamp color succesfully updated {r} {g} {b}")

    return {
        "message": "Lamp color succesfully updated"
    }

@app.post("/lamp/reading_mode", response_model=Message)
async def lamp_reading_mode():
    global reading_mode, intensity

    reading_mode = not reading_mode
    intensity = 20

    mqtt.publish("lamp",  f"Lamp reading mode turned {'on' if reading_mode else 'off'}")

    return {
        "message": f"Lamp reading mode turned {'on' if reading_mode else 'off'}"
    }

@app.post("/lamp/wave", response_model=Message)
async def lamp_wave():
    global wave

    wave = not wave

    mqtt.publish("lamp",  f"Lamp wave color shuffle turned {'on' if wave else 'off'}")

    return {
        "message": f"Lamp wave color shuffle turned {'on' if wave else 'off'}"
    }

@app.post("/lamp/intensity", response_model=Message, responses={500: {"model": HTTPError}})
async def lamp_intensity(new_intensity: int):
    if new_intensity < 0 or new_intensity > 100:
        raise HTTPError(status_code=500, detail="Intensity must be between 0 and 100 inclusive")

    global intensity, last_intensity
    intensity = new_intensity
    last_intensity = new_intensity

    mqtt.publish("lamp",  f"Lamp intensity sucesfully updated {intensity}")

    return {
        "message": "Lamp intensity sucesfully updated"
    }

@app.post("/lamp/off", response_model=Message)
async def lamp_off():
    global intensity, last_intensity, off

    last_intensity = intensity
    intensity = 0
    off = True

    mqtt.publish("lamp",  "Lamp turned off")

    return {
        "message": "Lamp turned off"
    }

@app.post("/lamp/on", response_model=Message)
async def lamp_off():
    global intensity, last_intensity, off

    last_intensity = intensity
    intensity = 0
    on = True

    mqtt.publish("lamp",  "Lamp turned on")

    return {
        "message": "Lamp turned on"
    }

@app.on_event("shutdown")
def shutdown_event():
    global stop_threads
    stop_threads = True

    sensor_thread.join()
    lamp_thread.join()

    f = open("./data.json", "w")
    json.dump({
        "last_intensity" : last_intensity,
        "intensity": intensity,
        "RGB": RGB,
        "reading_mode": reading_mode,
        "wave": wave,
        "off": off
    }, f)
    f.close()