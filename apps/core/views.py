from apps.parametro.models.estado import Estado


def get_estado_activo():
    return Estado.objects.filter(dsc_estado__iexact="ACTIVO", flg_activo=True).first()


def get_estado_inactivo():
    return Estado.objects.filter(dsc_estado__iexact="INACTIVO", flg_activo=True).first()
