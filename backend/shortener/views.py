import io
import qrcode

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Click, ShortURL
from .serializers import ShortURLDetailSerializer, ShortURLSerializer
from .utils import gen_short_code

MAX_COLLISION_RETRIES = 10

EXPIRED_HTML = """
<!DOCTYPE_HTML>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Link Expired</title>
</head>
<body>
    <h2>THis link has expired</h2>
</body>
</html>
"""
#this html i put in the server side
#since non-expired links are redirected from the server itself by HttpResponseRedirect(), the expired status html 
#is also served from the server (i could just send a Response then parse it and then do it from the frontend)

class ShortURLListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        #list all the urls created by the current logged in user
        urls = ShortURL.objects.filter(owner=request.user)
        serializer = ShortURLSerializer(urls, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        #create a new short url for the logged in user
        serializer = ShortURLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        custom_code = (serializer.validated_data.pop("custom_code", "") or "").strip()
        expires_at  = serializer.validated_data.pop("expires_at", None)

        if custom_code:
            code = custom_code
            is_custom = True
        else:
            #gen a unique short code
            for _ in range(MAX_COLLISION_RETRIES):
                code = gen_short_code()
                if not ShortURL.objects.filter(short_code=code).exists():
                    break
            else:
                return Response({"Error": "Could not generate a unique short code. Please try again. "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            is_custom = False
        
        kwargs = {"owner": request.user, "short_code": code, "is_custom": is_custom}
        if expires_at is not None: #only pass if the user provided one else, the model will default to 10 days, in the front end i think empty is 10 days as well
            kwargs["expires_at"] = expires_at

        short_url = serializer.save(**kwargs)
        return Response(ShortURLSerializer(short_url).data, status=status.HTTP_201_CREATED)
    

class ShortURLDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_owned(self, request, pk):
        return get_object_or_404(ShortURL, pk=pk, owner=request.user)
    
    def get(self, request, pk):
        #a single short url details, click analysis
        short_url = self._get_owned(request, pk)
        serializer = ShortURLDetailSerializer(short_url)
        return Response(serializer.data) 
        #here error or exception handling is not done, because _get_owner will raise exception if not found

    def delete(self, request, pk):
        short_url = self._get_owned(request, pk)
        short_url.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RedirectView(APIView):
    #this is a public endpoint
    #resolves a short code, records a click, and returns the destination URL. 

    #making the short url is a protected endpoint
    #however, the resolution or the redirect endpoint is public

    #anyone can use for redirection
    #but for creating need to be logged in
    
    permission_classes = [AllowAny]

    def get(self, request, short_code):
        short_url = get_object_or_404(ShortURL, short_code=short_code)

        if short_url.is_expired:
            return HttpResponse(EXPIRED_HTML, status=410, content_type="text/html")

        Click.objects.create(short_url=short_url)
        return HttpResponseRedirect(short_url.og_url)


class QRCodeView(APIView):
    permission_classes = [IsAuthenticated] #only the owner can create the qr code

    def get(self, request, pk):
        short_url = get_object_or_404(ShortURL, pk=pk, owner=request.user)

        redirect_url = request.build_absolute_uri(f"/r/{short_url.short_code}")

        qr = qrcode.QRCode(
            version=None, #this will auto size
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(redirect_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")


        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        response = HttpResponse(buf, content_type="image/png")
        response["Content-Disposition"] = f'inline; filename="qr-{short_url.short_code}.png"'
        return response
