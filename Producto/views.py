from django.http import JsonResponse
from django.db.models import Max, ExpressionWrapper, IntegerField
from django.views import View
from .models import *
from Login.models import Cuenta
from Bodega.models import Bodegas
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from PIL import Image, UnidentifiedImageError
from Login.models import Cuenta
from Combos.models import Combo
from django.db import transaction
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator,EmptyPage
from horariossemanales.models import Horariossemanales
from Inventario.models import Inventario
import json
from django.db.models import Max, F
from django.core.serializers import serialize
from decimal import Decimal
import traceback

@method_decorator(csrf_exempt, name='dispatch')
class CrearTipoProducto(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear un tipo de producto'}, status=403)
            data = json.loads(request.body)
            tp_nombre = data.get('tp_nombre')
            descripcion = data.get('descripcion')

            tipo_producto = TiposProductos.objects.create(tpnombre=tp_nombre, descripcion=descripcion,sestado=1)
            tipo_producto.save()

            return JsonResponse({'mensaje': 'Tipo de producto creado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class tipoProductoExist(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            tpnombre = data.get('tpnombre')

            obt=TiposProductos.objects.filter(tpnombre=tpnombre).first()
            if obt is not None:
                return JsonResponse({'mensaje': '1'})
            return JsonResponse({'mensaje': '0'})
        except Exception as e:
            return JsonResponse({'error xd': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CategoriaExist(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            catnombre = data.get('catnombre')

            obt=Categorias.objects.filter(catnombre=catnombre).first()
            if obt is not None:
                return JsonResponse({'mensaje': '1'})
            return JsonResponse({'mensaje': '0'})
        except Exception as e:
            return JsonResponse({'error xd': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CrearCategoria(View):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear una categoría'}, status=403)

            id_tipo_producto = request.POST.get('id_tipoproducto')
            cat_nombre = request.POST.get('catnombre')
            descripcion = request.POST.get('descripcion')

            imagen_archivo = request.FILES.get('imagencategoria')  # Cambiado a request.FILES
            image_64_encode=None
            if imagen_archivo:
                try:
                    image_read = imagen_archivo.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            tipo_producto = TiposProductos.objects.get(id_tipoproducto=id_tipo_producto)

            categoria = Categorias(
                id_tipoproducto=tipo_producto,
                catnombre=cat_nombre,
                descripcion=descripcion,
                imagencategoria=image_64_encode,
                sestado=1
            )
            categoria.save()

            return JsonResponse({'mensaje': 'Categoría creada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class ListaTiposYCategorias(View):
    def get(self, request, *args, **kwargs):
        try:
            tipos_productos = TiposProductos.objects.filter(sestado=1)
            data = []

            for tipo_producto in tipos_productos:
                categorias = Categorias.objects.filter(id_tipoproducto=tipo_producto)
                categorias_data = []

                for categoria in categorias:
                    imagencategoria = categoria.imagencategoria
                    imagencategoria_base64 = None

                    if imagencategoria:
                        imagencategoria_base64 = self.convertir_imagen_a_base64(imagencategoria)

                    categoria_data = {
                        'id_categoria': categoria.id_categoria,
                        'imagencategoria': imagencategoria_base64,
                        'catnombre': categoria.catnombre,
                        'descripcion': categoria.descripcion
                    }

                    categorias_data.append(categoria_data)

                tipo_producto_data = {
                    'id_tipoproducto': tipo_producto.id_tipoproducto,
                    'tpnombre': tipo_producto.tpnombre,
                    'descripcion': tipo_producto.descripcion,
                    'sestado':tipo_producto.sestado,
                    'categorias': categorias_data
                }

                data.append(tipo_producto_data)

            return JsonResponse({'tipos_y_categorias': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def convertir_imagen_a_base64(self, imagen):
        # Convierte la imagen a base64 y devuelve la cadena resultante
        return base64.b64encode(imagen).decode('utf-8') if imagen else None
@method_decorator(csrf_exempt, name='dispatch')
class ListaTiposProductos(View):
    def get(self, request, *args, **kwargs):
        try:
            tipos_productos = TiposProductos.objects.filter(sestado=1)
            data = []
            for tipo_producto in tipos_productos:
                tipo_producto_data = {
                    'id_tipoproducto': tipo_producto.id_tipoproducto,
                    'tpnombre': tipo_producto.tpnombre,
                    'descripcion': tipo_producto.descripcion,
                }

                data.append(tipo_producto_data)

            return JsonResponse({'tipos_productos': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class ListaCategorias(View):
    def get(self, request, *args, **kwargs):
        try:
            categorias = Categorias.objects.filter(sestado=1)
            data = []

            for categoria in categorias:
                imagencategoria = categoria.imagencategoria
                imagencategoria_base64 = None

                if imagencategoria:
                    try:
                        byteImg = base64.b64decode(imagencategoria)
                        imagencategoria_base64 = base64.b64encode(byteImg).decode('utf-8')
                    except Exception as img_error:
                        print(f"Error al procesar imagen: {str(img_error)}")

                tipo_producto_data = {
                    'id_tipoproducto': categoria.id_tipoproducto.id_tipoproducto,
                }

                categoria_data = {
                    'id_categoria': categoria.id_categoria,
                    'imagencategoria': imagencategoria_base64,
                    'catnombre': categoria.catnombre,
                    'descripcion': categoria.descripcion,
                    'id_tipoproducto': tipo_producto_data
                }

                data.append(categoria_data)

            return JsonResponse({'categorias': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
#@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarTipoProducto(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear editar un tipo de producto'}, status=403)
            tipo_producto_id = kwargs.get('tipo_producto_id') 
            tipo_producto = TiposProductos.objects.get(id_tipoproducto=tipo_producto_id)
            tipo_producto.tpnombre = request.POST.get('tpnombre', tipo_producto.tpnombre)
            tipo_producto.descripcion = request.POST.get('descripcion', tipo_producto.descripcion)
            if(request.POST.get('sestado')):
                tipo_producto.sestado = request.POST.get('sestado')
            tipo_producto.save()

            return JsonResponse({'mensaje': 'Tipo de producto editado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
#@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarCategoria(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear editar una categoría'}, status=403)
            categoria_id = kwargs.get('categoria_id')  # Asegúrate de tener la URL configurada para recibir el ID de la categoría
            categoria = Categorias.objects.get(id_categoria=categoria_id)
            imagencategoria = request.FILES.get('imagencategoria')
            nombre= request.POST.get('catnombre')
            if(nombre):
                categoria.catnombre =nombre
            descripcion = request.POST.get('descripcion')
            if(descripcion):
                categoria.descripcion=descripcion
            estado= request.POST.get('sestado')
            if(estado):
                categoria.sestado =estado
            tipo= request.POST.get('id_tipoproducto', categoria.id_tipoproducto.id_tipoproducto)
            if tipo:
                categoria.id_tipoproducto=TiposProductos.objects.get(id_tipoproducto=tipo)
            if imagencategoria:
                try:
                    image_read = imagencategoria.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                    categoria.imagencategoria=image_64_encode
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)
            
            categoria.save()
            return JsonResponse({'mensaje': 'Categoría editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CrearUnidadMedida(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
           #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear una unidad de medida'}, status=403)
            data = json.loads(request.body)
            nombre_um = data.get('nombre_um')
            unidad_medida = UnidadMedida.objects.create(nombreum=nombre_um,sestado=1)
            unidad_medida.save()
            return JsonResponse({'mensaje': 'Unidad de medida creada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class ListarUnidadesMedida(View):
    def get(self, request, *args, **kwargs):
        try:
            unidades_medida = UnidadMedida.objects.filter(sestado=1)
            data = []

            for unidad in unidades_medida:
                unidad_data = {
                    'id_um': unidad.idum,
                    'nombre_um': unidad.nombreum,
                }

                data.append(unidad_data)

            return JsonResponse({'unidades_medida': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class CrearProducto(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear un producto'}, status=403)
            id_categoria = request.POST.get('id_categoria')
            id_um = request.POST.get('id_um')
            imagen_p = request.FILES.get('imagen_p')
            puntosp = request.POST.get('puntos_p')
            nombreproducto = request.POST.get('nombre_producto')
            descripcionproducto = request.POST.get('descripcion_producto')
            preciounitario = request.POST.get('precio_unitario')
            iva = request.POST.get('iva')
            ice = request.POST.get('ice')
            irbpnr = request.POST.get('irbpnr')
            image_64_encode=None
            if imagen_p:
                try:
                    image_read = imagen_p.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            # Crear el producto
            categoria = Categorias.objects.get(id_categoria=id_categoria)
            unidad_medida = UnidadMedida.objects.get(idum=id_um)
            producto = Producto.objects.create(
                id_categoria=categoria,
                id_um=unidad_medida,
                imagenp=image_64_encode,
                puntosp=puntosp,
                codprincipal=obtener_siguiente_codprincipal(),
                nombreproducto=nombreproducto,
                descripcionproducto=descripcionproducto,
                preciounitario=preciounitario,
                iva=iva,
                ice=ice,
                irbpnr=irbpnr,
                sestado = 1
            )
            detalle_comp = json.loads(request.POST.get('detalle_comp'))
            if detalle_comp:
                cantidadpadre = Decimal(request.POST.get('cantidad', 0))
                
                ensambleproducto = EnsambleProducto.objects.create(
                    id_producto=producto,
                    padrecantidad=cantidadpadre,
                    id_um=unidad_medida  # Ajusta esta línea según tu lógica
                )
                for detalle_data in detalle_comp:
                    componente_hijo = Componente.objects.get(id_componente=detalle_data['id'])
                    um = componente_hijo.id_um
                    detalleEnsambleProducto = DetalleEnsambleProducto.objects.create(
                        id_emsamblep=ensambleproducto,
                        id_componentehijo=componente_hijo,
                        cantidadhijo=detalle_data['cantidad'],
                        id_umhijo=um
                    )
            producto.save()        

            return JsonResponse({'mensaje': 'Producto creado con éxito'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
#@method_decorator(login_required, name='dispatch')
class EditarUnidadMedida(View):
    @transaction.atomic
    def post(self, request, unidad_id, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para editar una unidad de medida'}, status=403)

            unidad = UnidadMedida.objects.get(idum=unidad_id)

            unidad.nombreum = request.POST.get('nombreum', unidad.nombreum)
            unidad.sestado = request.POST.get('sestado', unidad.sestado)
            unidad.save()

            return JsonResponse({'mensaje': 'Unidad de medida editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
#@method_decorator(login_required, name='dispatch')
class EditarProducto(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            producto_id = kwargs.get('producto_id')
            producto = Producto.objects.get(id_producto=producto_id)
            producto.id_categoria = Categorias.objects.get(id_categoria=request.POST.get('id_categoria', producto.id_categoria.id_categoria))
            producto.id_um = UnidadMedida.objects.get(idum=request.POST.get('id_um', producto.id_um.idum))
            producto.puntosp = request.POST.get('puntosp', producto.puntosp)
            producto.codprincipal = request.POST.get('codprincipal', producto.codprincipal)
            producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
            producto.descripcionproducto = request.POST.get('descripcionproducto', producto.descripcionproducto)
            producto.preciounitario = request.POST.get('preciounitario', producto.preciounitario)
            producto.iva = request.POST.get('iva', producto.iva)
            producto.ice = request.POST.get('ice', producto.ice)
            producto.irbpnr = request.POST.get('irbpnr', producto.irbpnr)

            # Manejo de la imagen
            imagen_producto = request.FILES.get('imagenp')
            if imagen_producto:
                try:
                    image_read = imagen_producto.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                    producto.imagenp = image_64_encode
                except Exception as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            producto.save()

            return JsonResponse({'mensaje': 'Producto editado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CrearComponente(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            costo = request.POST.get('costo')
            tipo = request.POST.get('tipo')
            id_um = request.POST.get('id_um')
            id_categoria = request.POST.get('id_categoria')

            # Verificar que la unidad de medida exista
            unidad_medida = UnidadMedida.objects.get(idum=id_um)
            categoria = Categorias.objects.get(id_categoria=id_categoria)

            if tipo == 'N':
                componente = Componente.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    costo=costo,
                    tipo=tipo,
                    id_um=unidad_medida,
                    id_categoria=categoria,
                    sestado=1
                )
            cantidadpadre = Decimal(request.POST.get('cantidad', 0))
            if tipo == 'F' and cantidadpadre > 0:
                detalle_comp = json.loads(request.POST.get('detalle_comp', '[]'))
                componente = Componente.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    costo=costo,
                    tipo=tipo,
                    id_um=unidad_medida,
                    id_categoria=categoria,
                    sestado=1
                )
                ensamblecomponente = EnsambleComponente.objects.create(
                    id_componentepadre=componente,
                    padrecantidad=cantidadpadre,
                    id_umpadre=unidad_medida  # Ajusta esta línea según tu lógica
                )
                for detalle_data in detalle_comp:
                    componente_hijo = Componente.objects.get(id_componente=detalle_data['id'])
                    um = componente_hijo.id_um
                    detalleensamblecomponente = DetalleEnsambleComponente.objects.create(
                        id_ensamblec=ensamblecomponente,
                        id_componentehijo=componente_hijo,
                        cantidadhijo=detalle_data['cantidad'],
                        id_umhijo=um
                    )

            return JsonResponse({'mensaje': 'Componente creado con éxito'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class EliminarComponentex(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            id_componente = request.POST.get('id_componente')
            componente = Componente.objects.get(id_componente=id_componente)
            componente.costo=None
            componente.sestado = 0
            ensamble=DetalleEnsambleComponente.objects.filter(id_componentehijo=componente)
            if(ensamble.exists()):
                return JsonResponse({'error': 'Este artículo ensambla otros productos, no se puede eliminar'},status=400)
            ensamble= EnsambleComponente.objects.filter(id_componentepadre=id_componente)
            ensamble.delete()
            componente.save()

            return JsonResponse({'mensaje': 'Artículo eliminado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class ListarComponentes(View):
    def get(self, request, *args, **kwargs):
        try:
            componentes = Componente.objects.filter(sestado=1)
            lista_componentes = []
            for componente in componentes:
                tipo_producto_data = {
                    'id_categoria': componente.id_categoria.id_categoria,
                    'catnombre': componente.id_categoria.catnombre,
                }
                ensambleexi = EnsambleComponente.objects.filter(id_componentepadre=componente)
                if (ensambleexi.exists()):
                    ensamble=EnsambleComponente.objects.get(id_componentepadre=componente)
                    detallesensamble=DetalleEnsambleComponente.objects.filter(id_ensamblec=ensamble)
                    lista_detalle = []
                    for detalle in detallesensamble:
                        hijo={
                            'id':detalle.id_componentehijo.id_componente,
                            'nombre':detalle.id_componentehijo.nombre
                        }
                        um={
                            'id':detalle.id_umhijo.idum,
                            'nombre':detalle.id_umhijo.nombreum
                        }
                        ensamble_data = {
                            'id_componentehijo':hijo,
                            'cantidadhijo': detalle.cantidadhijo,
                            'um':um
                        }
                        lista_detalle.append(ensamble_data)
                    compdata={
                        'padrecant':ensamble.padrecantidad,
                        'detalle':lista_detalle
                    }
                    componente_data = {
                        'id_componente': componente.id_componente,
                        'nombre': componente.nombre,
                        'descripcion': componente.descripcion,
                        'costo': str(componente.costo).replace('€', '').replace('$', ''),
                        'tipo': componente.tipo,
                        'id_um': componente.id_um.idum,
                        'id_categoria': tipo_producto_data,
                        'nombre_um': componente.id_um.nombreum,
                        'detalle':compdata,
                    }
                    lista_componentes.append(componente_data)
                else:
                    componente_data = {
                        'id_componente': componente.id_componente,
                        'nombre': componente.nombre,
                        'descripcion': componente.descripcion,
                        'costo': str(componente.costo).replace('€', '').replace('$', ''),
                        'tipo': componente.tipo,
                        'id_um': componente.id_um.idum,
                        'id_categoria': tipo_producto_data,
                        'nombre_um': componente.id_um.nombreum,
                    }
                    lista_componentes.append(componente_data)
            return JsonResponse({'componentes': lista_componentes})
        except Exception as e:
            # Manejar errores aquí
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class ComponentesDisponibles(View):
    def post(self, request, *args, **kwargs):
        try:
            id_componente = request.POST.get('id_componente')
            cantxensamble = Decimal(request.POST.get('cantxensamble'))
            catngenensamble = Decimal(request.POST.get('catngenensamble'))
            id_componentegen = request.POST.get('id_componentegen')
            cantxfabricar = Decimal(request.POST.get('cantxfabricar'))
            componentepadre= Componente.objects.get(id_componente=id_componentegen)
            componentehijo= Componente.objects.get(id_componente=id_componente)
            id_bodega = Bodegas.objects.get(id_bodega=(request.POST.get('id_bodega')))
            ensamble = EnsambleComponente.objects.get(id_componentepadre=componentepadre)
            detalle = DetalleEnsambleComponente.objects.filter(id_ensamblec=ensamble, id_componentehijo=componentehijo)
            
            cantnecesaria = (cantxensamble * cantxfabricar) / catngenensamble
            
            inventario = Inventario.objects.get(id_componente=componentehijo, id_bodega=id_bodega)
            print(cantnecesaria)
            print('<=')
            print(float(inventario.cantidad_disponible))
            if float(cantnecesaria) <= float(inventario.cantidad_disponible):
                print(1)
                return JsonResponse({'mensaje': 1})
            else:
                print('Cantidad de fabricar: '+request.POST.get('cantxfabricar'))
                print(0)
                return JsonResponse({'mensaje': 0})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class ComponentesDisponiblesPro(View):
    def post(self, request, *args, **kwargs):
        try:
            id_componente = request.POST.get('id_componente')
            cantxensamble = Decimal(request.POST.get('cantxensamble'))
            catngenensamble = Decimal(request.POST.get('catngenensamble'))
            id_productogen = request.POST.get('id_productogen')
            cantxfabricar = Decimal(request.POST.get('cantxfabricar'))
            productopadre= Producto.objects.get(id_producto=id_productogen)
            componentehijo= Componente.objects.get(id_componente=id_componente)
            id_bodega = Bodegas.objects.get(id_bodega=(request.POST.get('id_bodega')))
            ensamble = EnsambleProducto.objects.get(id_producto=productopadre)
            detalle = DetalleEnsambleProducto.objects.filter(id_emsamblep=ensamble, id_componentehijo=componentehijo)
            
            cantnecesaria = (cantxensamble * cantxfabricar) / catngenensamble
            
            inventario = Inventario.objects.get(id_componente=componentehijo, id_bodega=id_bodega)
            print(cantnecesaria)
            print('<=')
            print(float(inventario.cantidad_disponible))
            if float(cantnecesaria) <= float(inventario.cantidad_disponible):
                print(1)
                return JsonResponse({'mensaje': 1})
            else:
                print('Cantidad de fabricar: '+request.POST.get('cantxfabricar'))
                print(0)
                return JsonResponse({'mensaje': 0})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class FabricarComponente(View):
    def post(self, request, *args, **kwargs):
        try:
            lista_componentes = json.loads(request.POST.get('lista_componentes'))
            cantidad_fabricar = Decimal(request.POST.get('cantidad_fabricar'))
            id_componente_generado = request.POST.get('id_componente_generado')
            id_bodega = request.POST.get('id_bodega')
            bodega= Bodegas.objects.get(id_bodega=id_bodega)
            componente= Componente.objects.get(id_componente=id_componente_generado)
            ensamble = EnsambleComponente.objects.get(id_componentepadre=componente)
            # Restar la cantidad de cada componente en el inventario
            for compo in lista_componentes:
                print('Recorrer lista?')
                detalle_componente = compo
                id_componente = detalle_componente.get('key')
                componentedet=Componente.objects.get(id_componente=id_componente)
                cantidad_restar = Decimal(detalle_componente.get('quantity'))
                print('cantrestar:')
                print(cantidad_restar)
                catngenensamble=Decimal(ensamble.padrecantidad)
                cantnecesaria = (cantidad_restar * cantidad_fabricar) / catngenensamble
                inventario_componente = Inventario.objects.get(id_componente=componentedet, id_bodega=bodega)
                inventario_componente.cantidad_disponible -= cantnecesaria
                inventario_componente.save()
            inventario_generado = Inventario.objects.filter(id_componente=componente, id_bodega=bodega)
            if(inventario_generado.count()>0):
                print('Esto pasa cuando sdfas?')
                inventario_gen = Inventario.objects.get(id_componente=componente, id_bodega=bodega)
                inventario_gen.cantidad_disponible += cantidad_fabricar
                inventario_gen.save()
            else:
                print('Esto sucede?')
                inventariocre= Inventario.objects.create(
                    id_bodega = bodega,
                    id_componente =  componente,
                    id_um = componente.id_um,
                    stock_minimo = '1',
                    cantidad_disponible = cantidad_fabricar
                )
            print('Funciono?')
            return JsonResponse({'mensaje': 'Operación exitosa'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class FabricarProducto(View):
    def post(self, request, *args, **kwargs):
        try:
            lista_componentes = json.loads(request.POST.get('lista_componentes'))
            cantidad_fabricar = Decimal(request.POST.get('cantidad_fabricar'))
            id_producto_generado = request.POST.get('id_producto_generado')
            id_bodega = request.POST.get('id_bodega')
            bodega= Bodegas.objects.get(id_bodega=id_bodega)
            producto= Producto.objects.get(id_producto=id_producto_generado)
            ensamble = EnsambleProducto.objects.get(id_producto=producto)
            catngenensamble=Decimal(ensamble.padrecantidad)
            # Restar la cantidad de cada componente en el inventario
            for compo in lista_componentes:
                print('Recorrer lista?')
                detalle_componente = compo
                id_componente = detalle_componente.get('key')
                componentedet=Componente.objects.get(id_componente=id_componente)
                cantidad_restar = Decimal(detalle_componente.get('quantity'))
                cantnecesaria = (cantidad_restar * cantidad_fabricar) / catngenensamble
                inventario_componente = Inventario.objects.get(id_componente=componentedet, id_bodega=bodega)
                inventario_componente.cantidad_disponible -= cantnecesaria
                inventario_componente.save()
            inventario_generado = Inventario.objects.filter(id_producto=producto, id_bodega=bodega)
            if(inventario_generado.count()>0):
                print('Esto pasa cuando sdfas?')
                inventario_gen = Inventario.objects.get(id_producto=producto, id_bodega=bodega)
                inventario_gen.cantidad_disponible += cantidad_fabricar
                inventario_gen.save()
            else:
                print('Esto sucede?')
                inventariocre= Inventario.objects.create(
                    id_bodega = bodega,
                    id_producto =  producto,
                    id_um = producto.id_um,
                    stock_minimo = '1',
                    cantidad_disponible = cantidad_fabricar
                )
            print('Funciono?')
            return JsonResponse({'mensaje': 'Operación exitosa'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class EditarComponentex(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # Obtener el ID del componente a editar de los argumentos de la URL
            id_componente = kwargs.get('id_componente')
            componente = Componente.objects.get(id_componente=id_componente)
            '''
            detalle_comp = json.loads(request.POST.get('detalle_comp', '[]'))
            return JsonResponse({'mensaje': detalle_comp})
            '''
            #hasta aca
            componente.nombre = request.POST.get('nombre')
            componente.costo = None
            tipo = request.POST.get('tipo')
            componente.tipo=tipo
            descripcion = request.POST.get('descripcion')
            costo_str = request.POST.get('costo')
            if(descripcion):
                componente.descripcion=descripcion
            if costo_str:
                componente.costo = Decimal((costo_str.replace(',', '.')))
            id_um = request.POST.get('id_um')
            if id_um and id_um != str(componente.id_um.idum):
                ensambles = DetalleEnsambleComponente.objects.filter(id_componentehijo=componente)
                if ensambles.exists():
                    return JsonResponse({'error': 'Este artículo forma parte de otros ensambles, no se puede cambiar la unidad de medida'}, status=400)
                if id_um:
                    componente.id_um = UnidadMedida.objects.get(idum=id_um)
            categoria = request.POST.get('categoria')
            if(categoria):
                componente.categoria=Categorias.objects.get(id_categoria=categoria)
            if tipo == 'N':
                componente.tipo=tipo
                componente.save()
                return JsonResponse({'mensaje': 'Componente editado con éxito'})
            cantidadpadre = Decimal(request.POST.get('cantidad', 0))
            if(tipo=='F' and cantidadpadre > 0):
                componente.tipo='F'
                ensamble=EnsambleComponente.objects.filter(id_componentepadre=componente)
                cantidadpadre = Decimal(request.POST.get('cantidad', 0))
                detalle_comp = json.loads(request.POST.get('detalle_comp', '[]'))
                if(ensamble.count()==0):
                    ensamblecomponente = EnsambleComponente.objects.create(
                        id_componentepadre=componente,
                        padrecantidad=cantidadpadre,
                        id_umpadre=UnidadMedida.objects.get(idum=request.POST.get('id_um'))
                    )
                    for detalle_data in detalle_comp:
                        componente_hijo = Componente.objects.get(id_componente=detalle_data['id'])
                        um = componente_hijo.id_um
                        detalleensamblecomponente = DetalleEnsambleComponente.objects.create(
                            id_ensamblec=ensamblecomponente,
                            id_componentehijo=componente_hijo,
                            cantidadhijo=detalle_data['cantidad'],
                            id_umhijo=um
                        )
                    componente.save()
                    return JsonResponse({'mensaje': 'Componente editado con éxito'})
                if(ensamble.count()>0):
                    detalles_actuales = DetalleEnsambleComponente.objects.filter(id_ensamblec=EnsambleComponente.objects.get(id_componentepadre=componente))           
                    i=0
                    for det in detalle_comp:
                        componente_hijo = Componente.objects.get(id_componente=det['id'])
                        um = componente_hijo.id_um
                        if i < len(detalles_actuales):
                            detalle_actual = detalles_actuales[i]
                            detalle_actual.id_componentehijo = componente_hijo
                            detalle_actual.cantidadhijo = det['cantidad']
                            detalle_actual.id_umhijo = um
                            detalle_actual.save()
                        else:
                            ensamble = EnsambleComponente.objects.get(id_componentepadre=componente)
                            DetalleEnsambleComponente.objects.create(
                                id_ensamblec=ensamble,
                                id_componentehijo=componente_hijo,
                                cantidadhijo=det['cantidad'],
                                id_umhijo=um
                            )
                        i = i + 1
                    while(i<len(detalles_actuales)):
                        detalle_actual = detalles_actuales[i]
                        detalle_actual.delete()
                        i=i+1
            componente.save()
            return JsonResponse({'mensaje': 'Se edito correctamente'})
        except Componente.DoesNotExist:
            return JsonResponse({'error': 'Componente no encontrado'}, status=404)
        except UnidadMedida.DoesNotExist:
            return JsonResponse({'error': 'Unidad de medida no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ListarProductos(View):
    def get(self, request, *args, **kwargs):
        try:
            # Parámetros de paginación y búsqueda
            page = int(request.GET.get('page',1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')

            # Filtrar productos por término de búsqueda
            productos = Producto.objects.filter(nombreproducto__icontains=search)

            # Configurar la paginación
            paginator = Paginator(productos, size)

            try:
                # Obtener la página actual
                productos_pagina = paginator.page(page)
            except EmptyPage:
                # Si la página está fuera de rango, devolver una lista vacía
                productos_pagina = []

            # Convertir productos a formato JSON
            lista_productos = []
            lista_horario = []
            for producto in productos_pagina:
                imagen_base64 = None
                if producto.imagenp:
                    try:
                        byteImg = base64.b64decode(producto.imagenp)
                        imagen_base64 = base64.b64encode(byteImg).decode('utf-8')
                    except Exception as img_error:
                        print(f"Error al procesar imagen: {str(img_error)}")
                horariosz = HorarioProducto.objects.filter(id_producto=producto.id_producto)
                for horarioss in horariosz:
                    datos_horario = {
                        'id_horarioproducto': horarioss.id_horarioproducto,
                        'id_horarios': horarioss.id_horarios.id_horarios,  # Cambiado para obtener el campo deseado
                        'id_sucursal': horarioss.id_sucursal.id_sucursal,
                    }
                    lista_horario.append(datos_horario)
                ensambleexi = EnsambleProducto.objects.filter(id_producto=producto)
                if (ensambleexi.exists()):
                    ensamble=EnsambleProducto.objects.get(id_producto=producto)
                    detallesensamble=DetalleEnsambleProducto.objects.filter(id_emsamblep=ensamble)
                    lista_detalle = []
                    for detalle in detallesensamble:
                        hijo={
                            'id':detalle.id_componentehijo.id_componente,
                            'nombre':detalle.id_componentehijo.nombre
                        }
                        um={
                            'id':detalle.id_umhijo.idum,
                            'nombre':detalle.id_umhijo.nombreum
                        }
                        ensamble_data = {
                            'id_componentehijo':hijo,
                            'cantidadhijo': detalle.cantidadhijo,
                            'um':um
                        }
                        lista_detalle.append(ensamble_data)
                    compdata={
                        'padrecant':ensamble.padrecantidad,
                        'detalle':lista_detalle
                    }
                    datos_producto = {
                        'id_producto': producto.id_producto,
                        'id_categoria': producto.id_categoria.id_categoria,
                        'id_um': producto.id_um.idum,
                        'puntosp': producto.puntosp,
                        'codprincipal': producto.codprincipal,
                        'nombreproducto': producto.nombreproducto,
                        'descripcionproducto': producto.descripcionproducto,
                        'preciounitario': str(producto.preciounitario),
                        'iva': producto.iva,
                        'ice': producto.ice,
                        'irbpnr': producto.irbpnr,
                        'horarios': lista_horario,
                        'imagenp': imagen_base64,
                        'detalle':compdata,
                    }
                    lista_horario = []
                    lista_productos.append(datos_producto)
                else:
                    datos_producto = {
                        'id_producto': producto.id_producto,
                        'id_categoria': producto.id_categoria.id_categoria,
                        'id_um': producto.id_um.idum,
                        'puntosp': producto.puntosp,
                        'codprincipal': producto.codprincipal,
                        'nombreproducto': producto.nombreproducto,
                        'descripcionproducto': producto.descripcionproducto,
                        'preciounitario': str(producto.preciounitario),
                        'iva': producto.iva,
                        'ice': producto.ice,
                        'irbpnr': producto.irbpnr,
                        'horarios': lista_horario,
                        'imagenp': imagen_base64,
                    }
                    lista_horario = []
                    lista_productos.append(datos_producto)
            return JsonResponse({'productos': lista_productos, 'total': paginator.count}, safe=False)

        except Exception as e:
            # Manejar errores aquí
            return JsonResponse({'error': str(e)}, status=500)
def obtener_siguiente_codprincipal():
    max_cod_producto = Producto.objects.aggregate(max_cod=Max(ExpressionWrapper(F('codprincipal'), output_field=IntegerField())))

    # Obtener el CodPrincipal más alto de Combo
    max_cod_combo = Combo.objects.aggregate(max_cod=Max(ExpressionWrapper(F('codprincipal'), output_field=IntegerField())))

    # Obtener el máximo entre los dos y calcular el siguiente número
    ultimo_numero = max(int(max_cod_producto['max_cod'] or 0), int(max_cod_combo['max_cod'] or 0))
    siguiente_numero = ultimo_numero + 1

    # Formatear el siguiente número como CodPrincipal
    siguiente_codprincipal = f'{siguiente_numero:025d}'

    return siguiente_codprincipal
@method_decorator(csrf_exempt, name='dispatch')
class CrearEnsambleUnidadMedida(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            idump = request.POST.get('idump')
            idumc = request.POST.get('idumc')
            cantidadconversion = request.POST.get('cantidadconversion')
            if Decimal(cantidadconversion) != 0:
                cantidadconversioninv = 1 / Decimal(cantidadconversion)
                print(cantidadconversioninv)
            else:
                print('Dividio por cero xd')
                return JsonResponse({'error': 'Dividir por cero'}, status=400)
            unidapadre=UnidadMedida.objects.get(idum=idump)
            unidahijo=UnidadMedida.objects.get(idum=idumc)
            ensamble_existente = EnsambleUnidadMedida.objects.filter(idump=unidapadre, idumc=unidahijo).first()
            if ensamble_existente:
                ensamble_existente.cantidadconversion = cantidadconversion
                ensamble_existente.save()
            else:
                unidad_medida_padre = UnidadMedida.objects.get(idum=idump)
                unidad_medida_hijo = UnidadMedida.objects.get(idum=idumc)
                EnsambleUnidadMedida.objects.create(
                    idump=unidad_medida_padre,
                    idumc=unidad_medida_hijo,
                    cantidadconversion=cantidadconversion
                )
            inverso_existente = EnsambleUnidadMedida.objects.filter(idump=unidahijo, idumc=unidapadre).first()
            if inverso_existente:
                inverso_existente.cantidadconversion = cantidadconversioninv
                inverso_existente.save()
            else:
                unidad_medida_padre = UnidadMedida.objects.get(idum=idump)
                unidad_medida_hijo = UnidadMedida.objects.get(idum=idumc)
                EnsambleUnidadMedida.objects.create(
                    idump=unidad_medida_hijo,
                    idumc=unidad_medida_padre,
                    cantidadconversion=cantidadconversioninv
                )


            return JsonResponse({'mensaje': 'Ensamble de unidad de medida creado o actualizado con éxito'})

        except UnidadMedida.DoesNotExist as e:
            return JsonResponse({'error': 'Una o ambas unidades de medida no existen'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
class ListaConversiones(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las conversiones
            conversiones = EnsambleUnidadMedida.objects.all()

            # Crear una lista para almacenar los resultados
            lista_conversiones = []

            # Iterar sobre cada ensamble de unidad de medida
            for conversion in conversiones:
                # Obtener los detalles de la unidad de medida padre
                unidad_padre = UnidadMedida.objects.get(idum=conversion.idump_id)
                nombre_unidad_padre = unidad_padre.nombreum

                # Obtener los detalles de la unidad de medida hijo
                unidad_hijo = UnidadMedida.objects.get(idum=conversion.idumc_id)
                nombre_unidad_hijo = unidad_hijo.nombreum

                # Crear un diccionario con los detalles de la conversión
                detalle_conversion = {
                    'id_conversion': conversion.ideum,
                    'unidad_padre': {
                        'id_um': conversion.idump_id,
                        'nombre_um': nombre_unidad_padre,
                    },
                    'unidad_hijo': {
                        'id_um': conversion.idumc_id,
                        'nombre_um': nombre_unidad_hijo,
                    },
                    'cantidad_conversion': conversion.cantidadconversion,
                }

                # Agregar el diccionario a la lista de conversiones
                lista_conversiones.append(detalle_conversion)

            return JsonResponse({'conversiones': lista_conversiones})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)