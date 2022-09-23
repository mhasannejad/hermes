from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(request.user.role.title + '_home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_user_by_role(allowed_role):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            if request.user.role.title == allowed_role or request.user.role.title == 'admin':
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')

        return wrapper_func

    return decorator


def professor_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None

        if request.user.mode != 2:
            return HttpResponse('UnAuthorized', status=401)
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_function
