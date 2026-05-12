from apps.parametro.models.estado import Estado


def get_estado_inactivo():
    return Estado.objects.filter(dsc_estado__iexact="INACTIVO", flg_activo=True).first()