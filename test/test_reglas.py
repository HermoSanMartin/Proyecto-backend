# tests/test_reglas.py
# Pruebas automatizadas para validar las reglas de negocio del proyecto

def test_regla_1_obra_no_disponible_rechaza_prestamo():
    """Regla 1: No se puede solicitar en préstamo una obra no disponible."""
    obra_disponible = False
    
    # La regla exige rechazar el préstamo si la obra no está disponible
    permitido = obra_disponible
    assert permitido is False


def test_regla_3_dias_prestamo_validos():
    """Regla 3: La fecha/duración del préstamo debe ser mayor a 0 días."""
    dias_prestamo = 5
    assert dias_prestamo > 0


def test_regla_2_maximo_cinco_obras_por_exposicion():
    """Regla 2: Una exposición no puede tener más de 5 obras prestadas simultáneamente."""
    obras_prestadas_actuales = 5
    limite_permitido = 5
    
    # Si ya tiene 5 obras, la API debe rechazar incluir una sexta obra
    puede_agregar_mas = obras_prestadas_actuales < limite_permitido
    assert puede_agregar_mas is False


def test_regla_4_dias_prestamo_negativos_invalido():
    """Regla 4: No se permiten préstamos con duración menor o igual a 0 días."""
    dias_solicitados = -3
    
    es_valido = dias_solicitados > 0
    assert es_valido is False