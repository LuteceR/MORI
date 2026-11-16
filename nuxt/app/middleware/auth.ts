export default defineNuxtRouteMiddleware(async () => {
    const auth = useAuthStore();
    const isCookie = useCookie('access_token');
    
    if(!isCookie.value) {
        return navigateTo('/auth')
    }

    await auth.fetchUser()
})