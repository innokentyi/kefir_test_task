from drf_yasg import openapi

LoginModel = openapi.Schema(
    title="LoginModel",
    required=["login", "password"],
    type=openapi.TYPE_OBJECT,
    properties={'login': openapi.Schema(title='login', type=openapi.TYPE_STRING),
                'password': openapi.Schema(title='password', type=openapi.TYPE_STRING)}
)

ErrorResponseModel = openapi.Schema(
    title="ErrorResponseModel",
    required=["code", "message"],
    type=openapi.TYPE_OBJECT,
    properties={"code": openapi.Schema(title='Code', type=openapi.TYPE_INTEGER),
                "message": openapi.Schema(title='Message', type=openapi.TYPE_STRING)},
)

ValidationError = openapi.Schema(
    title="ValidationError",
    required=["loc", "msg", "type"],
    type=openapi.TYPE_OBJECT,
    properties={"loc": openapi.Schema(title="Location", type=openapi.TYPE_ARRAY, items=openapi.TYPE_STRING),
                "msg": openapi.Schema(title="Message", type=openapi.TYPE_STRING),
                "type": openapi.Schema(title="Error Type", type=openapi.TYPE_STRING)}
)

HTTPValidationError = openapi.Schema(
    title="HTTPValidationError",
    type=openapi.TYPE_OBJECT,
    properties={'detail': openapi.Schema(title="Detail", type=openapi.TYPE_ARRAY, items=ValidationError)}
)

CurrentUserResponseModel = openapi.Schema(
    title="CurrentUserResponseModel",
    required=["first_name", "last_name", "other_name", "email", "phone", "birthday", "is_admin"],
    type=openapi.TYPE_OBJECT,
    properties={"first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "is_admin": openapi.Schema(title="Is Admin", type=openapi.TYPE_BOOLEAN)}
)

PrivateCreateUserModel = openapi.Schema(
    title="PrivateCreateUserModel",
    required=["first_name", "last_name", "email", "is_admin", "password"],
    type=openapi.TYPE_OBJECT,
    properties={"first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "is_admin": openapi.Schema(title="Is Admin", type=openapi.TYPE_BOOLEAN),
                "city": openapi.Schema(title="City", type=openapi.TYPE_INTEGER),
                "additional_info": openapi.Schema(title="Additional Info", type=openapi.TYPE_STRING),
                "password": openapi.Schema(title="Password", type=openapi.TYPE_STRING),
                },
)

PrivateDetailUserResponseModel = openapi.Schema(
    title="PrivateDetailUserResponseModel",
    required=["id", "first_name", "last_name", "other_name", "email", "phone", "birthday", "city", "additional_info",
              "is_admin"],
    type=openapi.TYPE_OBJECT,
    properties={"first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "is_admin": openapi.Schema(title="Is Admin", type=openapi.TYPE_BOOLEAN),
                "city": openapi.Schema(title="City", type=openapi.TYPE_INTEGER),
                "additional_info": openapi.Schema(title="Additional Info", type=openapi.TYPE_STRING),
                "id": openapi.Schema(title="id", type=openapi.TYPE_INTEGER),
                }
)

UsersListElementModel = openapi.Schema(
    title="UsersListElementModel",
    required=["id", "first_name", "last_name", "email"],
    type=openapi.TYPE_OBJECT,
    properties={"id": openapi.Schema(title="Id", type=openapi.TYPE_INTEGER),
                "first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING)}
)

PaginatedMetaDataModel = openapi.Schema(
    title="PaginatedMetaDataModel",
    required=["total", "page", "size"],
    type=openapi.TYPE_OBJECT,
    properties={"total": openapi.Schema(title='Total', type=openapi.TYPE_INTEGER),
                "page": openapi.Schema(title='Page', type=openapi.TYPE_INTEGER),
                "size": openapi.Schema(title='Size', type=openapi.TYPE_INTEGER)}
)

CitiesHintModel = openapi.Schema(
    title="CitiesHintModel",
    required=["id", "name"],
    type=openapi.TYPE_OBJECT,
    properties={"id": openapi.Schema(title='Id', type=openapi.TYPE_INTEGER),
                "name": openapi.Schema(title='Name', type=openapi.TYPE_STRING)}
)

PrivateUsersListHintMetaModel = openapi.Schema(
    title="PrivateUsersListHintMetaModel",
    required=["city"],
    type=openapi.TYPE_OBJECT,
    properties={"city": openapi.Schema(title='City', type=openapi.TYPE_ARRAY, items=CitiesHintModel)}
)

PrivateUsersListMetaDataModel = openapi.Schema(
    title="PrivateUsersListMetaDataModel",
    required=["pagination", "hint"],
    type=openapi.TYPE_OBJECT,
    properties={"pagination": PaginatedMetaDataModel, "hint": PrivateUsersListHintMetaModel}
)

PrivateUsersListResponseModel = openapi.Schema(
    title='PrivateUsersListResponseModel',
    required=["data", "meta"],
    type=openapi.TYPE_OBJECT,
    properties={"data": openapi.Schema(title='Data', type=openapi.TYPE_ARRAY, items=UsersListElementModel),
                "meta": PrivateUsersListMetaDataModel}
)

PrivateUpdateUserModel = openapi.Schema(
    title="PrivateUpdateUserModel",
    required=["id"],
    type=openapi.TYPE_OBJECT,
    properties={"id": openapi.Schema(title='Id', type=openapi.TYPE_INTEGER),
                "first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "is_admin": openapi.Schema(title="Is Admin", type=openapi.TYPE_BOOLEAN),
                "city": openapi.Schema(title="City", type=openapi.TYPE_INTEGER),
                "additional_info": openapi.Schema(title="Additional Info", type=openapi.TYPE_STRING)}
)

UsersListMetaDataModel = openapi.Schema(
    title="UsersListMetaDataModel",
    required=["pagination"],
    type=openapi.TYPE_OBJECT,
    properties={"pagination": PaginatedMetaDataModel}
)

UsersListResponseModel = openapi.Schema(
    title="UsersListResponseModel",
    required=["data", "meta"],
    type=openapi.TYPE_OBJECT,
    properties={"data": openapi.Schema(title='Data', type=openapi.TYPE_ARRAY, items=UsersListElementModel),
                "meta": UsersListMetaDataModel}
)

UpdateUserModel = openapi.Schema(
    title="UpdateUserModel",
    type=openapi.TYPE_OBJECT,
    properties={"first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)}
)

UpdateUserResponseModel = openapi.Schema(
    title="UpdateUserResponseModel",
    required=["id", "first_name", "last_name", "other_name", "email", "phone", "birthday"],
    type=openapi.TYPE_OBJECT,
    properties={"id": openapi.Schema(title='Id', type=openapi.TYPE_INTEGER),
                "first_name": openapi.Schema(title="First Name", type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING),
                "other_name": openapi.Schema(title="Other Name", type=openapi.TYPE_STRING),
                "email": openapi.Schema(title="Email", type=openapi.TYPE_STRING),
                "phone": openapi.Schema(title="Phone", type=openapi.TYPE_STRING),
                "birthday": openapi.Schema(title="Last Name", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)}
)
