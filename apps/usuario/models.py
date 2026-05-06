from io import BytesIO
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from simple_history.models import HistoricalRecords
from apps.core.utils import log_error
from django.core.exceptions import ValidationError
from PIL import Image
from django.core.files.base import ContentFile
from django.templatetags.static import static

ALLOWED_FORMATS = ["JPEG", "PNG", "WEBP"]
MAX_SIZE_MB = 2
MAX_WIDTH = 800
MAX_HEIGHT = 800


import os
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name

def validar_imagen(foto):
    if foto.size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"La imagen no puede superar los {MAX_SIZE_MB} MB.")

    try:
        img = Image.open(foto)
        if img.format not in ALLOWED_FORMATS:
            raise ValidationError("Formato de imagen no permitido.")
    except Exception:
        log_error(
                mensaje="Error Archivo de imagen inválido"
        )
        raise ValidationError("Archivo de imagen inválido.")

def procesar_imagen(foto, dni, version):
    img = Image.open(foto)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((MAX_WIDTH, MAX_HEIGHT))

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=85)

    filename = f"{dni}-v{version}.webp"

    return ContentFile(buffer.getvalue(), name=filename)

def ruta_foto_usuario(instance, filename):
    return os.path.join("foto_usuario", filename)


class UsuarioManager(BaseUserManager):
    def create_user(self, username, dni, email, nombres, fch_nacimiento, password=None, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")
        if not dni:
            raise ValueError("El dni es obligatorio")
        email = self.normalize_email(email)
        dni=dni
        user = self.model(
        username=username,
        email=email,
        dni=dni,
        nombres=nombres,
        fch_nacimiento=fch_nacimiento,
        **extra_fields
    )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,dni,nombres,fch_nacimiento,email=None,password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(username,dni,email,nombres,fch_nacimiento, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    username=models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=50, null=False, blank=False)
    nombres = models.CharField(max_length=100, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fch_creacion = models.DateTimeField(auto_now_add=True)
    fch_ultimo_acceso= models.DateTimeField(auto_now=True)
    dni=models.PositiveBigIntegerField(validators=[MinValueValidator(0),MaxValueValidator(999999999)], unique=True, null=False, blank=False)
    
    cuil = models.PositiveBigIntegerField(
        validators=[MinValueValidator(19999999999), MaxValueValidator(99999999999)],
        unique=True,
        null=True,
        blank=True,
    )
    
    fch_nacimiento=models.DateField()
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    saldo_gral_flia = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    es_admin_local = models.BooleanField(default=False)

    operador_sistema = models.BooleanField(default=False)

    foto = models.ImageField(
        upload_to=ruta_foto_usuario,
        storage=OverwriteStorage(),
        null=True,
        blank=True
    )

    id_jerarquia = models.ForeignKey('datos_personales.Jerarquia', null=False, blank=False, on_delete=models.RESTRICT, related_name='datos_jerarquia')

    history = HistoricalRecords()
    

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombres', 'dni', 'fch_nacimiento', 'email' , 'cuil']


    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):

        print("📌 Inicio save()")

        update_fields = kwargs.get("update_fields")

        # 🔹 Si el save es solo para actualizar campos que NO son foto
        if update_fields and "foto" not in update_fields:
            print("⚡ Save rápido (sin procesar imagen)")
            return super().save(*args, **kwargs)

        version = 1
        old_file = None

        if self.pk:
            old = Usuario.objects.filter(pk=self.pk).values("foto").first()

            if old and old["foto"]:
                old_file = old["foto"]

                try:
                    nombre = os.path.basename(old_file)
                    version = int(nombre.split("-v")[1].split(".")[0]) + 1
                except:
                    version = 1

        # 🔹 SOLO si realmente hay una foto nueva subida
        if self.foto and hasattr(self.foto, "_file"):

            print(f"🖼️ Procesando nueva foto: {self.foto.name}")

            # 🔹 verificar que el archivo exista
            if self.foto.name and self.foto.storage.exists(self.foto.name):

                validar_imagen(self.foto)

                self.foto = procesar_imagen(self.foto, self.dni, version)

                print(f"✅ Foto procesada: {self.foto.name}")

        print("💾 Guardando modelo...")
        super().save(*args, **kwargs)

        
    def delete(self, *args, **kwargs):
        if self.foto:
            self.foto.delete(save=False)
        super().delete(*args, **kwargs)

    @property
    def foto_url(self):
        if self.foto:
            return self.foto.url
        return static("images/foto_usuario_default.png")

