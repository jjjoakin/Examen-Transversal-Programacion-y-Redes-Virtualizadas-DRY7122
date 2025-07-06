grupo = ["Joaquin Contreras", "Ismael Consuegra"]
print("Integrantes del grupo:")
for persona in grupo:
    print("-", persona)

print("\n--- VLAN ---")
# verificacion de vlan
vlan = int(input("Ingrese el número de VLAN: "))

if 1 <= vlan <= 1005:
    print("VLAN NORMAL")
elif 1006 <= vlan <= 4094:
    print("VLAN EXTENDIDA")
else:
    print("Número de VLAN inválido. Debe estar entre 1 y 4094.")