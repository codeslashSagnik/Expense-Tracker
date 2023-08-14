from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.views import View
from validate_email import validate_email 
from django.contrib import messages
import re
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth

class UsernameValidateView(View):
    def post(self,request):
        data=json.loads(request.body)
        username=data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username can only be submitted using alpha-numeric values '}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'username is already in use , please choose some other username '}, status=400)
        return JsonResponse({'username_valid':True})
    
class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')
    
    def post(self,request):
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        
        context={
            'fieldValues':request.POST
        }
        
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,"Password too short")
                    return render(request,'authentication/register.html',context)
                elif not re.search("[A-Z]", password):  # Check for uppercase letter
                    messages.error(request, "Password should have at least one uppercase letter.")
                    return render(request,'authentication/register.html',context)
                elif not re.search("[!@#$%^&*(),.?\":{}|<>]", password):  # Check for special character
                    messages.error(request, "Password should have at least one special character.")
                    return render(request,'authentication/register.html',context)
                user=User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()
                #path_to_view
                # -getting we are on
                # -relative url verification
                #encode uid
                #token
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link
                email_subject='Actiavte your account'
                email_body='Test body'
                email=EmailMessage[
                    email_subject,
                    email_body,
                    'noreply@semycolon.com',
                    [email],
                ]
                messages.success(request,"Account created successfully")
                
        return render(request,'authentication/register.html')
class EmailValidateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not provided'}, status=400)

            if not validate_email(email):
                return JsonResponse({'email_error': 'Email is invalid'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error': 'Email is already in use'}, status=400)

            return JsonResponse({'email_valid': True})

        except Exception as e:
            # This will return any exception that arises in the view, helping you pinpoint the exact issue.
            return JsonResponse({'error': str(e)}, status=500)
        
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')