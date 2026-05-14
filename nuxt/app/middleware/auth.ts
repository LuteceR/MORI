// export default defineNuxtRouteMiddleware((to, from) => {
//     // Replace this with your actual auth check (e.g., pinia, useUserSession)
//     const { loggedIn } = userses() 

//     // If user is not logged in and trying to access a protected page
//     if (!loggedIn.value && to.path !== '/auth') {
//     return navigateTo('/auth')
//     }
// })