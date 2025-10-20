from django import forms
from .models import Receta, RecetaIngrediente, Ingrediente, UnidadMedicion

# -------------------- FORMULARIO DE RECETA --------------------
class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['Nombre_Receta', 'Categoria', 'Aporte_Calorico',
                  'Tiempo_Preparacion', 'Procedimiento', 'Imagen']

        widgets = {
            'Nombre_Receta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Pastel de choclo'
            }),
            'Categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Plato principal'
            }),
            'Aporte_Calorico': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'Tiempo_Preparacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 30 min'
            }),
            'Procedimiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el procedimiento...'
            }),
            'Imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }


# -------------------- FORMULARIO RECETA - INGREDIENTE --------------------
class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ['Receta_idReceta', 'Ingrediente_idIngrediente', 'Cantidad']

        widgets = {
            'Receta_idReceta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la receta'
            }),
            'Ingrediente_idIngrediente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ingrediente'
            }),
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
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad


# -------------------- FORMULARIO INGREDIENTE --------------------
class IngredienteForm(forms.ModelForm):
    # Ahora que UnidadMedicion es un CharField, usamos ChoiceField
    OPCIONES_UNIDAD = [
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('unidad', 'Unidad'),
        ('cda', 'Cucharada'),
        ('cdta', 'Cucharadita'),
    ]

    UnidadMedicion_idUnidadMedicion = forms.ChoiceField(
        choices=OPCIONES_UNIDAD,
        label="Unidad de Medición",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Ingrediente
        fields = ['Nombre_Ingrediente', 'Calidad', 'Costo_Unitario', 'UnidadMedicion_idUnidadMedicion']

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
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ejemplo: 1500'
            }),
        }

    def clean_Costo_Unitario(self):
        costo = self.cleaned_data.get('Costo_Unitario')
        if costo < 0:
            raise forms.ValidationError("El costo unitario no puede ser negativo.")
        return costo


# -------------------- FORMULARIO UNIDAD DE MEDICIÓN --------------------
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
