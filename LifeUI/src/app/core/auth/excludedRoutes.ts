//
// Routes to be excluded from authentication
// These routes will not have the token added to the header by the interceptor
//
export const excludedRoutes = [
    '/auth/login/',
    '/auth/register/',
    '/auth/logout/',
    '/auth/login/refresh/'
];