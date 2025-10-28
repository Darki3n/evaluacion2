import requests
import urllib.parse

ROUTE_URL = "https://graphhopper.com/api/1/route?"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
API_KEY = "6d19b8de-2a91-4092-a038-4260d59d07e9"

VEHICLE_MAP = {
    "auto": "car",
    "moto": "bike",
    "a pie": "foot",
}

def geocoding(location: str, key: str):
    location = location.strip()
    while location == "":
        location = input("Ingrese la ubicación nuevamente: ").strip()

    url = GEOCODE_URL + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    r = requests.get(url)
    status = r.status_code

    if status != 200:
        msg = ""
        try:
            msg = r.json().get("message", "")
        except Exception:
            pass
        print(f"Estado Geocoding API: {status}\nMensaje: {msg}")
        return status, "null", "null", location

    data = r.json()
    hits = data.get("hits", [])
    if not hits:
        print("No se encontraron resultados de geocodificación para esa consulta.")
        return status, "null", "null", location

    hit = hits[0]
    lat = hit["point"]["lat"]
    lng = hit["point"]["lng"]
    name = hit.get("name", "")
    country = hit.get("country", "")
    state = hit.get("state", "")

    if state and country:
        new_loc = f"{name}, {state}, {country}"
    elif country:
        new_loc = f"{name}, {country}"
    else:
        new_loc = name

    osm_value = hit.get("osm_value", "")
    print(f"URL de Geocoding para {new_loc} (Tipo: {osm_value})\n{url}")
    return status, lat, lng, new_loc


def pedir_ruta(orig, dest, vehicle_param: str, key: str):
    op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
    dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

    params = {
        "key": key,
        "vehicle": vehicle_param,
        "points_encoded": "false",
        "instructions": "true",
        "locale": "es"
    }

    url = ROUTE_URL + urllib.parse.urlencode(params) + op + dp
    resp = requests.get(url)
    try:
        data = resp.json()
    except Exception:
        data = {}
    return resp.status_code, data, url


while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehículos disponibles:")
    print("auto, moto, a pie")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    vehicle_in = input("Ingrese el medio de transporte (o 'salir'/'s' para terminar): ").strip().lower()

    if vehicle_in in ("salir", "s"):
        break
    if vehicle_in not in VEHICLE_MAP:
        print("Perfil no válido. Se usará 'auto'.")
        vehicle_in = "auto"

    vehicle_param = VEHICLE_MAP[vehicle_in]

    loc1 = input("Ubicación de inicio: ").strip()
    if loc1 in ("salir", "s"):
        break
    orig = geocoding(loc1, API_KEY)
    if orig[1] == "null":
        continue

    print(orig)

    loc2 = input("Destino: ").strip()
    if loc2 in ("salir", "s"):
        break
    dest = geocoding(loc2, API_KEY)
    if dest[1] == "null":
        continue

    print("=================================================")
    print(f"Indicaciones desde {orig[3]} hasta {dest[3]} en {vehicle_in}")
    print("=================================================")

    status, data, url_used = pedir_ruta(orig, dest, vehicle_param, API_KEY)
    print(f"Estado Routing API: {status}\nURL utilizada:\n{url_used}")
    print("=================================================")

    if status != 200 or "paths" not in data or not data["paths"]:
        print("No fue posible obtener la ruta.")
        print(data.get("message", "Error desconocido."))
        print("*************************************************")
        continue

    path0 = data["paths"][0]
    distancia_km = round(path0.get("distance", 0.0) / 1000.0, 2)
    seg_total = int(path0.get("time", 0) / 1000)

    hr = seg_total // 3600
    min_ = (seg_total % 3600) // 60
    sec = seg_total % 60

    print(f"Distancia total: {distancia_km:.2f} km")
    print(f"Duración estimada: {hr:02d}:{min_:02d}:{sec:02d} (hh:mm:ss)")
    print("=================================================")

    instrucciones = path0.get("instructions", [])
    if not instrucciones:
        print("No hay instrucciones disponibles.")
    else:
        for step in instrucciones:
            texto = step.get("text", "")
            distancia_tramo_km = round(step.get("distance", 0.0) / 1000.0, 2)
            print(f"- {texto} ({distancia_tramo_km:.2f} km)")

    print("=============================================")
