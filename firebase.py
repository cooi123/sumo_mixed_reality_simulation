import firebase_admin
from firebase_admin import db
import json
from sklearn import linear_model
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import math
import pandas as pd
import folium
import datetime
from noiseplanet.matcher import matching
from noiseplanet.ui.foroute import plot_html
cred_obj = firebase_admin.credentials.Certificate('.\cobibikeapp-firebase-adminsdk-lgp5i-ebf92e900f.json')
default_app = firebase_admin.initialize_app(cred_obj,{
	'databaseURL':"https://cobibikeapp-default-rtdb.asia-southeast1.firebasedatabase.app"
	})

X = []
Y= []
df = None
def listener(event):
	print(event.event_type)  # can be 'put' or 'patch'
	print(event.path)  # relative to the reference, it seems
	data = event.data
	print(data)
	global df
	if 'coordinate' in data:
		# dataArr.append(data)
		# predictVelocity(data['time'],data['speed'])
		newLocation= predictNextPos(data['bearing'],data['speed'],data['coordinate'])
		tempDf= pd.DataFrame.from_dict(data, orient='index')
		pd.concat([df,tempDf])
		coordinates = df['coordinate'].map(lambda v:[v['latitude'], v['longitude']]).values
		co = np.array(list(coordinates))[-5:]
		newCoords= np.concatenate((co,np.array([newLocation])), axis =0)
		print(newCoords)
		#take only the last 5 second of data
		mapMatching(newCoords)

	else:
		df =pd.DataFrame.from_dict(data, orient='index')
		coordinates = df['coordinate'].map(lambda v: [v['latitude'], v['longitude']]).values

		co = np.array(list(coordinates))
		print(co.size)
		# mapMatching(co)
		print(df)

ref = db.reference('/bike_data').listen(listener)
linReg = linear_model.LinearRegression()
model =None
m = folium.Map(location=[50.119080642289674, 8.638764347587754], zoom_start=15)
m.save("index.html")
def mapMatching(track):
	graph = matching.model.graph_from_track(track)
	track_coor, route_corr, edgeid, stats = matching.match(graph, track, method='hmm')
	print(track_coor, stats)
	folium.PolyLine(track_coor).add_to(m)
	m.save("index.html")
	# plot_html(track, track_corr=track_coor, route_corr=route_corr,
	# 		  proj=True, show_graph=True)
def predictNextPos(heading:int, speed, coordinate):
	#time to break
	time = 5
	r= 6378137.0
	lat = coordinate['latitude']
	lon = coordinate['longitude']
	x = speed * math.sin(heading * math.pi / 180) * time / 3600;
	y = speed * math.cos(heading * math.pi / 180) * time / 3600;
	newLat = lat + 180 / math.pi * y / r;
	newLon = lon + 180 / math.pi / math.sin(lat * math.pi / 180) * x / r;
	print(f'new pos{newLat,newLon}')
	return  [newLat,newLon]

def predictVelocity(x,y):
	global model
	X.append(x)
	Y.append(y)
	npX = np.array(X).reshape((-1,1))
	npY= np.array(Y)
	print(X,Y)
	print(x,y)
	model = linReg.fit(npX, npY)

	print(model.coef_, model.intercept_)
	r_sq = model.score(npX, npY)
	print(r_sq)

# def draw_graph(i):
# 	plt.cla()
# 	plt.scatter(X,Y)
#
# 	if model is not None:
# 		npX = np.array(X).reshape((-1, 1))
# 		plt.plot(X, model.predict(npX), color='k')
# anima = animation.FuncAnimation(plt.gcf(),draw_graph)
# plt.scatter(X,Y)
# plt.plot(X,Y)
# plt.show()
# def getValueFromDatabase(event=None):
# 	values = ref.order_by_key().limit_to_last(1).get()
# 	for key, value in values.items():
# 		print(type(value))
# 		print(value)
#
# 		res = json.loads(value)
# 		print(res)
# # getValueFromDatabase()
# def insertDataToDatabase(data,path:str):
# 	jsonData = json.dumps(data)
# 	ref = db.reference(path)
# 	ref.push(jsonData)

# insertDataToDatabase({"2":"test"}, "/")




# print(predictNextPos(181.752, 5, 50.11818, 8.63044))
#
# x = [0,1,2,3,4,5,6]
# X = np.array(x).reshape((-1,1))
# y=[0,1,2,3,4,5,6]
#
#
# reg = linear_model.LinearRegression().fit(X,y)
# r_sq = reg.score(X,y)
# print(r_sq)
# plt.plot(X,reg.predict(X), color='k')
# plt.show()