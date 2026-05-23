export default defineNuxtRouteMiddleware(async () => {
    const auth = useAuthStore();
    const isCookie = useCookie('access_token');
    
    if(!isCookie.value) {
        return navigateTo('/auth', { redirectCode: 301 })
    } else {
        auth.fetchUser();
    }
})