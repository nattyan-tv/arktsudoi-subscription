import sanic
import json


config = json.load(open("config.json", "r"))

ENVIRONMENT = "test"
if config["PRODUCTION"]:
    ENVIRONMENT = "production"

app = sanic.Sanic(f"dinosaur-stripeconnect-{ENVIRONMENT}")

@app.post("/webhook")
async def webhook(request):
    print(request.json)
    return sanic.response.json({"status": "ok"})

if __name__ == "__main__":
    print("dinosaur-stripeconnect")
    if config["PRODUCTION"]:
        print("########## ATTENTION! ##########")
        print("YOU ARE RUNNING IN PRODUCTION MODE!")
        print("If you want to run in test mode, set 'PRODUCTION' to false in config.json")
    print("Starting server on port: ", config["SERVER_PORT"])
    app.run("0.0.0.0", config["SERVER_PORT"])
