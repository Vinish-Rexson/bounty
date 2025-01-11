class NextParameterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        next_param = request.GET.get('next')
        if next_param:
            request.session['next'] = next_param
        return self.get_response(request) 