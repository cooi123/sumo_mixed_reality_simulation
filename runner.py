import traci
import firebase_admin
from firebase_admin import db
import math
import time
cred_obj = firebase_admin.credentials.Certificate('.\cobibikeapp-firebase-adminsdk-lgp5i-ebf92e900f.json')
default_app = firebase_admin.initialize_app(cred_obj,{
	'databaseURL':"https://cobibikeapp-default-rtdb.asia-southeast1.firebasedatabase.app"
	})


sumoCmd = ["sumo-gui", "-c", "monash.sumocfg"]
traci.start(sumoCmd)

def predictNextPos(angle, x,y, speed):
    print(angle)
    time =5
    newX = speed * math.sin(angle * math.pi / 180) * time + x
    newY = speed * math.cos(angle * math.pi / 180)*time + y
    return newX,newY
while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep();
    count=0
    for id in traci.vehicle.getIDList():

        x, y = traci.vehicle.getPosition(id)
        lon, lat = traci.simulation.convertGeo(x, y)
        angle = traci.vehicle.getAngle(id)
        speed = traci.vehicle.getSpeed(id)
        newX, newY= predictNextPos(angle,x,y,speed)
        newLon, newLat= traci.simulation.convertGeo(newX, newY)
        writeRef = db.reference('/bikeMovement/'+str(count))
        count+=1
        # print({'currentPos':{'latitude': lat,'longitude':lon},'time':time.time(),'futurePos':{'latitude': newLat,'longitude':newLon}})

        writeRef.set({'currentPos':{'latitude': lat,'longitude':lon},'time':round(time.time()*1000),'futurePos':{'latitude': newLat,'longitude':newLon}, 'bearing':angle})
    # print(count)

traci.close()








