import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


mqtt_client = mqtt.Client(client_id="user-8e8edeeff6fb4e30bad6eb188939442b")
mqtt_client.on_connect = on_connect
mqtt_client.username_pw_set("admin", "abc")
