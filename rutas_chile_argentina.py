import requests
import sys

API_KEY = "pk.a80c038d1216a7f74595a805da522f92"

TRANSPORTES = {
    "1": "driving",
    "2": "cycling",
    "3": "walking"
}

TRADUCCIONES_TIPO = {
    "turn": "Gire",
    "depart": "Comience",
    "arrive": "Ha llegado a su destino",
    "roundabout": "Tome la salida {exit} en la rotonda",
    "new name": "Continúe",
    "off ramp": "Salga por la rampa",
    "end of road": "Al final de la calle",
    "continue": "Continúe",
    "merge": "Incorpórese",
    "fork": "Tome la bifurcación",
    "on ramp": "Tome la rampa de acceso",
    "notification": "",
    "exit roundabout": "Salga de la rotonda",
    "exit rotary": "Salga de la rotonda",
    "roundabout turn": "Gire en la rotonda",
}

TRADUCCIONES_MODIFICADOR = {
    "right": "derecha",
    "left": "izquierda",
    "sharp right": "derecha cerrada",
    "sharp left": "izquierda cerrada",
    "slight right": "ligeramente a la derecha",
    "slight left": "ligeramente a la izquierda",
    "straight": "recto",
    "recto": "recto",
    "recta": "recto",
    "uturn": "media vuelta",
}

def traducir_instruccion(tipo, modificador, salida):
    texto_tipo = TRADUCCIONES_TIPO.get(tipo.lower(), tipo.capitalize())
    texto_modif = TRADUCCIONES_MODIFICADOR.get(modificador.lower(), modificador)
    
    if tipo == "roundabout" and salida:
        return texto_tipo.format(exit=salida)
    if tipo == "arrive":
        return texto_tipo
    
    if tipo == "continue":
        if modificador in ["straight", "recto", "recta"]:
            return "Continúe recto"
        elif modificador:
            return f"Continúe a la {texto_modif}"
        else:
            return "Continúe"
    
    if modificador:
        if texto_modif == "recto":
            return f"{texto_tipo} recto"
        else:
            return f"{texto_tipo} a la {texto_modif}"
    else:
        return texto_tipo

def geocodificar(ciudad, pais):
    url = "https://us1.locationiq.com/v1/search.php"
    params = {
        "key": API_KEY,
        "q": f"{ciudad}, {pais}",
        "format": "json",
        "limit": 1
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Error en geocodificación: {response.status_code}")
        return None
    data = response.json()
    if not data:
        print(f"❌ No se encontró la ciudad: {ciudad}, {pais}")
        return None
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    print(f"📍 Coordenadas para {ciudad}, {pais}: ({lat}, {lon})")
    return (lat, lon)

def calcular_ruta(origen_coords, destino_coords, transporte):
    url = f"https://router.project-osrm.org/route/v1/{transporte}/{origen_coords[1]},{origen_coords[0]};{destino_coords[1]},{destino_coords[0]}"
    params = {
        "overview": "false",
        "steps": "true",
        "alternatives": "false"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Error al calcular la ruta: {response.status_code}")
        return
    data = response.json()
    if data["code"] != "Ok":
        print(f"❌ Error en la respuesta de ruta: {data['code']}")
        return
    route = data["routes"][0]
    distancia_km = route["distance"] / 1000
    distancia_millas = distancia_km * 0.621371
    duracion_min = route["duration"] / 60
    duracion_horas = duracion_min / 60
    print("\n=== Ruta calculada ===")
    print(f"📏 Distancia: {distancia_km:.2f} km / {distancia_millas:.2f} millas")
    print(f"🕒 Duración estimada: {duracion_min:.1f} minutos ({duracion_horas:.2f} horas)")
    print("📘 Instrucciones del viaje:")

    for leg in route["legs"]:
        for step in leg["steps"]:
            maneuver = step["maneuver"]
            tipo = maneuver.get("type", "").lower()
            modificador = maneuver.get("modifier", "").lower()
            salida = maneuver.get("exit", "")
            calle = step.get("name", "")
            
            instruccion = traducir_instruccion(tipo, modificador, salida)
            
            if calle and tipo != "arrive":
                instruccion += f" en {calle}"
            
            print(f"• {instruccion}")

def menu():
    print("=== Ruta entre ciudades de Chile y Argentina ===")
    print("Opciones de transporte:")
    print("1 - Auto")
    print("2 - Bicicleta")
    print("3 - Caminando")
    print("s - Salir")

    while True:
        opcion = input("\nSelecciona tipo de transporte (1/2/3) o 's' para salir: ").lower()
        if opcion == 's':
            print("👋 Saliendo del programa.")
            sys.exit()

        transporte = TRANSPORTES.get(opcion)
        if not transporte:
            print("❌ Opción inválida. Intenta de nuevo.")
            continue

        ciudad_origen = input("Ingrese ciudad de origen (Chile): ").strip()
        ciudad_destino = input("Ingrese ciudad de destino (Argentina): ").strip()

        origen_coords = geocodificar(ciudad_origen, "Chile")
        destino_coords = geocodificar(ciudad_destino, "Argentina")

        if not origen_coords or not destino_coords:
            print("❌ No se pudieron obtener las coordenadas. Intenta con otras ciudades.")
            continue

        calcular_ruta(origen_coords, destino_coords, transporte)

if __name__ == "__main__":
    menu()
