from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction

from Cliente.models import Clientes

from .models import *

@method_decorator(csrf_exempt, name='dispatch')
class CrearMesa(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            id_administrador = request.POST.get('id_administrador', 1)

            observacion = request.POST.get('observacion')
            estado = request.POST.get('estado')
            activa = request.POST.get('activa')
            max_personas = request.POST.get('max_personas')

            administrador = Administrador.objects.first()

            mesa = Mesas(
                id_administrador=administrador,
                observacion=observacion,
                estado=estado,
                activa=activa,
                maxpersonas=max_personas,
                sestado=1
            )
            mesa.save()

            return JsonResponse({'mensaje': 'Mesa creada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class MostrarMesas(View):
    def get(self, request, *args, **kwargs):
        try:
            mesas = Mesas.objects.all()
            mesas_list = []

            for mesa in mesas:
                mesa_info = {
                    'id_mesa': mesa.id_mesa,
                    'observacion': mesa.observacion,
                    'estado': mesa.estado,
                    'activa': mesa.activa,
                    'max_personas': mesa.maxpersonas
                }
                mesas_list.append(mesa_info)

            return JsonResponse({'mesas': mesas_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class EditarMesa(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            mesa_id = kwargs.get('id_mesa')
            mesa = Mesas.objects.get(id_mesa=mesa_id)

            observacion = request.POST.get('observacion')
            estado = request.POST.get('estado')
            activa = request.POST.get('activa')
            max_personas = request.POST.get('max_personas')

            # Validar valores de estado y activa
            if estado not in ['D', 'R', 'U', 'A']:
                return JsonResponse({'error': 'Valor no válido para estado'}, status=400)

            if activa not in ['0', '1']:
                return JsonResponse({'error': 'Valor no válido para activa'}, status=400)

            mesa = Mesas.objects.get(id_mesa=mesa_id)

            mesa.observacion = observacion
            mesa.estado = estado
            mesa.activa = activa
            mesa.maxpersonas = max_personas
            mesa.save()

            return JsonResponse({'mensaje': 'Mesa editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearReservacion(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            id_cliente = request.POST.get('id_cliente')
            id_mesa = request.POST.get('id_mesa')
            fecha_reserva = request.POST.get('fecha_reserva')
            hora_reserva = request.POST.get('hora_reserva')
            estado = request.POST.get('estado')

            # Asegúrate de que los valores de estado sean válidos
            if estado not in ['E', 'D', 'F']:
                return JsonResponse({'error': 'Valor no válido para estado'}, status=400)

            # Realiza validaciones adicionales según tus necesidades

            cliente = Clientes.objects.get(id_cliente=id_cliente)
            mesa = Mesas.objects.get(id_mesa=id_mesa)

            reservacion = Reservaciones(
                id_cliente=cliente,
                id_mesa=mesa,
                fecha_reserva=fecha_reserva,
                hora_reserva=hora_reserva,
                estado=estado
            )
            reservacion.save()

            return JsonResponse({'mensaje': 'Reservación creada con éxito'})
        except Clientes.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=400)
        except Mesas.DoesNotExist:
            return JsonResponse({'error': 'Mesa no encontrada'}, status=400)
        except Exception as e:
            # Loguea el error para tener un registro detallado
            print(f'Error en la creación de reservación: {str(e)}')
            return JsonResponse({'error': 'Error al procesar la solicitud'}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class ListarReservaciones(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las reservaciones
            reservaciones = Reservaciones.objects.all()

            # Serializar los datos
            reservaciones_data = []
            for reservacion in reservaciones:
                reservacion_data = {
                    'id_reservacion': reservacion.id_reservacion,
                    'id_cliente': reservacion.id_cliente.id_cliente,
                    'id_mesa': reservacion.id_mesa.id_mesa,
                    'fecha_reserva': reservacion.fecha_reserva.strftime('%Y-%m-%d'),
                    'hora_reserva': reservacion.hora_reserva.strftime('%H:%M:%S'),
                    'estado': reservacion.estado,
                }
                reservaciones_data.append(reservacion_data)

            return JsonResponse({'reservaciones': reservaciones_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')       
class EditarReservacion(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            reservacion_id = kwargs.get('id_reservacion')
            reservacion = Reservaciones.objects.get(id_reservacion=reservacion_id)

            # Obtener los datos del cuerpo de la solicitud
            fecha_reserva = request.POST.get('fecha_reserva')
            hora_reserva = request.POST.get('hora_reserva')
            estado = request.POST.get('estado')
            id_mesa = request.POST.get('id_mesa')

            # Actualizar los campos de la reservación
            reservacion.fecha_reserva = fecha_reserva
            reservacion.hora_reserva = hora_reserva
            reservacion.estado = estado

            # Validar si se proporcionó el nuevo id_mesa
            if id_mesa:
                # Actualizar el id_mesa solo si se proporciona un nuevo valor
                reservacion.id_mesa = Mesas.objects.get(id_mesa=id_mesa)

            reservacion.save()

            return JsonResponse({'mensaje': 'Reservación editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
