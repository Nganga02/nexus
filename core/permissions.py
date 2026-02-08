from rest_framework.permissions import BasePermission, SAFE_METHODS

def is_authenticated(user):
    return user is not None and user.is_authenticated


def has_role(user, *roles):
    return is_authenticated(user) and user.role in roles


def is_admin(user):
    return has_role(user, 'admin')


def is_host(user):
    return has_role(user, 'host')


def is_guest(user):
    return has_role(user, 'guest')


# for user deletion/update (admin/self only)
class UsersPermission(BasePermission):
    """
    We have the following permissions for the user operation

    - Only admins can view users
    - Admins or the user themselves can retrieve/update/delete instance of user
    - Admin or anyone can create a user(registration)

    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        elif view.action in ['list']:
            return is_admin(request.user)
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return is_authenticated(request.user)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return is_admin(request.user) or obj == request.user
        

# for property creation/update/deletion (admin/host only)
class PropertyPermissions(BasePermission):
    """
    We have the following permissions for the property operation

    - Only admins and hosts can create properties
    - Only admins and the host who owns the property can update/delete it
    - Anyone can view properties

    """
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        
        if view.action not in ['list', 'retrieve']:
            return is_admin(request.user) or is_host(request.user)

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return request.user.role == 'host' and obj.owner == request.user

# for booking creation (guest only)
class BookingPermissions(BasePermission):
    """
    We have the following permissions for the booking operation
    - Only guests or hosts who dont't own the property can create bookings
    - Only admins, the host who owns the property or the guests in the booking
    can view it's details
    - Only guests in the booking can update/cancel a pending booking
    """
    def has_permission(self, request, view):
        if is_admin(request.user):
            return True
        
        elif view.action in ['list', 'retrieve', 'create']:
            return is_guest(request.user) or is_host(request.user) 
        elif view.action in ['update', 'partial_update', 'destroy']:
            return is_guest(request.user) or is_host(request.user)
        else:
            return False

    def has_object_permission(self, request, view, obj):
            return is_guest(request.user) and request.user in obj.guests.all() and obj.status == 'pending'
   
# for payment creation (guest only)
class IsGuestForPayment(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return is_guest(request.user)
        elif view.action in ['list', 'retrieve']:
            return True
        else:
            return False
    def has_object_permission(self, request, view, obj):
        return is_guest(request.user)
