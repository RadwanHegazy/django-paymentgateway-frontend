from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic import TemplateView
from django.views import View
from globals.decorators import login_required
from globals.request_manager import Action
from frontend.settings import MAIN_URL
from django.contrib.messages import error, success

class ProfileView(TemplateView) : 
    template_name = 'profile.html'

    @login_required
    def get(self, request, **kwargs) : 

        amount = request.GET.get('amount',None)
        if amount :
            action = Action(
                url=MAIN_URL + "/payment/create/",
                headers=kwargs['headers'],
                data={
                    'amount' : amount
                }
            )

            action.post()
            
            success(request, action.json_data()['id'])
            return redirect('profile')
        
        action = Action(
            url=MAIN_URL + "/payment/get/",
            headers=kwargs['headers'],
        )

        action.get()
        
        context = {
            'payments' : action.json_data()
        }
        
        return render(request, self.template_name, context)

class LoginView (TemplateView): 
    template_name = 'login.html'

    def post(self, request) : 
        action = Action(url=MAIN_URL + "/users/auth/login/",data={
            **request.POST
        })

        action.post()
        if action.is_valid:
            user = action.json_data()['access_token']
            response = redirect('profile')
            response.set_cookie('user', user)
            return response
        
        error(request,'invalid crediantils')
        return redirect('login')

class RegisterView (TemplateView) : 
    template_name = 'register.html'

    def post (self, request) : 
        action = Action(MAIN_URL + '/users/auth/register/', data={
            **request.POST
        })

        action.post()
        if action.is_valid :
            user = action.json_data()['access_token']
            response = redirect('profile')
            response.set_cookie('user', user)
            return response
        
        error(request, action.json_data()['message'][0])
        return redirect('register')

class LogoutView (View) : 
    
    def get (self, request) : 
        response = redirect('login')
        response.delete_cookie('user')
        return response
    
class PaymentPage (View) :

    def get(self, request, payment_id) : 

        action = Action(
            url=MAIN_URL + f"/payment/get/{payment_id}/"
        ) 
        action.get()

        if not action.is_valid:
            raise Http404(request)

        context = {
            'amount' : action.json_data()['amount']
        }

        return render(request, 'payment.html', context)


    def post(self, request, payment_id) : 
        action = Action(
            url=MAIN_URL + f"/payment/create/{payment_id}/",
            data={
                **request.POST
            }
        ) 
        action.post()

        if not action.is_valid:
            error(request, action.json_data()['message'][0])
        else:
            success(request,"تم اتمام العملية بنجاح")
        return redirect('payment', payment_id)

