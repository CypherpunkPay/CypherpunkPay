from cypherpunkpay.web.views.base_view import BaseView


class AdminBaseView(BaseView):

    def __init__(self, request):
        super().__init__(request)
        self.logged_in = request.authenticated_userid
