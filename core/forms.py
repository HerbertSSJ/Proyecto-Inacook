from django import forms
from django.forms import inlineformset_factory
from .models import Receta, RecetaIngrediente, Ingrediente, UnidadMedicion

class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['Nombre_Receta', 'Categoria', 'Aporte_Calorico', 'Tiempo_Preparacion', 'Procedimiento', 'Imagen']

class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ['Receta_idReceta', 'Ingrediente_idIngrediente', 'Cantidad']
        widgets = {
            'Receta_idReceta': forms.TextInput(attrs={'readonly': 'readonly'}),  # se llenará desde la vista
        }

class IngredienteForm(forms.ModelForm):
    # reemplazamos el campo por un ModelChoiceField
    UnidadMedicion_idUnidadMedicion = forms.ModelChoiceField(
        queryset=UnidadMedicion.objects.all(),
        empty_label="Selecciona una unidad",  # texto por defecto
        label="Unidad de Medición"
    )

    class Meta:
        model = Ingrediente
        fields = ['Nombre_Ingrediente', 'Calidad', 'Costo_Unitario', 'UnidadMedicion_idUnidadMedicion']


class UnidadMedicionForm(forms.ModelForm):
    class Meta:
        model = UnidadMedicion
        fields = ['Nombre_Unidad', 'Abreviatura']