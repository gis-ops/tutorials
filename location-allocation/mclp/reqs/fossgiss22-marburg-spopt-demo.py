#!/usr/bin/env python
# coding: utf-8

# In[151]:


import random
import json
import requests
import numpy as np
from shapely.geometry import mapping, shape, Point
import random
import folium
from routingpy import Valhalla
from spopt.locate.coverage import MCLP
import pulp

MARBURG_CITY='{"type":"Polygon","coordinates":[[[8.75949,50.80525],[8.78724,50.80525],[8.78721,50.81729],[8.75949,50.81729],[8.75949,50.80521]]]}'

def generate_random(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
    return [pnt.x, pnt.y]

poly = shape(json.loads(MARBURG_CITY))

haushalte = []
for i in range(50):
    r_coord = generate_random(poly)
    haushalte.append(r_coord)

    


# In[154]:


m = folium.Map(location=[50.81165, 8.77284], tiles="cartodbpositron", zoom_start=15)

for coord in haushalte:
    folium.CircleMarker(
        location=[coord[1], coord[0]],
        radius=5,
        fill=True,
        fill_opacity=1,
        popup=folium.Popup("Marburg Haushalt", show=False),
        color="#3186cc"
    ).add_to(m)
      
m


# In[149]:


standorte = [[8.77284, 50.81165], [8.76301, 50.80989], [8.77133, 50.81610], [8.77163, 50.80794]]

for coord in standorte:
    folium.CircleMarker(
        location=[coord[1], coord[0]],
        radius=10,
        fill=True,
        fill_opacity=1,
        popup=folium.Popup("Potentielle Currywurstbuden", show=False),
        color="red"
    ).add_to(m)

m


# In[150]:


client = Valhalla(base_url="https://valhalla1.openstreetmap.de")
valhalla_sources_to_targets = client.matrix(locations=standorte + haushalte, sources=list(range(0,4)), destinations=list(range(4, len(haushalte) + 4)), profile='pedestrian')
cost_matrix = np.array(valhalla_sources_to_targets.durations).T

solver = pulp.PULP_CBC_CMD(msg=False) # see solvers available in pulp reference
MAX_COVERAGE = 600 # maximum acceptable service duration, 10 minutes
ai = np.full((1, len(haushalte)), 1, dtype=int) # weights, all set to 1 for demos sake

mclp_from_cost_matrix = MCLP.from_cost_matrix(cost_matrix, ai, MAX_COVERAGE, p_facilities=2)
result = mclp_from_cost_matrix.solve(solver)
mclp_from_cost_matrix.facility_client_array()

solution = {}
colors = ['orange', 'green', 'purple', 'cyan']
for i in range(len(standorte)):
    if mclp_from_cost_matrix.fac2cli[i]:
        folium.CircleMarker(
            location=[standorte[i][1], standorte[i][0]],
            radius=30,
            fill=True,
            popup=folium.Popup('Optimierte Currywurstbude', show=True),
            color=colors[i]
        ).add_to(m)
        # print(mclp_from_cost_matrix.fac2cli[i])
        solution[i] = []
        for j in mclp_from_cost_matrix.fac2cli[i]:
            solution[i].append(haushalte[j])
            folium.CircleMarker(
                location=[haushalte[j][1], haushalte[j][0]],
                radius=10,
                fill=True,
                popup="Haushalt",
                color=colors[i]
            ).add_to(m)

# print(solution)
m


# In[159]:


result.uncovered_clients()
result.get_percentage()
result.percentage


# In[ ]:




