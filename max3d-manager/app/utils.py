import math
from datetime import datetime, date


def calcular_costo_material(peso, precio_por_gramo):
    return peso * precio_por_gramo if precio_por_gramo else 0


def calcular_costo_luz(horas, potencia_w, costo_kwh):
    kwh = (potencia_w * horas) / 1000
    return kwh * costo_kwh


def calcular_costo_desgaste(horas, costo_hora):
    return horas * costo_hora


def calcular_costo_modelado(horas, costo_hora):
    return horas * costo_hora


def calcular_trabajo(costo_total, porcentaje):
    return costo_total * (porcentaje / 100)


def calcular_precio_sugerido(costo_total, trabajo, redondeo=5):
    precio = costo_total + trabajo
    return redondear_precio(precio, redondeo)


def redondear_precio(valor, redondeo=5):
    if redondeo == 0:
        return round(valor, 2)
    return math.ceil(valor / redondeo) * redondeo


def calcular_totales_pedido(
    peso, precio_por_gramo,
    horas_impresion,
    horas_modelado,
    costo_hora_modelado,
    costo_pintura=0,
    potencia_w=300,
    costo_kwh=0.000153,
    costo_desgaste_hora=0.75,
    trabajo_porcentaje=20,
    redondeo=5
):
    material = calcular_costo_material(peso, precio_por_gramo)
    luz = calcular_costo_luz(horas_impresion, potencia_w, costo_kwh)
    desgaste = calcular_costo_desgaste(horas_impresion, costo_desgaste_hora)
    modelado = calcular_costo_modelado(horas_modelado, costo_hora_modelado)
    costo_total = material + luz + desgaste + costo_pintura + modelado
    trabajo = calcular_trabajo(costo_total, trabajo_porcentaje)
    precio_sugerido = calcular_precio_sugerido(costo_total, trabajo, redondeo)

    return {
        "costo_material": round(material, 2),
        "costo_luz": round(luz, 2),
        "costo_desgaste": round(desgaste, 2),
        "costo_modelado": round(modelado, 2),
        "costo_total": round(costo_total, 2),
        "trabajo": round(trabajo, 2),
        "precio_sugerido": precio_sugerido,
        "ganancia_estimada": round(precio_sugerido - costo_total, 2),
    }


def formatear_moneda(valor, moneda="Q"):
    return f"{moneda}{valor:,.2f}"


def fecha_hoy():
    return date.today().isoformat()


def fecha_hora_ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
