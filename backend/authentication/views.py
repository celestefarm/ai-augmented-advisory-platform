# authentication/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import logging
from decouple import config

from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer,
    GoogleAuthSerializer,
    VerifyEmailSerializer,
    UserUpdateSerializer
)
from .models import User

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    """
    User Registration Endpoint
    POST /api/auth/register
    
    Creates new user account with email and password.
    Sends verification email.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Algorithm:
        1. Validate input data (email format, password length)
        2. Check if email already exists
        3. Hash password using bcrypt
        4. Create user record (inactive until email verified)
        5. Send verification email
        6. Return success message (no tokens until verified)
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            # Validate input
            if not serializer.is_valid():
                logger.warning(f"Registration validation failed: {serializer.errors}")
                return Response(
                    {
                        'message': 'Validation failed',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use transaction for data consistency
            with transaction.atomic():
                # Extract validated data
                validated_data = serializer.validated_data
                email = validated_data.pop('email')
                password = validated_data.pop('password')
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    logger.info(f"Registration attempt with existing email: {email}")
                    return Response(
                        {
                            'message': 'User with this email already exists'
                        },
                        status=status.HTTP_409_CONFLICT
                    )

                # Create user (inactive until email verified)
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    is_active=False,  # Inactive until email verified
                    email_verified=False,
                    auth_provider='email',
                    **validated_data
                )
                
                logger.info(f"New user registered: {user.email} (ID: {user.id})")

                # Send verification email
                try:
                    user.send_verification_email()
                    logger.info(f"Verification email sent to {user.email}")
                except Exception as email_error:
                    logger.error(f"Failed to send verification email: {str(email_error)}")
                    # Don't fail registration if email fails
                    # User can resend verification email later

            return Response(
                {
                    'message': 'Registration successful. Please check your email to verify your account.',
                    'email': user.email,
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Registration failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailAPIView(APIView):
    """
    Email Verification Endpoint
    POST /api/auth/verify-email
    
    Verifies user email using token from email link.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Algorithm:
        1. Extract token from request
        2. Decode and validate JWT token
        3. Get user from token
        4. Mark email as verified
        5. Activate account
        6. Generate new tokens for login
        7. Send welcome email
        """
        try:
            serializer = VerifyEmailSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        'message': 'Invalid verification data',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = serializer.validated_data['token']
            
            try:
                # Decode token
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Get user
                user = User.objects.get(id=user_id)
                
                # Check if already verified
                if user.email_verified:
                    return Response(
                        {
                            'message': 'Email already verified'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Verify email and activate account
                user.email_verified = True
                user.is_active = True
                user.save(update_fields=['email_verified', 'is_active'])
                
                logger.info(f"Email verified for user: {user.email}")
                
                # Generate new tokens for login
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # Send welcome email
                try:
                    from django.core.mail import send_mail
                    from django.template.loader import render_to_string
                    
                    html_message = render_to_string('emails/welcome.html', {
                        'user': user,
                        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
                    })
                    
                    send_mail(
                        subject='Welcome to AI-Augmented!',
                        message='',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send welcome email: {str(e)}")
                
                return Response(
                    {
                        'message': 'Email verified successfully',
                        'user': UserSerializer(user).data,
                        'access_token': access_token,
                        'refresh_token': str(refresh),
                    },
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                return Response(
                    {
                        'message': 'Invalid verification token'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Token validation error: {str(e)}")
                return Response(
                    {
                        'message': 'Invalid or expired verification token'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Email verification error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Email verification failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResendVerificationEmailAPIView(APIView):
    """
    Resend Verification Email Endpoint
    POST /api/auth/resend-verification
    
    Resends verification email to unverified user.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            
            if not email:
                return Response(
                    {'message': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(email=email)
                
                if user.email_verified:
                    return Response(
                        {'message': 'Email already verified'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Send verification email
                user.send_verification_email()
                logger.info(f"Verification email resent to {user.email}")
                
                return Response(
                    {'message': 'Verification email sent. Please check your inbox.'},
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                logger.warning(f"Resend verification attempt for non-existent email: {email}")
                return Response(
                    {'message': 'If this email is registered, a verification link will be sent.'},
                    status=status.HTTP_200_OK
                )
        
        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}", exc_info=True)
            return Response(
                {'message': 'An error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginAPIView(APIView):
    """
    User Login Endpoint
    POST /api/auth/login
    
    Authenticates user with email and password.
    Returns JWT tokens on success.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Algorithm:
        1. Extract email and password from request
        2. Query user by email
        3. Check if email is verified
        4. If not found: Return 401 (generic message for security)
        5. If found: Compare password hash using bcrypt
        6. If match: Generate JWT, update last_login, return tokens
        7. If mismatch: Return 401 (generic message)
        """
        try:
            serializer = LoginSerializer(data=request.data)
            
            # Validate input
            if not serializer.is_valid():
                logger.warning(f"Login validation failed: {serializer.errors}")
                return Response(
                    {
                        'message': 'Validation failed',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                # Query user by email
                user = User.objects.get(email=email)
                
                # Check if email is verified
                if not user.email_verified:
                    logger.warning(f"Login attempt with unverified email: {email}")
                    return Response(
                        {
                            'message': 'Please verify your email address before logging in.',
                            'email_verified': False
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Check if account is active
                if not user.is_active:
                    logger.warning(f"Login attempt for inactive account: {email}")
                    return Response(
                        {
                            'message': 'Account is inactive. Please contact support.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Verify password
                if not user.check_password(password):
                    logger.warning(f"Failed login attempt for {email}: Invalid password")
                    # Generic message for security (don't reveal which part failed)
                    return Response(
                        {
                            'message': 'Invalid email or password'
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Update last login timestamp
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                logger.info(f"Successful login: {user.email}")

                return Response(
                    {
                        'message': 'Login successful',
                        'user': UserSerializer(user).data,
                        'access_token': access_token,
                        'refresh_token': str(refresh),
                    },
                    status=status.HTTP_200_OK
                )

            except User.DoesNotExist:
                logger.warning(f"Login attempt with non-existent email: {email}")
                # Generic message for security (don't reveal email doesn't exist)
                return Response(
                    {
                        'message': 'Invalid email or password'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Login failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleAuthAPIView(APIView):
    """
    Google OAuth Login Endpoint
    POST /api/auth/google
    
    Authenticates user with Google OAuth token.
    Creates account if doesn't exist.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Algorithm:
        1. Extract Google ID token from request
        2. Verify token with Google
        3. Extract user info (email, name, picture)
        4. Check if user exists by email
        5. If exists: Login
        6. If not: Create new user (auto-verified, auto-activated)
        7. Generate JWT tokens
        8. Return user data and tokens
        """
        try:
            serializer = GoogleAuthSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        'message': 'Invalid Google token',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            id_token = serializer.validated_data['id_token']
            
            try:
                # Verify Google token
                from google.oauth2 import id_token as google_id_token
                from google.auth.transport import requests as google_requests
                
                idinfo = google_id_token.verify_oauth2_token(
                    id_token,
                    google_requests.Request(),
                    config('GOOGLE_CLIENT_ID')
                )
                
                # Extract user info
                email = idinfo.get('email')
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                picture = idinfo.get('picture', '')
                
                if not email:
                    return Response(
                        {'message': 'Email not provided by Google'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if user exists
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'is_active': True,
                        'email_verified': True,
                        'auth_provider': 'google',
                    }
                )
                
                if created:
                    logger.info(f"New user created via Google OAuth: {email}")
                    
                    # Send welcome email
                    try:
                        from django.core.mail import send_mail
                        from django.template.loader import render_to_string
                        
                        html_message = render_to_string('emails/welcome.html', {
                            'user': user,
                            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
                        })
                        
                        send_mail(
                            subject='Welcome to AI-Augmented!',
                            message='',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            html_message=html_message,
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send welcome email: {str(e)}")
                else:
                    logger.info(f"Existing user logged in via Google OAuth: {email}")
                    
                    # Update last login
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                return Response(
                    {
                        'message': 'Login successful' if not created else 'Account created successfully',
                        'user': UserSerializer(user).data,
                        'access_token': access_token,
                        'refresh_token': str(refresh),
                        'is_new_user': created,
                    },
                    status=status.HTTP_200_OK
                )
                
            except ValueError as e:
                logger.error(f"Invalid Google token: {str(e)}")
                return Response(
                    {'message': 'Invalid Google token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            logger.error(f"Google OAuth error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Google authentication failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyTokenAPIView(APIView):
    """
    Token Verification Endpoint
    GET /api/auth/verify
    
    Verifies JWT token validity and returns user data.
    Requires valid JWT in Authorization header.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            
            # Check if account is active and email verified
            if not user.is_active or not user.email_verified:
                logger.warning(f"Token verification failed: User {user.email} is inactive or unverified")
                return Response(
                    {
                        'message': 'Account is inactive or email not verified'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            logger.info(f"Token verified for user: {user.email}")

            return Response(
                {
                    'message': 'Token is valid',
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Token verification error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Token verification failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutAPIView(APIView):
    """
    Logout Endpoint
    POST /api/auth/logout
    
    Blacklists refresh token to prevent reuse.
    Requires valid JWT in Authorization header.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Algorithm:
        1. Extract refresh token from request body
        2. Blacklist the refresh token
        3. Return success message
        """
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {
                        'message': 'Refresh token is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User logged out: {request.user.email}")

            return Response(
                {
                    'message': 'Logout successful'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Logout failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckAPIView(APIView):
    """
    Health Check Endpoint
    GET /api/health
    
    Returns API health status.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                'status': 'healthy',
                'message': 'AI-Augmented API is running',
                'timestamp': timezone.now().isoformat()
            },
            status=status.HTTP_200_OK
        )
    
class UpdateProfileAPIView(APIView):
    """
    Update User Profile Endpoint
    PUT /api/auth/profile
    PATCH /api/auth/profile
    
    Updates user profile information
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self._update_profile(request, partial=False)

    def patch(self, request, *args, **kwargs):
        return self._update_profile(request, partial=True)

    def _update_profile(self, request, partial=False):
        try:
            user = request.user
            serializer = UserUpdateSerializer(
                user,
                data=request.data,
                partial=partial
            )

            if not serializer.is_valid():
                return Response(
                    {
                        'message': 'Validation failed',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            logger.info(f"Profile updated for user: {user.email}")

            return Response(
                {
                    'message': 'Profile updated successfully',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Profile update error: {str(e)}", exc_info=True)
            return Response(
                {
                    'message': 'Profile update failed',
                    'error': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetFormChoicesAPIView(APIView):
    """
    Get Form Choices Endpoint
    GET /api/auth/form-choices
    
    Returns available choices for industries and regions
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            return Response(
                {
                    'industries': [
                        {'value': choice[0], 'label': choice[1]}
                        for choice in User.INDUSTRIES
                    ],
                    'regions': [
                        {'value': choice[0], 'label': choice[1]}
                        for choice in User.REGIONS
                    ]
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error fetching form choices: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch form choices'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )