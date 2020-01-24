from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView

from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView, ListView, CreateView
from django.http import HttpResponseRedirect

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q, Max, Min
from tienda.productos.models import Producto, Comentario

User = get_user_model()


class Indice(TemplateView):
    template_name = 'index.html'


class ListadoProducto(ListView):
    template_name = 'listado_productos.html'
    model = Producto
    paginate_by = 10

    def get_queryset(self):
        query = None

        if ('nombre' in self.request.GET) and self.request.GET['nombre'] != "":
            query = Q(nombre=self.request.GET["nombre"])

        if ('maximo' in self.request.GET) and self.request.GET['maximo'] != "":
            try:
                if query == None:
                    #lte mensor o igual a un numero
                    query = Q(precio__lte=int(float(self.request.GET['maximo'])))
                else:
                    query = query & Q(precio__lte=int(float(self.request.GET['maximo'])))
            except:
                pass


        if ('minimo' in self.request.GET) and self.request.GET['minimo'] != "":
            try:
                if query == None:
                    #gte mayor o igual que un numero
                    query = Q(precio__gte=int(float(self.request.GET['minimo'])))
                else:
                    query = query & Q(precio__gte=int(float(self.request.GET['minimo'])))
            except:
                pass


        if query is not None:
            productos = Producto.objects.filter(query)
        else:
            productos = Producto.objects.all()
        return productos

    #enviamos al template informacion que requerimos
    def get_context_data(self, **kwargs):
        context = super(ListadoProducto, self).get_context_data(**kwargs)
        context['maximo'] = Producto.objects.all().aggregate(Max('precio'))['precio__max']
        context['minimo'] = Producto.objects.all().aggregate(Min('precio'))['precio__min']
        return context


class DetalleProducto(DetailView):
    template_name = 'detalle.html'
    model = Producto


class ComentarioProducto(CreateView):
    template_name = 'detalle.html'
    model = Comentario
    fields = ('comentario','usuario','producto',)

    #confirmar si todo esta bien para dar url
    def get_success_url(self):
        return "/detalle_producto/{}/".format(self.object.producto.pk)


class Salir(LogoutView):
	next_page = reverse_lazy('indice')


class Ingresar(LoginView):
	template_name = 'login.html'

    # Si el logueo es correcto redirecciona al inicio si no no
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return HttpResponseRedirect(reverse('indice'))
		else:
			context = self.get_context_data(**kwargs)
			return self.render_to_response(context)

	def get_success_url(self):
		return reverse('indice')


class CambiarPerfil(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('telefono','last_name','first_name','email',)
    success_url = '/'
    template_name = 'perfil.html'

    #obtener objeto que queremos modificar
    def get_object(self, queryset=None):
        return self.request.user
