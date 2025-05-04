def empleadostxt(nombre_archivo):
    empleados = []
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            nombre, ocupacion, precio_hora = linea.strip().split(';')
            empleados.append({
                'nombre': nombre,
                'ocupacion': ocupacion,
                'precio_hora': int(precio_hora)
            })
    return empleados


def clientestxt(nombre_archivo):
    clientes = []
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            nombre, ocupacion_requerida, presupuesto = linea.strip().split(';')
            clientes.append({
                'nombre': nombre,
                'ocupacion_requerida': ocupacion_requerida,
                'presupuesto': int(presupuesto)
            })
    return clientes


def generar_emparejamientos(clientes, empleados, emparejamiento_actual, resultados):
    if not clientes:  # Si no quedan clientes por emparejar
        resultados.append(emparejamiento_actual.copy())
        return

    cliente_actual = clientes[0]

    for empleado in empleados:
        # Verificar si el empleado cumple con los requisitos del cliente
        if (cliente_actual['ocupacion_requerida'] == empleado['ocupacion'] and
            cliente_actual['presupuesto'] >= empleado['precio_hora']):
            # Crear emparejamiento temporal
            emparejamiento_actual.append(f"{cliente_actual['nombre']} - {empleado['nombre']}")
            # Remover empleado para evitar duplicados
            empleados_restantes = empleados.copy()
            empleados_restantes.remove(empleado)
            # Continuar con los siguientes clientes
            generar_emparejamientos(clientes[1:], empleados_restantes, emparejamiento_actual, resultados)
            # Deshacer el emparejamiento actual
            emparejamiento_actual.pop()


def filtrar(clientes, resultados):
    # Filtrar únicamente los emparejamientos que incluyan a todos los clientes
    return [emp for emp in resultados if len(emp) == len(clientes)]


def main():
    # Leer datos de los archivos
    empleados = empleadostxt('Discretas Entregrables\empleados.txt')
    clientes = clientestxt('Discretas Entregrables\clientes.txt')

    # Generar todas las combinaciones de emparejamientos
    resultados = []
    generar_emparejamientos(clientes, empleados, [], resultados)

    # Filtrar emparejamientos completos (todos los clientes están emparejados)
    emparejamientos_completos = filtrar(clientes, resultados)

    # Mostrar resultados
    if emparejamientos_completos:
        n = 0
        for i, emparejamiento in enumerate(emparejamientos_completos, start=1):
            print(f"Emparejamiento {i}:")
            n = n + 1
            for par in emparejamiento:
                print(par)  
            print()
        print("Cantidad de emparejamientos: ", n)
    else:
        print("No se encontraron emparejamientos completos.")


if __name__ == "__main__":
    main()
