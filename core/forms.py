from django import forms
from django.core.exceptions import ValidationError
from .models import Receta, RecetaIngrediente, Ingrediente, UnidadMedicion


# ========================================================
# FORMULARIO DE RECETA 
# ========================================================

class RecetaForm(forms.ModelForm):

    class Meta:
        model = Receta
        fields = [
            'Nombre_Receta',
            'Categoria',
            'Aporte_Calorico',
            'Tiempo_Preparacion',
            'imagen',
        ]

        widgets = {
            'Nombre_Receta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Pastel de choclo'
            }),
            'Categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Postre, Entrada...'
            }),
            'Aporte_Calorico': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'Tiempo_Preparacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 30 min'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    # ========================================================
    # VALIDACIONES
    # ========================================================

    def clean_Nombre_Receta(self):
        nombre = self.cleaned_data.get('Nombre_Receta', '').strip()

        if len(nombre) < 4:
            raise ValidationError("El nombre de la receta es demasiado corto.")

        if any(ch.isdigit() for ch in nombre):
            raise ValidationError("El nombre de la receta no puede contener números.")

        return nombre.title()

    def clean_Categoria(self):
        categoria = self.cleaned_data.get('Categoria', '').strip()

        if len(categoria) < 3:
            raise ValidationError("La categoría es demasiado corta.")

        if any(ch.isdigit() for ch in categoria):
            raise ValidationError("La categoría no puede contener números.")

        return categoria.title()

    def clean_Aporte_Calorico(self):
        valor = self.cleaned_data.get('Aporte_Calorico')

        if valor is None:
            raise ValidationError("Debes ingresar un aporte calórico.")

        if valor < 0:
            raise ValidationError("El aporte calórico no puede ser negativo.")

        return valor

    def clean_Tiempo_Preparacion(self):
        tiempo = self.cleaned_data.get('Tiempo_Preparacion', '').strip()

        if len(tiempo) < 3:
            raise ValidationError("El tiempo de preparación es demasiado corto.")

        return tiempo

    def clean(self):
        return super().clean()


# ========================================================
# FORMULARIO RECETA - INGREDIENTE
# ========================================================

class RecetaIngredienteForm(forms.ModelForm):
    
    class Meta:
        model = RecetaIngrediente
        fields = ['Receta', 'Ingrediente', 'Cantidad']

        widgets = {
            'Receta': forms.Select(attrs={'class': 'form-select'}),
            'Ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'Cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.1',
                'step': '0.01',
                'placeholder': 'Cantidad utilizada'
            }),
        }

    def clean_Cantidad(self):
        cantidad = self.cleaned_data.get('Cantidad')

        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")

        return cantidad


# ========================================================
# FORMULARIO INGREDIENTE
# ========================================================

class IngredienteForm(forms.ModelForm):

    class Meta:
        model = Ingrediente
        fields = ['Nombre_Ingrediente', 'Calidad', 'Costo_Unitario', 'UnidadMedicion']

        widgets = {
            'Nombre_Ingrediente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Harina'
            }),
            'Calidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Premium / Normal'
            }),
            'Costo_Unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'UnidadMedicion': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    # ---------------- VALIDACIONES PERSONALIZADAS ----------------

    def clean_Nombre_Ingrediente(self):
        nombre = self.cleaned_data.get('Nombre_Ingrediente', '').strip()

        if len(nombre) < 3:
            raise ValidationError("El nombre del ingrediente debe tener al menos 3 caracteres.")

        # primera letra de cada palabra en mayúscula
        nombre_normalizado = nombre.title()

        # Evita duplicados pero si permite cuando se edita el mismo ingrediente
        qs = Ingrediente.objects.filter(Nombre_Ingrediente__iexact=nombre_normalizado)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Este ingrediente ya está registrado.")

        return nombre_normalizado


    def clean_Costo_Unitario(self):
        costo = self.cleaned_data.get('Costo_Unitario')

        if costo is None:
            raise ValidationError("Debes ingresar un costo unitario.")

        if costo <= 0:
            raise ValidationError("El costo unitario debe ser mayor a 0.")

        return costo


    def clean(self):
        cleaned = super().clean()

        calidad = cleaned.get("Calidad")

        if calidad:
            calidad = calidad.strip()

            # No permitir valores numéricos
            if any(char.isdigit() for char in calidad):
                raise ValidationError("La calidad no puede contener números.")

            # Normaliza
            cleaned["Calidad"] = calidad.title()

        return cleaned

# ========================================================
# FORMULARIO UNIDAD DE MEDICIÓN
# ========================================================

class UnidadMedicionForm(forms.ModelForm):

    class Meta:
        model = UnidadMedicion
        fields = ['Nombre_Unidad', 'Abreviatura']

        widgets = {
            'Nombre_Unidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Gramos'
            }),
            'Abreviatura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: g'
            }),
        }

    # ---------------- VALIDACIONES PERSONALIZADAS ----------------

    def clean_Abreviatura(self):
        abrev = self.cleaned_data.get('Abreviatura').strip()

        if len(abrev) > 5:
            raise ValidationError("La abreviatura no puede tener más de 5 caracteres.")

        return abrev

    def clean_Nombre_Unidad(self):
        nombre = self.cleaned_data.get("Nombre_Unidad").strip()

        # Evitar unidades duplicadas
        if UnidadMedicion.objects.filter(Nombre_Unidad__iexact=nombre).exists():
            raise ValidationError("Esta unidad ya existe.")

        return nombre.title()

