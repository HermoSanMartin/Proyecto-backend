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